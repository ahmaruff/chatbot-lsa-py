from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import csv

#!usr/bin/python3
import os
from CHATBOT_LSA import lsa

def get_lsa_response(input_text):
    lsa_response = lsa(input_text)
    return lsa_response
    
    file_path = os.getcwd() + '/fallback_sentences.txt'
    with open(file_path, 'a') as file:
        file.write(input_text + "\n")

app = Flask(__name__)

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
    print(type(payload))
    if(type(payload) == str):
        return jsonify({
            'result' : {
                'messages' : {
                    'speech' : payload
                }
            }
        })
    else:
        return jsonify(payload)

@app.route('/lsa', methods=['POST'])
def lsa_post():
    if not request.json:
        return jsonify({
            "status": 400,
            "message": "Bar request. Request has no body"
        })
    else:
        print(request.get_json())
        payload = get_lsa_response(request.get_json()['query'])
        print(type(payload))
        if(type(payload) == str):
            return jsonify({
                'result' : {
                    'messages' : {
                        'speech' : payload
                    }
                }
            })
        else:
            return jsonify(payload)

@app.route('/uploads', methods=['POST'])
def upload_dataset():
    if 'dataset' not in request.files:
        return jsonify({
            "status": 400,
            "message": "missing dataset" 
        })

    file = request.files['dataset']

    # Mengecek apakah file memiliki ekstensi .csv
    if not file.filename.endswith('.csv'):
        return jsonify({
            "status": 400,
            "message": "file must be using csv format"
        })
    
    # save temporary
    tmp_path = os.getcwd() + '/tmp_dataset.csv'
    file.save(tmp_path)
    
    # dataset baru
    new_dataset = []
    with open(tmp_path, 'r') as f:
        reader = csv.reader(f)
        next(reader, None) #skip header
        new_dataset = list(reader)

    # remove tmp csv
    os.remove(tmp_path)
    
    # buka dataset lama
    existing_dataset_path = os.getcwd()+'/dataset/dataset.csv'
    existing_dataset = []
    with open(existing_dataset_path, 'r') as existing_file:
        reader = csv.reader(existing_file)
        existing_dataset = list(reader)
    
    # combine dataset lama dan dataset baru
    combined_dataset = existing_dataset + new_dataset

    # write ke file dataset
    with open(existing_dataset_path, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(combined_dataset)

    return jsonify({
        "status": 200,
        "message": "dataset uploaded successfully"
    })


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)