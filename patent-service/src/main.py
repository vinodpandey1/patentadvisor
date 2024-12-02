from src.service.metadataextraction.extractMetaData import process_multiple_pdfs
from src.service import configReader
from src.service.document import storeDocument, searchDocumentService
import os
from dotenv import load_dotenv
from langchain.retrievers.self_query.base import SelfQueryRetriever
import json
load_dotenv()

## This function will read the metadata from the documents and will store in database
def readMetaDataAndStore():
    datasetPath = configReader.getDatasetPath()  # Replace with the path to your folder containing PDF files
    print(datasetPath)
    metadata_dict, metadatainfo = process_multiple_pdfs(datasetPath+"/documents", 1)
    # print(metadata_dict)
    # Display results

    for filename, metadata in metadata_dict.items():
        print(f"\nMetadata for {filename}:= \n")
        print(metadata)
        
        # Convert metadata keys to lower case
    
        filename = os.path.basename(filename)
        filename = filename.split('.')[0]
        print(filename)
        storeDocument.process_and_store_documents_from_metadata(datasetPath+"/documents",filename,metadata,configReader.getDatabaseDir())
        
## This function will get the metadata info from the documents and store it in metadatainfo.json
def getMetaDataInfo():
    datasetPath = configReader.getDatasetPath()  # Replace with the path to your folder containing PDF files
    print(datasetPath)
    metadata_dict, metadatainfo = process_multiple_pdfs(datasetPath+"/documents", 1)
    print("Metadata Info")
    print(metadatainfo)

    with open('metadatainfo.json', 'w') as json_file:
        json.dump(metadatainfo, json_file, indent=4)
    print("Metadata Info written to metadatainfo.json")


## This function will store the documents in the database from given csv file
def storeDocuments():
    metadatafilename = configReader.getProperty("metadatafilename")
    datasetPath = configReader.getDatasetPath()
    storeDocument.process_and_store_documents_from_csv(datasetPath+"/documents",datasetPath+"/"+metadatafilename,configReader.getDatabaseDir())
    client, collection, vector_store = storeDocument.ChromaDBClient.get_collection(configReader.getDatabaseDir())
    
    print("Collection ID:",collection.id)
    print(f"Total Document Count is " ,collection.count())
    ids = collection.get()['ids']
    print(f"Document IDs: {ids}")


#getMetaDataInfo()
readMetaDataAndStore()
#storeDocuments()
#searchDocumentService.getQueryStructure("find patent where technology Digital Music") 
#searchDocumentService.getQueryStructure("find patent for patent number US010854180B2") 
