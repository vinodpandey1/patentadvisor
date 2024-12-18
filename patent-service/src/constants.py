import os

ROOT_DIR = os.path.abspath(os.curdir)
CONFIG_DIR = ROOT_DIR + "/config"
OUTPUT_DIR=ROOT_DIR + "/output"
DATASET_DIR=ROOT_DIR + "/dataset"
INPUT_PATENT_DIR_PATH=ROOT_DIR + "/dataset/documents"

CLEARML_PROJECT="ai-patent-advisor"
SUMMARISATION_TASK="patent-summarizer"
PODCAST_GEN_TASK="patent-podcast-generator"
AUDIO_GEN_TASK="audio-generator"

DOC_COLLECTION="documents"
META_COLLECTION="patentdocuments"
DOC_CHUNK_COLLECTION="patentdocumentdetail"

PATENT_SUMMARY_URL = "/patent/summary/"
PATENT_AUDIO_URL = "/patent/audio/"
PATENT_PODCAST_URL = "/patent/podcast/"
PATENT_IMAGE_URL = "/patent/images/"
PATENT_QA_URL = "/queryDocument/"

##python3 -m spacy download en_core_web_sm