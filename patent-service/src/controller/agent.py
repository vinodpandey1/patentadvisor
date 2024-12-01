import os
import requests
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.tools import tool

from dotenv import load_dotenv

from src import constants as const
from src.utils import logger

load_dotenv()
ADVISOR_URL = os.getenv("AI_ADVISOR_END_POINT_URL")


@tool
def get_summary_of_patent(patent_name: str) -> str:
    """Fetches the summary of patent pdf file. Take the name of pdf and use it to get the summary present in
    system"""
    url = ADVISOR_URL + const.PATENT_SUMMARY_URL + patent_name
    logger.info(f"Invoking Summary tool for getting summary of patent {patent_name} from url - {url}")
    res = requests.get(url)
    if res.status_code == 200:
        return res.text  # Process and return the API response
    else:
        return f"Error: {res.status_code} - {res.text}"


@tool
def get_audio_url_of_patent(patent_name: str) -> str:
    """Fetches the audio or audio summary of patent. Take the name of patent and use it to get the audio url
    present in the system. If audio url is not present, return 'No Audio present in system' as response"""
    url = ADVISOR_URL + const.PATENT_AUDIO_URL + patent_name
    logger.info(f"Invoking Audio tool for getting audio url of patent {patent_name} from url - {url}")
    res = requests.get(url)
    if res.status_code == 200:
        return res.text  # Process and return the API response
    else:
        return f"Error: {res.status_code} - {res.text}"


@tool
def get_podcast_url_of_patent(patent_name: str) -> str:
    """Fetches the podcast of patent. Take the name of patent and use it to get the podcast url
    present in the system. If podcast url is not present, return 'No Audio present in system' as response"""
    url = ADVISOR_URL + const.PATENT_PODCAST_URL + patent_name
    logger.info(f"Invoking Podcast tool for getting podcast url of patent {patent_name} from url - {url}")
    res = requests.get(url)
    if res.status_code == 200:
        return res.text  # Process and return the API response
    else:
        return f"Error: {res.status_code} - {res.text}"


'''llm = OpenAI(temperature=0)
# Create the agent with the tool
tools = [get_summary_of_patent, get_audio_url_of_patent, get_podcast_url_of_patent]
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
print(agent.run("Get the podcast url of patent US11431660"))'''
