import os
import boto3

import src.llmtemplate.template
from src.service.audio.gen_audio import AudioGenerator
from src.service.image.gen_image import ImageGenerator
from src.service.metadataextraction.document_processor import DocumentProcessor
from src.service.podcast.podcast_gen import PodcastGenerator, Script
from src.service.summarization.patent_summarizer import PdfPatentSummarizer
from src.service.metadataextraction.document_processor import MetaExtractor
from src.service.supabase_client import initialize_supabase
from src.utils import logger
import src.utils as utils
from src import constants as const
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()


class PatentAdvisorPipeLine:

    def __init__(self):
        # Retrieve credentials from environment variables
        access_key = os.getenv('CLOUDFLARE_R2_ACCESS_KEY')
        secret_key = os.getenv('CLOUDFLARE_R2_SECRET_KEY')
        self.bucket_name = os.getenv('CLOUDFLARE_BUCKET_NAME')
        self.bucket_url = os.getenv('CLOUDFLARE_BUCKET_URL')
        endpoint_url = os.getenv('CLOUDFLARE_URL')
        self.upload_dir_prefix = os.getenv('CLOUDFLARE_UPLOAD_DIRECTORY_PREFIX')
        self.summary_dir_prefix = os.getenv('CLOUDFLARE_SUMMARY_DIRECTORY_PREFIX')
        self.audio_dir_prefix = os.getenv('CLOUDFLARE_AUDIO_DIRECTORY_PREFIX')
        self.podcast_dir_prefix = os.getenv('CLOUDFLARE_PODCAST_DIRECTORY_PREFIX')
        self.image_dir_prefix = os.getenv('CLOUDFLARE_IMAGE_DIRECTORY_PREFIX')
        self.patent_dir_prefix = os.getenv('CLOUDFLARE_PATENT_DIRECTORY_PREFIX')
        self.supabase = initialize_supabase()

        if not all([access_key, secret_key, self.bucket_name, endpoint_url]):
            logger.error("One or more Cloudflare R2 credentials are missing in the .env file.")
            raise ValueError("One or more Cloudflare R2 credentials are missing in the .env file.")

            # Initialize the S3 client with Cloudflare R2 credentials
        logger.info("Initializing S3 client for Cloudflare R2.")
        self.s3_client = boto3.client(
            's3',
            region_name='auto',  # Cloudflare R2 uses 'auto' for region
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.patent_summarizer = PdfPatentSummarizer()
        self.audio_gen = AudioGenerator()
        self.podcast_gen = PodcastGenerator()
        self.image_gen = ImageGenerator()

    def upload_file(self, file_path: str):
        logger.info(f"Starting to upload file {file_path}")
        file_name, file_name_without_ext = utils.get_file_name_and_without_extension(file_path)
        if os.path.exists(file_path):
            response = self.s3_client.upload_file(file_path, self.bucket_name, self.upload_dir_prefix + file_name)
            url = self.bucket_url + "/" + self.upload_dir_prefix + file_name
            logger.info(f"response of file upload {file_path} is {response}")
            self.supabase.table(const.DOC_COLLECTION).insert({
                "document_id": file_name_without_ext,
                "file_name": file_name,
                "user_id": "7ec222c4-3bb2-418b-baf7-bf1b559a2a04",
                "file_url": url
            }).execute()
            logger.info(f"Inserted into documents collection  {file_name_without_ext} and {url}")
        else:
            logger.error(f"File not present at path {file_path}")

    def trigger_pipeline(self, pipeline_type):
        logger.info(f"Starting pipeline of type {pipeline_type}")

        logger.info(f"Fetching objects from bucket: {self.bucket_name} with prefix: {self.upload_dir_prefix}")
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.upload_dir_prefix)

        if 'Contents' not in response:
            logger.warning(f"No objects found in bucket: {self.bucket_name}")
            return {}

        pdf_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].lower().endswith('.pdf')]
        logger.info(f"Found {len(pdf_files)} PDF files in bucket.")
        for pdf_key in pdf_files:
            self.trigger_pipeline_for_pdf(pdf_key, pipeline_type)

    def trigger_pipeline_for_pdf(self, pdf_key, pipeline_type):
        try:
            logger.info(f"Downloading PDF: {pdf_key}")
            pdf_file = self.s3_client.get_object(Bucket=self.bucket_name, Key=pdf_key)
            pdf_content = pdf_file['Body'].read()

            pdf_text_content = utils.get_pdf_text_from_s3(pdf_content, pdf_key)
            pdf_file_name, pdf_file_name_without_ext = utils.get_file_name_and_without_extension(pdf_key)
            pdf_download_path = const.DATASET_DIR + "/tmp/" + pdf_file_name
            with open(pdf_download_path, 'wb') as f:
                f.write(pdf_content)
                logger.info(f"Downloaded PDF in local : {pdf_download_path}")

            url = self.bucket_url + "/" + self.upload_dir_prefix + pdf_file_name
            self.supabase.table(const.DOC_COLLECTION).insert({
                "document_id": pdf_file_name_without_ext,
                "file_name": pdf_file_name,
                "user_id": "7ec222c4-3bb2-418b-baf7-bf1b559a2a04",
                "file_url": url
            }).execute()
            logger.info(f"Inserted into documents collection  {pdf_file_name_without_ext} and {url}")

            documentProcessor = DocumentProcessor(pdf_download_path, pdf_file_name, pdf_file_name_without_ext,
                                                  self.supabase)
            uuid = utils.get_document_uuid(self.supabase, pdf_file_name_without_ext)
            logger.info(f"UUID for document {pdf_file_name} is {uuid}")

            if pipeline_type == "meta" or pipeline_type == "all":
                metaExtractor = MetaExtractor(pdf_download_path, pdf_file_name, pdf_file_name_without_ext)
                metadata = metaExtractor.process_pdf_file()
                metaExtractor.store_metadata_in_documents(self.supabase, metadata)
                documentProcessor.process_document(metadata, uuid)

            summary_output_file = const.OUTPUT_DIR + '/summary/' + pdf_file_name_without_ext + '.txt'
            if pipeline_type == "summary" or pipeline_type == "all" or pipeline_type == "audio":
                summary = self.patent_summarizer.summarize_text(pdf_text_content, pdf_file_name, summary_output_file)
                self.s3_client.upload_file(summary_output_file, self.bucket_name, self.summary_dir_prefix
                                           + pdf_file_name_without_ext + '.txt')
                logger.info(f"Uploaded summary file to {self.summary_dir_prefix}/{pdf_file_name_without_ext}.txt"
                            f" in bucket {self.bucket_name}")
                self.patent_summarizer.store_metadata_in_documents(self.supabase, summary, pdf_file_name_without_ext)

            if pipeline_type == "audio" or pipeline_type == "all":
                summary_text = utils.get_file_contents(summary_output_file)
                audio_output_file = const.OUTPUT_DIR + '/audio/' + pdf_file_name_without_ext + ".mp3"
                AudioGenerator.save_text_to_speech(summary_text, pdf_file_name, audio_output_file)
                self.s3_client.upload_file(audio_output_file, self.bucket_name, self.audio_dir_prefix
                                           + pdf_file_name_without_ext + '.mp3')
                logger.info(f"Uploaded audio file to {self.audio_dir_prefix}/{pdf_file_name_without_ext}.mp3"
                            f" in bucket {self.bucket_name}")
                audio_url = self.bucket_url + "/" + self.audio_dir_prefix + pdf_file_name_without_ext + ".mp3"
                AudioGenerator.store_metadata_in_documents(self.supabase, audio_url, pdf_file_name_without_ext)

            if pipeline_type == "podcast" or pipeline_type == "all":
                podcast_output_file = const.OUTPUT_DIR + '/podcast/' + pdf_file_name_without_ext + ".wav"
                podcast_dialog_file = const.OUTPUT_DIR + '/podcast/' + pdf_file_name_without_ext + ".txt"
                script = self.podcast_gen.generate_script(src.llmtemplate.template.PODCAST_PROMPT, pdf_text_content,
                                                          Script,
                                                          pdf_file_name, podcast_dialog_file)
                self.s3_client.upload_file(podcast_dialog_file, self.bucket_name, self.podcast_dir_prefix
                                           + pdf_file_name_without_ext + '.txt')
                self.podcast_gen.generate_podcast(script, pdf_file_name, podcast_output_file)
                self.s3_client.upload_file(podcast_output_file, self.bucket_name, self.podcast_dir_prefix
                                           + pdf_file_name_without_ext + '.wav')
                logger.info(f"Uploaded podcast file to {self.podcast_dir_prefix}/{pdf_file_name_without_ext}.wav"
                            f" in bucket {self.bucket_name}")
                podcast_url = self.bucket_url + "/" + self.podcast_dir_prefix + pdf_file_name_without_ext + ".wav"
                self.podcast_gen.store_metadata_in_documents(self.supabase, podcast_url, pdf_file_name_without_ext)

            if pipeline_type == "image" or pipeline_type == "all":
                print(pdf_file_name_without_ext)
                print(pdf_file_name)

                image_output_file = const.OUTPUT_DIR + '/image/' + pdf_file_name_without_ext
                self.image_gen.extract_images(pdf_content, image_output_file)

                files = os.listdir(const.OUTPUT_DIR + '/image/')
                # Filter files that start with the specified prefix
                filtered_files = [file for file in files if file.startswith(pdf_file_name_without_ext)]

                for file in filtered_files:
                    file_path = os.path.join(const.OUTPUT_DIR + '/image/', file)

                    # Example: Print the file path (replace with your processing logic)
                    #print(f"Processing file: {file}")
                    #print(f"Full path: {file_path}")

                    self.s3_client.upload_file(file_path, self.bucket_name, self.image_dir_prefix +
                                               pdf_file_name_without_ext + "/" + file)

                logger.info(f"Uploaded image file for {self.image_dir_prefix}/{pdf_file_name_without_ext}"
                            f" in bucket {self.bucket_name}")

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_key}: {str(e)}")


if __name__ == "__main__":
    print("start pipeline")
    pipeline = PatentAdvisorPipeLine()
    dir_path = "/Users/amitarora/workspace/poc-workspace/capstone/patentadvisor/patent-service/dataset/documents"
    onlyfiles = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    print(onlyfiles)
    #pipeline.upload_file("/Users/amitarora/workspace/poc-workspace/capstone/patentadvisor/patent-service/dataset/documents/AI_PATENT/US8874431.pdf")
