import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()  # Make sure to load environment variables from .env file
openai_api_key = os.getenv("OPENAI_API_KEY")

# Function to load the PDF document
def load_pdf(pdf_path):
    """Function to load and read the PDF file."""
    loader = PyPDFLoader(pdf_path)
    return loader.load()

# Function to split the document into chunks
def split_document(docs):
    """Function to split documents into chunks using RecursiveCharacterTextSplitter."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=1000)
    split_docs = text_splitter.split_documents(docs)
    return split_docs

# Function to create and run the summarization chain
def summarize_pdf(pdf_path):
    """Function to load, split, and summarize the PDF document."""
    # Load the PDF document
    docs = load_pdf(pdf_path)

    # Split the PDF content into chunks
    split_docs = split_document(docs)

    # Define the prompt template for the summary
    prompt_template = """Write a concise summary of the following:
    "{text}"
    CONCISE SUMMARY:"""
    prompt = PromptTemplate.from_template(prompt_template)

    # Initialize the LLM (using ChatOpenAI with gpt-4o-mini model)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)

    # Create the LLM chain with the correct prompt
    llm_chain = prompt | llm

    # Create the StuffDocumentsChain (combining the documents and prompt)
    stuff_chain = create_stuff_documents_chain(
        llm=llm, prompt=prompt, document_variable_name="text"
    )

    # Pass the split documents as input to the chain
    input_data = {"text": split_docs}

    # Run the chain to get the result
    result = stuff_chain.invoke(input_data)

    # Output the result (summary)
    print("Summary:")
    print(result)
    return result

if __name__ == "__main__":
    # Specify the path to the PDF file
    pdf_path = ## Update this to your PDF path ##
    
    # Call the summarize function
    summarize_pdf(pdf_path)
