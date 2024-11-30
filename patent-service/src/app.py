import json
from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import request
from src.service.document import searchDocumentService

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)


@app.route('/')
def home():
    return jsonify({"message": "Call Multiple LLM"})

@app.route('/searchPatent')
def search():  
    query = request.args.get('query')
    documentList = searchDocumentService.searchDocument(query)
    documentList_json = json.dumps(documentList, indent=4)
    return documentList_json

@app.route('/query')
def search():  
    query = request.args.get('query')
    documentList = searchDocumentService.queryDocument(query)
    documentList_json = json.dumps(documentList, indent=4)
    return documentList_json



if __name__ == '__main__':
    app.run(debug=False)


