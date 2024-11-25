from transformers import BigBirdPegasusForConditionalGeneration, AutoTokenizer
from clearml import Task

import os
from dotenv import load_dotenv

import logging
from logging import config

import src.constants as const
import src.utils as utils

config.fileConfig(const.CONFIG_DIR + "/logging.conf")
logger = logging.getLogger("patent")

#from langchain_community.callbacks import ClearMLCallbackHandler
#from langchain_core.callbacks import StdOutCallbackHandler


class PdfPatentSummarizer:
    
    def __init__(self):
        load_dotenv()
        model_name = "google/bigbird-pegasus-large-bigpatent"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = BigBirdPegasusForConditionalGeneration.from_pretrained(model_name)    
        '''Task.init(const.CLEARML_PROJECT, const.SUMMARISATION_TASK)
        self.clearml_callback = ClearMLCallbackHandler(
            task_type="testing",
            project_name= const.CLEARML_PROJECT,
            task_name= const.SUMMARISATION_TASK,
            tags=["summarizer"],                               
            visualize=True,                               
            complexity_metrics=True,                   
            stream_logs=True                             
        )
        self.callbacks = [StdOutCallbackHandler(), self.clearml_callback]'''

    def preprocess_text(self, text, max_tokens=4096):
        """
        Prepares the text for BigBird-Pegasus by truncating it to the token limit.
        """
        inputs = self.tokenizer(text, return_tensors="pt", max_length=max_tokens, truncation=True)
        return inputs

    def summarize_text(self, text, pdf_file, output_file):
        """
        Summarizes the input text using BigBird-Pegasus.
        """
        if not utils.is_output_file_exists(output_file):
            summary = ""
            try:
                logger.info(f"Generating summary of {pdf_file}")
                inputs = self.preprocess_text(text)
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=200,  # Adjust based on desired summary length
                    min_length=50,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True,
                    #callbacks = self.callbacks
                )
                summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            except Exception as e:
                logger.error(f"Error while generating summary of the PDF file ({pdf_file}): {str(e)}")
            if summary:
                with open(output_file, "w") as f:
                    f.write(summary)
                logger.info(f"Generated summary of {pdf_file} at location {output_file}")  
            #self.clearml_callback.flush_tracker(langchain_asset=self.model, name="sumarizer")
        else:
            logger.info(f"Saving processing!! Summary of {pdf_file} already exists at location {output_file}...")


if __name__ == "__main__":
    patent_summarizer = PdfPatentSummarizer()
    pdf_file = const.INPUT_PATENT_DIR_PATH + "/US20190213407A1.pdf"
    _, file_name_without_ext=utils.get_file_name_and_without_extension(pdf_file)
    text = utils.get_pdf_text(pdf_file)
    output_file = const.OUTPUT_DIR + '/summary/'+file_name_without_ext
    script = patent_summarizer.summarize_text(text, pdf_file, output_file + '.txt')