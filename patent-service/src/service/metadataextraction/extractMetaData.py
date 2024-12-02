import os
import pdfplumber
import openai
from src.service.llm.chatmodel import getChatModel
from src.llmtemplate.template import METADATA_PROMPT_TEMPLATE, METADATAINFO_PROMPT_TEMPLATE


def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages[:2]:
            text += page.extract_text()
    return text

# Function to prompt the LLM to extract metadata
def extract_metadata_with_llm(text):

    llm = getChatModel("gpt-3.5-turbo")
    llm.temperature = 0
    prompt = METADATA_PROMPT_TEMPLATE.format(content=text)
    response = llm.invoke(prompt)
    return response.content

def fetch_files_from_directory(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

# Main function to process all PDFs in a directory
def process_multiple_pdfs(pdf_folder_path, nofiles: int):
    all_metadata = {}
    metadatainfo = {}
        
    all_files =fetch_files_from_directory(pdf_folder_path)
    # Loop through each PDF file in the specified folder
    
    if(nofiles==None):
        nofiles=len(all_files)
    
    count=0
    for filename in all_files:
        print("finding pdf " + filename)
        if filename.endswith(".pdf"):
            count=count+1
            pdf_path = os.path.join(pdf_folder_path, filename)
            print(f"Processing {filename}...")

            # Extract text from the current PDF
            text = extract_text_from_pdf(pdf_path)
            # print(text)

            # Use LLM to extract metadata
            metadata = extract_metadata_with_llm(text)
            all_metadata[filename] = metadata
            if(count>=nofiles):
                break
    
    for filename, metadata in all_metadata.items():
       metadatainfo= extract_metadatainfo_with_llm(metadata)
       break
    return all_metadata, metadatainfo

def extract_metadatainfo_with_llm(text):

    llm = getChatModel("gpt-3.5-turbo")
    llm.temperature = 0
    prompt = METADATAINFO_PROMPT_TEMPLATE.format(content=text)
    response = llm.invoke(prompt)
    return response.content