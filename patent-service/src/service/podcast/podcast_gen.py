from typing import List, Literal, Tuple, Optional
from pydantic import BaseModel, ValidationError
from langchain_community.callbacks import ClearMLCallbackHandler
from langchain_core.callbacks import StdOutCallbackHandler

from together import Together
from cartesia import Cartesia
from clearml import Task

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
        Task.init(const.CLEARML_PROJECT, const.PODCAST_GEN_TASK)
        self.clearml_callback = ClearMLCallbackHandler(
            task_type="testing",
            project_name= const.CLEARML_PROJECT,
            task_name= const.PODCAST_GEN_TASK,
            tags=["podcast_gen"],                               
            visualize=True,                               
            complexity_metrics=True,                   
            stream_logs=True                             
        )
        self.callbacks = [StdOutCallbackHandler(), self.clearml_callback]

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
        
        #self.clearml_callback.flush_tracker(langchain_asset=self.client_together, name="podcast_gen")
        
        if os.path.exists(temp_podcast_pcm):
            os.remove(temp_podcast_pcm)


podcast_gen = Podcast_Generator()
pdf_file = const.INPUT_PATENT_DIR_PATH + "/US10612929.pdf"
_, file_name_without_ext=utils.get_file_name_and_without_extension(pdf_file)
text = utils.get_pdf_text(pdf_file)
output_file = const.OUTPUT_DIR + '/podcast/'+file_name_without_ext
script = podcast_gen.generate_script(const.PODCAST_PROMPT, text, Script, pdf_file, output_file + '.txt')
podcast_gen.generate_podcast(script, output_file + '.wav', pdf_file)
