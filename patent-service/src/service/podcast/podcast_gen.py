from typing import List, Literal, Tuple, Optional
from pydantic import BaseModel, ValidationError
from pypdf import PdfReader

from together import Together
from cartesia import Cartesia

import subprocess
import ffmpeg
import os

import logging
from logging import config

config.fileConfig("config/logging.conf")
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
    
    
# Adapted and modified from https://github.com/gabrielchua/open-notebooklm
PODCAST_PROMPT = """
You are a world-class podcast producer tasked with transforming the provided input text into an engaging and informative podcast script. The input may be unstructured or messy, sourced from PDFs or web pages. Your goal is to extract the most interesting and insightful content for a compelling podcast discussion.

# Steps to Follow:

1. **Analyze the Input:**
   Carefully examine the text, identifying key topics, points, and interesting facts or anecdotes that could drive an engaging podcast conversation. Disregard irrelevant information or formatting issues.

2. **Brainstorm Ideas:**
   In the `<scratchpad>`, creatively brainstorm ways to present the key points engagingly. Consider:
   - Analogies, storytelling techniques, or hypothetical scenarios to make content relatable
   - Ways to make complex topics accessible to a general audience
   - Thought-provoking questions to explore during the podcast
   - Creative approaches to fill any gaps in the information

3. **Craft the Dialogue:**
   Develop a natural, conversational flow between the host (Jane) and the guest speaker (the author or an expert on the topic). Incorporate:
   - The best ideas from your brainstorming session
   - Clear explanations of complex topics
   - An engaging and lively tone to captivate listeners
   - A balance of information and entertainment

   Rules for the dialogue:
   - The host (Jane) always initiates the conversation and interviews the guest
   - Include thoughtful questions from the host to guide the discussion
   - Incorporate natural speech patterns, including occasional verbal fillers (e.g., "Uhh", "Hmmm", "um," "well," "you know")
   - Allow for natural interruptions and back-and-forth between host and guest - this is very important to make the conversation feel authentic
   - Ensure the guest's responses are substantiated by the input text, avoiding unsupported claims
   - Maintain a PG-rated conversation appropriate for all audiences
   - Avoid any marketing or self-promotional content from the guest
   - The host concludes the conversation

4. **Summarize Key Insights:**
   Naturally weave a summary of key points into the closing part of the dialogue. This should feel like a casual conversation rather than a formal recap, reinforcing the main takeaways before signing off.

5. **Maintain Authenticity:**
   Throughout the script, strive for authenticity in the conversation. Include:
   - Moments of genuine curiosity or surprise from the host
   - Instances where the guest might briefly struggle to articulate a complex idea
   - Light-hearted moments or humor when appropriate
   - Brief personal anecdotes or examples that relate to the topic (within the bounds of the input text)

6. **Consider Pacing and Structure:**
   Ensure the dialogue has a natural ebb and flow:
   - Start with a strong hook to grab the listener's attention
   - Gradually build complexity as the conversation progresses
   - Include brief "breather" moments for listeners to absorb complex information
   - For complicated concepts, reasking similar questions framed from a different perspective is recommended
   - End on a high note, perhaps with a thought-provoking question or a call-to-action for listeners

IMPORTANT RULE: Each line of dialogue should be no more than 100 characters (e.g., can finish within 5-8 seconds)

Remember: Always reply in valid JSON format, without code blocks. Begin directly with the JSON output.
"""

class Podcast_Generator:
    
    def __init__(self):
        self.client_together = Together(api_key="xxxx")
        self.client_cartesia = Cartesia(api_key="xxx")

    def get_PDF_info(self, pdf_file : str):
        text = ''

        file_name = os.path.basename(pdf_file).split('/')[-1]
        file_tuple = os.path.splitext(file_name)
        
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

        return file_tuple[0], text

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
        
        temp_podcast_pcm = "dataset/podcast/podcast.pcm"
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
pdf_file = "dataset/documents/AI_PATENT/US9204102.pdf"
file_name_without_ext, text = podcast_gen.get_PDF_info(pdf_file)
output_file = 'dataset/podcast/'+file_name_without_ext
script = podcast_gen.generate_script(PODCAST_PROMPT, text, Script, pdf_file, output_file + '.txt')
podcast_gen.generate_podcast(script, output_file + '.wav', pdf_file)
