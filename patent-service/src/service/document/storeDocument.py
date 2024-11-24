import os
import openai
import numpy as np
from langchain_community.document_loaders import PyPDFLoader
import gradio as gr
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma

from langchain_core.documents import Document
from service import configReader, dbclient
from langchain_postgres import PGVector
from service.llm import chatmodel
import pandas as pd
import chromadb

def process_and_store_documents_from_csv(datasetDir,patentDataFile,db_storage_path):
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

def process_and_store_documents_from_metadata(datasetDir,patentName, patentMetaData,db_storage_path):
    # Load documents from the folder
    
    
    documents = load_documents_from_folder(datasetDir, patentName)
    
    # # Split documents into chunks
    
    
    text_chunks = split_text(patentMetaData)
    
    document_chunks = split_documents(documents)
    
    # # Create embeddings and store in FAISS
    store_document("patentdocuments",patentName, text_chunks,patentMetaData)
    
    store_document("patentdocumentdetail",patentName, document_chunks,patentMetaData)

def cleanData(patentData):

    # df = df.remove('Sr.No.', axis=1, inplace=True)
    return patentData

# Function to find the document in the folder and read content
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

# Function to find the document in the folder
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

def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    document_chunks = []
    document_chunks.extend(text_splitter.split_text(text))
    return document_chunks

# Create embeddings and store in Database. Using Langchain interface to stroe data in database
def store_document(collectionName, documentname, document_chunks,metadata):

    print("storing documents")
    client, collection, vector_store = dbclient.getDBClient(collectionName)
    i=0
    documents =[]
    if isinstance(metadata, str):
        metadata = eval(metadata)
    print(type(metadata))
    print(metadata)
    if(len(document_chunks)==0):    
        print("No content found for document", {documentname})
    else:
        for chunk in document_chunks:
            i=i+1
            print(chunk)
            
            if not hasattr(chunk, 'page_content'):
                text=chunk
            else:
                text=chunk.page_content
            document_temp = Document(
            page_content=text,
            metadata=metadata,
            id=documentname+"_"+str(i)
            )
            documents.append(document_temp)

        vector_store.add_documents(documents, ids=[doc.id for doc in documents])   
