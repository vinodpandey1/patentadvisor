from typing import List, Literal, Tuple, Optional
from pydantic import BaseModel, ValidationError
from pypdf import PdfReader

from together import Together
from cartesia import Cartesia

import subprocess
import ffmpeg
import os
from dotenv import load_dotenv

import logging
from logging import config

import src.constants as const
import src.utils as utils

config.fileConfig(const.CONFIG_DIR + "/logging.conf")
logger = logging.getLogger("patent")

class LineItem(BaseModel):
    """A single line in the script."""

    speaker: Literal["Host (Jane)", "Guest"]
    text: str


class Script(BaseModel):
    """The script between the host and guest."""

    scratchpad: str
    name_of_guest: str
    script: List[LineItem]

class Podcast_Generator:
    
    def __init__(self):
        load_dotenv()  # Make sure to load environment variables from .env file
        self.client_together = Together(api_key=os.getenv("TOGETHER_AI_API_KEY"))
        self.client_cartesia = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))

    def get_PDF_info(self, pdf_file : str):
        text = ''

        # Read the PDF file and extract text
        try:
            with open(pdf_file, "rb") as f:
                reader = PdfReader(f)
                logger.info(f"Reading the text from {pdf_file} for generating podcast")
                text = "\n\n".join([page.extract_text() for page in reader.pages])
        except Exception as e:
            logger.error(f"Error reading the PDF file ({pdf_file}): {str(e)}")
            raise f"Error reading the PDF file: {str(e)}"
            raise e

            # Check if the PDF has more than ~400,000 characters
            # The context length limit of the model is 131,072 tokens and thus the text should be less than this limit
            # Assumes that 1 token is approximately 4 characters
        if len(text) > 400000:
            logger.error(f"PDF {pdf_file} is too long to generate the podcast")
            raise "The PDF is too long. Please upload a PDF with fewer than ~131072 tokens."

        return text

    def call_llm(self, system_prompt: str, text: str, dialogue_format):
        """Call the LLM with the given prompt and dialogue format."""
        response = self.client_together.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            response_format={
                "type": "json_object",
                "schema": dialogue_format.model_json_schema(),
            },
        )
        return response

    def generate_script(self, system_prompt: str, input_text: str, output_model, pdf_file, dialog_file):
        """Get the script from the LLM."""
        # Load as python object
        try:
            response = self.call_llm(system_prompt, input_text, output_model)
            dialogue = output_model.model_validate_json(
                response.choices[0].message.content
            )
            with open(dialog_file, "w") as f:
                f.write(repr(dialogue))
            logger.info(f"Generating dialog for {pdf_file} for generating podcast")
        except ValidationError as e:
            error_message = f"Failed to parse dialogue JSON: {e}"
            logger.warn(f"Failed to parse dialogue JSON: {e}, retrying with LLM for pdf file {pdf_file}")
            system_prompt_with_error = f"{system_prompt}\n\nPlease return a VALID JSON object. This was the earlier error: {error_message}"
            response = self.call_llm(system_prompt_with_error, input_text, output_model)
            dialogue = output_model.model_validate_json(
                response.choices[0].message.content
            )
        return dialogue
    
    def generate_podcast(self, script, podcast_file, pdf_file):
        
        host_id = "694f9389-aac1-45b6-b726-9d9369183238" # Jane - host voice
        guest_id = "a0e99841-438c-4a64-b679-ae501e7d6091" # Guest voice
        model_id = "sonic-english" # The Sonic Cartesia model for English TTS
        output_format = {
            "container": "raw",
            "encoding": "pcm_f32le",
            "sample_rate": 44100,
            }
        
        temp_podcast_pcm = const.OUTPUT_DIR + "/podcast/podcast.pcm"
        if os.path.exists(temp_podcast_pcm):
            os.remove(temp_podcast_pcm)
        if os.path.exists(podcast_file):
            os.remove(podcast_file)
        logger.info(f"Generating pcm for {pdf_file} at location {temp_podcast_pcm}")
        
        ws = self.client_cartesia.tts.websocket()
        f = open(temp_podcast_pcm, "wb")

        # Generate and stream audio.
        for line in script.script:
            if line.speaker == "Guest":
                voice_id = guest_id
            else:
                voice_id = host_id

            for output in ws.send(
                model_id=model_id,
                transcript='-' + line.text, # the "-"" is to add a pause between speakers
                voice_id=voice_id,
                stream=True,
                output_format=output_format,
            ):
                buffer = output["audio"]  # buffer contains raw PCM audio bytes
                f.write(buffer)

        # Close the connection to release resources
        ws.close()
        f.close()

        # Convert the raw PCM bytes to a WAV file.
        logger.info(f"Generating wav file for {pdf_file} at location {podcast_file}")
        ffmpeg.input(temp_podcast_pcm, format="f32le").output(podcast_file).run()
        
        if os.path.exists(temp_podcast_pcm):
            os.remove(temp_podcast_pcm)


podcast_gen = Podcast_Generator()
pdf_file = const.INPUT_PATENT_DIR_PATH + "/US9736308.pdf"
_, file_name_without_ext=utils.get_file_name(pdf_file)
text = podcast_gen.get_PDF_info(pdf_file)
output_file = const.OUTPUT_DIR + '/podcast/'+file_name_without_ext
script = podcast_gen.generate_script(const.PODCAST_PROMPT, text, Script, pdf_file, output_file + '.txt')
podcast_gen.generate_podcast(script, output_file + '.wav', pdf_file)
