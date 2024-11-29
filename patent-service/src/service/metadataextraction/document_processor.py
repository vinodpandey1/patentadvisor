import json

import pdfplumber
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.llmtemplate.template import METADATA_PROMPT_TEMPLATE
from src.service import supabase_client
from src.service.llm import llm_model
from langchain_core.documents import Document

import logging
from logging import config

import src.constants as const
from src.service.supabase_client import SupabaseClient

config.fileConfig(const.CONFIG_DIR + "/logging.conf")
logger = logging.getLogger("patent")


def extract_metadata_with_llm(template, text):
    llm = llm_model.get_chat_model("gpt-3.5-turbo")
    llm.temperature = 0
    prompt = template.format(content=text)
    response = llm.invoke(prompt)
    return response.content


class MetaExtractor:

    def __init__(self, pdf_path, pdf_file_name, pdf_file_name_without_ext):
        self.pdf_path = pdf_path
        self.pdf_file_name = pdf_file_name
        self.pdf_file_name_without_ext = pdf_file_name_without_ext

    def get_top_pages_content_from_pdf(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            text = ''
            for page in pdf.pages[:2]:
                text += page.extract_text()
        return text

    def process_pdf_file(self):
        text = self.get_top_pages_content_from_pdf()
        metadata = extract_metadata_with_llm(METADATA_PROMPT_TEMPLATE, text)
        logger.info(f"Extracted metadata for {self.pdf_file_name} -  {metadata}")
        return metadata

    def store_metadata_in_documents(self, supabase, metadata):
        metadata_json = json.loads(metadata)
        title = metadata_json["title"]
        patent_number = metadata_json["patentNumber"]
        supabase.table(const.DOC_COLLECTION).update({
            "patent_id": patent_number,
            "patent_title": title
        }).eq("document_id", self.pdf_file_name_without_ext).execute()
        logger.info(f"Stored information for {self.pdf_file_name} in {const.DOC_COLLECTION} - {patent_number} and {title}")


def chunk_metadata(metadata):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    meta_chunks = []
    meta_chunks.extend(text_splitter.split_text(metadata))
    return meta_chunks


def chunk_document(document):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    document_chunks = []
    document_chunks.extend(text_splitter.split_documents(document))
    return document_chunks


class DocumentProcessor:

    def __init__(self, pdf_path, pdf_file_name, pdf_file_name_without_ext):
        self.pdf_path = pdf_path
        self.pdf_file_name = pdf_file_name
        self.pdf_file_name_without_ext = pdf_file_name_without_ext

    def process_document(self, metadata):

        loader = PyPDFLoader(self.pdf_path)
        document = loader.load()

        meta_chunks = chunk_metadata(metadata)
        logger.info(f"Completed metadata chunking for file {self.pdf_file_name}")
        document_chunks = chunk_document(document)
        logger.info(f"Completed document chunking for file {self.pdf_file_name}")

        self.store_document(const.META_COLLECTION, meta_chunks, metadata)
        logger.info(f"Stored metadata {self.pdf_file_name} in vector store collection {const.META_COLLECTION}")
        self.store_document(const.DOC_CHUNK_COLLECTION, document_chunks, metadata)
        logger.info(f"Stored document {self.pdf_file_name} in vector store collection {const.DOC_COLLECTION}")

    def store_document(self, collection_name, chunks, metadata):

        client, collection, vector_store = SupabaseClient.get_collection(collection_name)
        i = 0
        documents = []
        if isinstance(metadata, str):
            metadata = eval(metadata)
        if len(chunks) == 0:
            logger.error("No content found for document", {self.pdf_file_name})
        else:
            for chunk in chunks:
                i = i + 1

                if not hasattr(chunk, 'page_content'):
                    text = chunk
                else:
                    text = chunk.page_content
                document_temp = Document(
                    page_content=text,
                    metadata=metadata,
                    id=self.pdf_file_name_without_ext + "_" + str(i),
                    document_id=self.pdf_file_name_without_ext
                )
                documents.append(document_temp)

            vector_store.add_documents(documents, ids=[doc.id for doc in documents])
