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
import pandas as pd
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

# Split documents into chunks
def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    document_chunks = []
    for doc in documents.values():
        document_chunks.extend(text_splitter.split_documents(doc))
    return document_chunks

# Create embeddings and store in FAISS
def create_vector_store(document_chunks,persist_directory):
    embedding = OpenAIEmbeddings(model='text-embedding-3-small')
    
    chroma_store = Chroma(
    collection_name="pdfdocuments",
    embedding_function=embedding,
    persist_directory=persist_directory
    )

    if chroma_store._collection.count() ==0 :
        chroma_store = Chroma.from_documents(
        documents=document_chunks, # splits we created earlier
        collection_name="patentdocuments",
        embedding=embedding,
        persist_directory=persist_directory, # save the directory
        )
        print("PDF Documents uploaded to the database")
        print(chroma_store._collection_name)
    else:
        
        print("Existing Database found with the name pdfdocuments")
        print(chroma_store._collection.count())
        print(chroma_store._collection_name)
   
    return chroma_store

def process_and_store_documents(datasetDir,patentDataFile,db_storage_path):
    # Load documents from the folder
    

    df = pd.read_csv(patentDataFile)
    df =  cleanData(df)
    for index, row in df.iterrows():
        print(f"Processing row {index}: {row.to_dict()}")
        patentName = row['Patent Name']

        documents = load_documents_from_folder(datasetDir, patentName)
    
        # # Split documents into chunks
        document_chunks = split_documents(documents)
    
        # # Create embeddings and store in FAISS
        vector_store = create_vector_store(document_chunks,db_storage_path)
    
        # return vector_store

def cleanData(patentData):

    # df = df.remove('Sr.No.', axis=1, inplace=True)
    return patentData

def fetch_file_from_directory(directory, patentDocumentName):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            if path.find(patentDocumentName) > 0:
                return path
    return file_paths