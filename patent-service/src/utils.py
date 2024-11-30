import io
import os
from pypdf import PdfReader

import logging
from logging import config

import src.constants as const

config.fileConfig(const.CONFIG_DIR + "/logging.conf")
logger = logging.getLogger("patent")


def get_file_name_and_without_extension(file_path):
    file_name = os.path.basename(file_path).split('/')[-1]
    file_tuple = os.path.splitext(file_name)
    return file_name, file_tuple[0]


def validate_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The File '{file_path}' does not exist.")
    if not file_path.endswith(".pdf"):
        raise ValueError(f"The file is '{file_path}' not pdf file")


def get_pdf_text(pdf_file: str):
    text = ''

    # Read the PDF file and extract text
    try:
        with open(pdf_file, "rb") as f:
            reader = PdfReader(f)
            logger.info(f"Reading the text from {pdf_file}")
            text = "\n\n".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        logger.error(f"Error reading the PDF file ({pdf_file}): {str(e)}")
        raise f"Error reading the PDF file: {str(e)}"
        raise e

        # Check if the PDF has more than ~400,000 characters
        # The context length limit of the model is 131,072 tokens and thus the text should be less than this limit
        # Assumes that 1 token is approximately 4 characters
    if len(text) > 400000:
        logger.error(f"PDF {pdf_file} is too long")
        raise "The PDF is too long. Please upload a PDF with fewer than ~131072 tokens."

    return text


def get_pdf_text_from_s3(pdf_data, pdf_file_name):
    text = ''
    try:
        reader = PdfReader(io.BytesIO(pdf_data))

        # Extract text from each page
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()
    except Exception as e:
        logger.error(f"Error reading the PDF file ({pdf_file_name}): {str(e)}")
        raise f"Error reading the PDF file: {str(e)}"
    return text


def get_file_contents(text_file: str):
    text = ""
    try:
        with open(text_file, "r") as f:
            text = f.read()
    except Exception as e:
        logger.error(f"Error reading the text file ({text_file}): {str(e)}")
        raise f"Error reading the text file: {str(e)}"
    return text


def is_output_file_exists(output_file):
    if os.path.exists(output_file):
        return True
    else:
        return False
