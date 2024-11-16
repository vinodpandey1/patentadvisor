import os
import openai
import numpy as np
from langchain_community.document_loaders import PyPDFLoader
import gradio as gr
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from service import configReader
from service.llm import chatmodel
import pandas as pd
import chromadb

def process_and_store_documents(datasetDir,patentDataFile,db_storage_path):
    # Load documents from the folder
    
    df = pd.read_csv(patentDataFile)
    df =  cleanData(df)
    for index, row in df.iterrows():
        rowData  = row.to_dict()
        print(f"Processing row {index}: {rowData}")

        patentName = row['Patent Name']

        documents = load_documents_from_folder(datasetDir, patentName)
    
        # # Split documents into chunks
        document_chunks = split_documents(documents)
    
        # # Create embeddings and store in FAISS
        store_document(db_storage_path,patentName, document_chunks,rowData)

def cleanData(patentData):

    # df = df.remove('Sr.No.', axis=1, inplace=True)
    return patentData

# Function to load and display content from all PDF files in the folder
def load_documents_from_folder(datasetDir, patentName):
    # List to store the content of all documents
    documents_content = {}
    
    file = fetch_file_from_directory(datasetDir, patentName)
    # Check if the folder exists
    if not os.path.exists(file):
        raise FileNotFoundError(f"The File '{file}' does not exist.")
    
    if file.endswith(".pdf"):
            
        # Load the document using PyPDFLoader
        loader = PyPDFLoader(file)
        document = loader.load()  # This will return the document content
            
        # Store the content of the document in the dictionary
        documents_content[file] = document
    
    # Return the dictionary with document names and their contents
    return documents_content

def fetch_file_from_directory(directory, patentDocumentName):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            if path.find(patentDocumentName) > 0:
                return path
    return file_paths

# Split documents into chunks
def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    document_chunks = []
    for doc in documents.values():
        document_chunks.extend(text_splitter.split_documents(doc))
    return document_chunks

# Create embeddings and store in FAISS
def store_document(db_storage_path, documentname, document_chunks,metadata):


    client, collection = ChromaDBClient.get_collection(db_storage_path)
    i=0
    for chunk in document_chunks:
        i=i+1
        print(chunk.id)
        print(chunk.page_content)
        collection.add(
            documents=[chunk.page_content],
            metadatas=[metadata],
            ids=[documentname+"_"+str(i)]
        )    

class ChromaDBClient:
    _client = None
    _collection = None

    @staticmethod
    def get_collection(persist_directory,collection_name="patentdocuments"):
            
        emb_fn = chatmodel.getEmbeddingFunction("openai-embedding")
        if ChromaDBClient._client is None:
            ChromaDBClient._client = chromadb.PersistentClient(path=persist_directory)
            ChromaDBClient._collection = ChromaDBClient._client.get_or_create_collection(collection_name,embedding_function=emb_fn)
        return ChromaDBClient._client,ChromaDBClient._collection
 