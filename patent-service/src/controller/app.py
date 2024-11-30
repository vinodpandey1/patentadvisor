import json
import os

import boto3
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Response

from src.service.document import searchDocumentService
from src.service.pipeline import PatentAdvisorPipeLine
from src.utils import logger

app = FastAPI()
load_dotenv()
access_key = os.getenv('CLOUDFLARE_R2_ACCESS_KEY')
secret_key = os.getenv('CLOUDFLARE_R2_SECRET_KEY')
bucket_name = os.getenv('CLOUDFLARE_BUCKET_NAME')
bucket_url = os.getenv('CLOUDFLARE_BUCKET_URL')
endpoint_url = os.getenv('CLOUDFLARE_URL')
upload_dir_prefix = os.getenv('CLOUDFLARE_UPLOAD_DIRECTORY_PREFIX')
summary_dir_prefix = os.getenv('CLOUDFLARE_SUMMARY_DIRECTORY_PREFIX')
audio_dir_prefix = os.getenv('CLOUDFLARE_AUDIO_DIRECTORY_PREFIX')
podcast_dir_prefix = os.getenv('CLOUDFLARE_PODCAST_DIRECTORY_PREFIX')
image_dir_prefix = os.getenv('CLOUDFLARE_IMAGE_DIRECTORY_PREFIX')
patent_dir_prefix = os.getenv('CLOUDFLARE_PATENT_DIRECTORY_PREFIX')

if not all([access_key, secret_key, bucket_name, endpoint_url]):
    logger.error("One or more Cloudflare R2 credentials are missing in the .env file.")
    raise ValueError("One or more Cloudflare R2 credentials are missing in the .env file.")

    # Initialize the S3 client with Cloudflare R2 credentials
logger.info("Initializing S3 client for Cloudflare R2.")
s3_client = boto3.client(
    's3',
    region_name='auto',  # Cloudflare R2 uses 'auto' for region
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)


@app.get("/patent/summary/{patent_name}")
def get_patent_summary(patent_name: str):
    file_key = summary_dir_prefix + patent_name + ".txt"
    file = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    file_content = file['Body'].read()
    logger.info(f"Got summary text for {patent_name} = {file_content}")
    return Response(content=file_content, media_type="text/plain")


@app.get("/patent/audio/{patent_name}")
def get_patent_audio(patent_name: str):
    file_url = bucket_url + "/" + audio_dir_prefix + patent_name + ".mp3"
    logger.info(f"Got audio for {patent_name} = {file_url}")
    return Response(content=file_url, media_type="audio/mpeg")


@app.get("/patent/podcast/{patent_name}")
def get_patent_podcast(patent_name: str):
    file_url = bucket_url + "/" + podcast_dir_prefix + patent_name + ".wav"
    logger.info(f"Got podcast for {patent_name} = {file_url}")
    return Response(content=file_url, media_type="audio/mpeg")


@app.get("/patent/images/{patent_name}")
def get_patent_images(patent_name: str):
    pass


@app.get('/searchPatent')
def search(query: str):
    try:
        documentList = searchDocumentService.searchDocument(query)
        documentList_json = json.dumps(documentList, indent=4)

        return documentList_json
    except Exception as e:
        print(e)

@app.route('/queryDocument')
def searchDocument(query: str, documentID: str):  
    documentList = searchDocumentService.queryDocument(query, documentID)
    documentList_json = json.dumps(documentList, indent=4)
    return documentList_json

@app.get("/patent/trigger/{patent_name}")
def trigger_pipeline_for_pdf(patent_name: str):
    pipeline = PatentAdvisorPipeLine()
    key = upload_dir_prefix + patent_name + ".pdf"
    logger.info(f"Triggering pipeline for pdf {key}")
    pipeline.trigger_pipeline_for_pdf(pdf_key=key, pipeline_type="all")


@app.get("/patent/query/{patent_name}")
def invoke_questions_answer_using_agent(patent_name: str):
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
