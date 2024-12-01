import json
import os

import boto3
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Response

from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI

from src.controller.agent import get_summary_of_patent, get_audio_url_of_patent, get_podcast_url_of_patent
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
    #return Response(content=file_url, media_type="audio/mpeg")
    return Response(content=file_url, media_type="text/plain")


@app.get("/patent/podcast/{patent_name}")
def get_patent_podcast(patent_name: str):
    file_url = bucket_url + "/" + podcast_dir_prefix + patent_name + ".wav"
    logger.info(f"Got podcast for {patent_name} = {file_url}")
    #return Response(content=file_url, media_type="audio/mpeg")
    return Response(content=file_url, media_type="text/plain")


@app.get("/patent/images/{patent_name}")
def get_patent_images(patent_name: str):
    # List objects with the specified prefix
    folder = "image/" + patent_name
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder)

    # Initialize the list to store file information
    file_data = []

    # Check if the response contains 'Contents'
    if 'Contents' in response:

        for obj in response['Contents']:
            full_file_name = obj['Key']
            # Extract just the file name (remove the prefix/folder path)
            file_name = os.path.basename(full_file_name)
            # Generate the URL for the object
            file_url = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': bucket_name, 'Key': file_name},
                                                        ExpiresIn=3600)  # URL expires in 1 hour (3600 seconds)
            # Append the file info (file name and URL) as a dictionary to the file_data list
            file_data.append({
                'file_name': file_name,
                'file_url': file_url
            })
        # Return the list of files as a JSON array
        response_json = json.dumps(file_data, indent=4)
        return json.loads(response_json)
    else:
        logger.error(f"No files found in '{bucket_name}' with prefix 'image'.")


@app.get('/searchPatent')
def search(query: str):
    try:
        documentList = searchDocumentService.searchDocument(query)       
        patent_list_json = json.dumps(documentList, indent=4)
        response = {"patentList": json.loads(patent_list_json)}
        
        # logger.info(f"Search results :{response}")     
      
        # return Response(content=response, media_type="application/json")
        return response
    except Exception as e:
        print(e)

@app.get("/queryDocument/{userid}/{patentID}")
def searchDocument(query: str, userid:str, patentID: str):  
    try:
        logger.info(f"Calling Search Document API {userid} {patentID}")
        llm_response , history_dict, bias_analyzer = searchDocumentService.queryDocument(query, userid,patentID)
        response = {"answer": llm_response, "history": history_dict, "bias": bias_analyzer}        
        response_json = json.dumps(response, indent=4)
        response = json.loads(response_json)
        # logger.info(f"Search results JSON Response :{response}")
        return response
        
    except Exception as e:
        logger.error(f"Error in searchDocument: {str(e)}")  

@app.post("/patent/trigger/{patent_name}")
def trigger_pipeline_for_pdf(patent_name: str):
    pipeline = PatentAdvisorPipeLine()
    key = upload_dir_prefix + patent_name + ".pdf"
    logger.info(f"Triggering pipeline for pdf {key}")
    pipeline.trigger_pipeline_for_pdf(pdf_key=key, pipeline_type="all")


@app.get("/patent/query/{patent_name}")
def invoke_questions_answer_using_agent(patent_name: str, query: str):
    llm = OpenAI(temperature=0)
    # Create the agent with the tool
    tools = [get_summary_of_patent, get_audio_url_of_patent, get_podcast_url_of_patent]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    return agent.run(query)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
