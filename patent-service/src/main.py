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
    metaDataFileName = configReader.getProperty("metadataFileName")
    datasetPath = configReader.getDatasetPath()
    storeDocument.process_and_store_documents(datasetPath+"/documents",datasetPath+"/"+metaDataFileName,configReader.getDatabaseDir())
    
storeDocuments()