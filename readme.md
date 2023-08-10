# chatbot LSA

Simple Chatbot web API using Latent Semantic Analysis Algorithm
[Ahmad Ma'ruf](mailto:ahmadmaruf2701@gmail.com)

## how to
1. install python3  
2. buat virtual environment  
`python3 -m venv venv` 
3. aktifkan virtual environment `source venv/bin/activate` 
4. install dependencies  
`pip install -r requirements.txt`
5. inisiasi database  
`python3 init_db.py`
6. jalankan program  
`python3 app.py`

## route untuk web api

| Route | Method | parameter | description |
|---|---|---|---|
| `/lsa` | GET | `?query=your question` | chatbot |
| `/lsa` | POST | `{query:your question}` | chatbot |
| `/uploads` | POST | `{dataset:yourfile.csv}` | add new dataset |
| `/train` | GET | -- | re-train dataset |
| `/dataset` | GET | -- | return dataset |
| `/dataset` | GET | `?id=1` | return single dataset by ID |
| `/dataset/add` | POST | `message:<msg>,response:<resp>}` | create single dataset |
| `/dataset/edit` | POST | `{id:<dataset_id>,message:<edited message>,response:<edited response>}` | edit/update single dataset |
| `/dataset/delete` | GET | `?id=1` | delete single dataset by ID |
