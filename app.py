from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

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

@app.route('/lsa-get', methods=['GET'])
def lsa_get():
    query = request.args.get('q')
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

@app.route('/lsa-post', methods=['POST'])
def lsa_post():
    if not request.json:
        return jsonify({
            "status": 400,
            "message": "Bar request. Request has no body"
        })
    else:
        print(request.get_json())
        payload = get_lsa_response(request.get_json())
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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)