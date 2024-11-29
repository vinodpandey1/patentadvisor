from gtts import gTTS
from clearml import Task

from langchain_community.callbacks import ClearMLCallbackHandler
from langchain_core.callbacks import StdOutCallbackHandler

import os
from dotenv import load_dotenv

import logging
from logging import config

import src.constants as const
import src.utils as utils

config.fileConfig(const.CONFIG_DIR + "/logging.conf")
logger = logging.getLogger("patent")


class AudioGenerator:

    def __init__(self):
        load_dotenv()
        '''Task.init(const.CLEARML_PROJECT, const.SUMMARISATION_TASK)
        self.clearml_callback = ClearMLCallbackHandler(
            task_type="testing",
            project_name= const.CLEARML_PROJECT,
            task_name= const.AUDIO_GEN_TASK,
            tags=["audio_generator"],                               
            visualize=True,                               
            complexity_metrics=True,                   
            stream_logs=True                             
        )
        self.callbacks = [StdOutCallbackHandler(), self.clearml_callback]'''

    @staticmethod
    def save_text_to_speech(text, file_name, output_file):
        if not utils.is_output_file_exists(output_file):
            try:
                # Initialize gTTS with the given text
                tts = gTTS(text, lang="en", slow=False, tld="us")
                # Save the generated speech to an audio file
                tts.save(output_file)
                logger.info(f"Generated audio of {file_name} at location {output_file}")
            except Exception as e:
                print(f"Error during text-to-speech conversion: {e}")
        else:
            logger.info(f"Saving processing!! Audio of {file_name} already exists at location {output_file}...")

    @classmethod
    def store_metadata_in_documents(cls, supabase, audio_url, pdf_file_name_without_ext):
        supabase.table(const.DOC_COLLECTION).update({
            "audio_url": audio_url,
        }).eq("document_id", pdf_file_name_without_ext).execute()
        logger.info(
            f"Stored audio URL for {pdf_file_name_without_ext} in {const.DOC_COLLECTION}")


if __name__ == "__main__":
    audio_gen = AudioGenerator()
    summary_file = const.OUTPUT_DIR + "/summary" +"/US20190213407A1.txt"
    _, file_name_without_ext=utils.get_file_name_and_without_extension(summary_file)
    text = utils.get_file_contents(summary_file)
    output_file = const.OUTPUT_DIR + '/audio/'+file_name_without_ext
    audio_gen.save_text_to_speech(text, output_file + '.mp3', summary_file)
