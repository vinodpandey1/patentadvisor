from service.metadataextraction.extractMetaData import process_multiple_pdfs
from service import configReader
from service.document import storeDocument
import os
from dotenv import load_dotenv

load_dotenv()

   
def readMetaData():
    datasetPath = configReader.getDatasetPath()  # Replace with the path to your folder containing PDF files
    print(datasetPath)
    metadata_dict = process_multiple_pdfs(datasetPath+"/documents")
    print(metadata_dict)
    # Display results
    for filename, metadata in metadata_dict.items():
        print(f"\nMetadata for {filename}:= \n")
        print(metadata)
        
def storeDocuments():
    metadatafilename = configReader.getProperty("metadatafilename")
    datasetPath = configReader.getDatasetPath()
    storeDocument.process_and_store_documents(datasetPath+"/documents",datasetPath+"/"+metadatafilename,configReader.getDatabaseDir())
    
# storeDocuments()

client, collection = storeDocument.ChromaDBClient.get_collection(configReader.getDatabaseDir())
print(collection.get("US8892906_1"))
results = collection.query(
    query_texts=["US Patent"], # Chroma will embed this for you
    n_results=2 # how many results to return
)
# print(results)