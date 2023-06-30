# chatbot LSA

## how to
1. install python3
2. buat virtual environment
`python3 -m venv venv`
3. install dependencies
`pip install -r requirements.txt`
4. jalankan program
   1. jika mau mode cli `python3 chatbot.py`
   2. jika mau mode web api `python3 app.py`

## route untuk web api
route :`/lsa`, bisa pake method get maupun post


method `GET`
`/lsa?query="<<insert question here>>"`

method `POST`
`/lsa`

request body:

```json
{
    query : "<<insert your question here>>"
}
```
