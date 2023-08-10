from flask import Flask, request, jsonify, g
import os
# from werkzeug.utils import secure_filename
import csv
import sqlite3
from sqlite3 import Error

#!usr/bin/python3
import os
from LsaChatbot import LsaChatbot

# SQLITE DATABASE
DATABASE = 'database_lsa.db'
stopword_path = os.getcwd() + '/stopword.txt'

lsaChatbot = LsaChatbot(stopword_path=stopword_path, db_path=DATABASE)

def get_lsa_response(input_text):
    lsa_response = lsaChatbot.lsa(input_text)
    return lsa_response
    
    file_path = os.getcwd() + '/fallback_sentences.txt'
    with open(file_path, 'a') as file:
        file.write(input_text + "\n")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def exec_db(query, args=(), one=False):
    try:
        db = get_db()
        if(one):
            data = db.execute(query,args)
        else :
            data = db.executemany(query, args)
        db.commit()
        db.close()
        return f"Total records affected:  {data.rowcount}"
    
    except Error as e:
        db.rollback()
        return f"Oops! Something went wrong. Error: {e}"
        


# FLASK
app = Flask(__name__)

# close SQLITE DB
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET'])
def health():
    return jsonify({
        'status' : 'active',
        'state' : 'running',
        'errors' : None
    })

@app.route('/lsa', methods=['GET'])
def lsa_get():
    query = request.args.get('query')
    payload = get_lsa_response(query)
    return jsonify(payload)

@app.route('/lsa', methods=['POST'])
def lsa_post():
    if not request.json:
        return jsonify({
            "message": "Bad request. Request has no body"
        }), 400
    else:
        payload = get_lsa_response(request.get_json()['query'])
        return jsonify(payload)

@app.route('/uploads', methods=['POST'])
def upload_dataset():
    if 'dataset' not in request.files:
        return jsonify({
            "message": "missing dataset" 
        }), 400

    file = request.files['dataset']

    # Mengecek apakah file memiliki ekstensi .csv
    if not file.filename.endswith('.csv'):
        return jsonify({
            "message": "file must be using csv format"
        }), 400
    
    # save temporary
    tmp_path = os.getcwd() + '/tmp_dataset.csv'
    file.save(tmp_path)
    
    # dataset baru
    new_dataset = []
    with open(tmp_path, 'r') as f:
        reader = csv.reader(f)
        next(reader, None) #skip header
        new_dataset = list(tuple(line) for line in reader)
    
    d = exec_db('INSERT INTO datasets(message,response) VALUES(?,?)',new_dataset)

    # remove tmp csv
    os.remove(tmp_path)

    return jsonify({
        "message": d
    })

@app.route('/train', methods=['GET'])
def train():
    lsaChatbot.train()
    return jsonify({
        "message": "dataset re-trained successfully"
    })

@app.route('/dataset', methods=['GET'])
def get_dataset():
    id = request.args.get('id')
    if(id):
        dataset = query_db('SELECT * FROM datasets WHERE id = ?', [id], one=True)
        if(dataset):
            return jsonify({
                'id'        : dataset[0],
                'message'   : dataset[1],
                'response'  : dataset[2],
                'created'   : dataset[3],
            })
        else:
            return jsonify({
                'message' : f'dataset with id {id} not found'
            }), 404
    else :
        dataset = query_db('SELECT * FROM datasets')
        if (dataset):
            dataset_dict = []
            for d in dataset:
                dataset_dict.append({
                    'id'        : d[0],
                    'message'   : d[1],
                    'response'  : d[2],
                    'created'   : d[3],
                })
            return jsonify({
                'result': {
                    'payload' : dataset_dict

                }
            })
        else:
            return jsonify({
                'message' : f'dataset not found'
            }), 500
        

@app.route('/dataset/add', methods=['POST'])
def add_dataset():
    if not request.json:
        return jsonify({
            "message": "Bad request. Request has no body"
        }), 400
    else:
        try:
            request_data = request.get_json()
            message = request_data['message']
            response = request_data['response']
        except KeyError as ke:
            return jsonify({
                "message": f"Bad request. Request body is not complete. missing {ke} key"
            }), 400 
    
        d = exec_db("INSERT INTO datasets(message,response) VALUES (?, ?)", (message, response), one=True)
        return jsonify({
            'message' : d
        })

@app.route('/dataset/edit', methods=['POST'])
def edit_dataset():
    if not request.json:
        return jsonify({
            "message": "Bad request. Request has no body"
        }), 400
    else:
        try:
            request_data = request.get_json()
            id = request_data['id']
            message = request_data['message']
            response = request_data['response']
        except KeyError as ke:
            return jsonify({
                "message": f"Bad request. Request body is not complete. missing {ke} key"
            }), 400 
        
        d = exec_db("UPDATE datasets SET message = ?, response = ? WHERE id = ?", (message, response, id), one=True)
        return jsonify({
            'message' : d
        })
        
@app.route('/dataset/delete', methods=['GET'])
def delete_dataset():
    id = request.args.get('id')
    if(id):
        d = exec_db("DELETE FROM datasets WHERE id = ?", [id], one=True)
        return jsonify({
            'message' : d
        })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
