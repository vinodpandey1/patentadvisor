from service.metadataextraction.extractMetaData import process_multiple_pdfs
from service.configReader import getDatasetPath
import os
from dotenv import load_dotenv

load_dotenv()

    
def readMetaData():
    pdf_folder_path = getDatasetPath()  # Replace with the path to your folder containing PDF files
    print(pdf_folder_path)
    metadata_dict = process_multiple_pdfs(pdf_folder_path)
    print(metadata_dict)
    # Display results
    for filename, metadata in metadata_dict.items():
        print(f"\nMetadata for {filename}:= \n")
        print(metadata)
        
readMetaData()