import os
import requests
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.tools import tool

from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper

from src import constants as const
from src.utils import logger

load_dotenv()
ADVISOR_URL = os.getenv("AI_ADVISOR_END_POINT_URL")
search = SerpAPIWrapper(serpapi_api_key="17576ddc385538219c158a9116c1311ede86f31bf62a7bed9344471e30501a5b")


@tool
def get_summary_of_patent(userId: str, patentID: str, query: str) -> str:
    """Fetches the summary of patent pdf file. Take the patentID of pdf and use it to get the summary present in
    system"""
    url = ADVISOR_URL + const.PATENT_SUMMARY_URL + patentID
    logger.info(f"Invoking Summary tool for getting summary of patent {patentID} from url - {url}")
    res = requests.get(url)
    if res.status_code == 200:
        return res.text  # Process and return the API response
    else:
        return f"Error: {res.status_code} - {res.text}"


@tool
def get_audio_url_of_patent(userId: str, patentID: str, query: str) -> str:
    """Fetches the audio or audio summary of patent. Take the patentID of patent and use it to get the audio url
    present in the system. If audio url is not present, return 'No Audio present in system' as response"""
    url = ADVISOR_URL + const.PATENT_AUDIO_URL + patentID
    logger.info(f"Invoking Audio tool for getting audio url of patent {patentID} from url - {url}")
    res = requests.get(url)
    if res.status_code == 200:
        return res.text  # Process and return the API response
    else:
        return f"Error: {res.status_code} - {res.text}"


@tool
def get_podcast_url_of_patent(userId: str, patentID: str, query: str) -> str:
    """Fetches the podcast of patent. Take the patentID of patent and use it to get the podcast url
    present in the system. If podcast url is not present, return 'No Audio present in system' as response"""
    url = ADVISOR_URL + const.PATENT_PODCAST_URL + patentID
    logger.info(f"Invoking Podcast tool for getting podcast url of patent {patentID} from url - {url}")
    res = requests.get(url)
    if res.status_code == 200:
        return res.text  # Process and return the API response
    else:
        return f"Error: {res.status_code} - {res.text}"


@tool
def get_queries_of_patent(userId: str, patentID: str, query: str) -> str:
    """Find out the answers related to query raised by user related to patent present in
    patentID. Take the patentID of patent and user identified by userId and query
    and use it to get the answer to query. If you don't know answer, return 'No answer'"""
    url = ADVISOR_URL + const.PATENT_QA_URL + userId + "/" + patentID + "?query=" + query
    logger.info(f"Invoking QnA tool for getting answer to queries from url - {url}")
    res = requests.get(url)
    if res.status_code == 200:
        return res.text  # Process and return the API response
    else:
        return f"Error: {res.status_code} - {res.text}"


def get_ai_patent_advisor_agent():
    llm = OpenAI(temperature=0)
    tools = [get_queries_of_patent, get_summary_of_patent, get_audio_url_of_patent, get_podcast_url_of_patent]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    return agent


@tool
def search_internet(query: str) -> str:
    """Search the internet using Google. Provide a search query, and it will return relevant web results.
    Take the query and use it to get the answer from
    Google"""
    logger.info(f"Going to google for query {query}")
    return search.run(query)


def get_fallback_agent():
    llm = OpenAI(temperature=0.7)
    tools = [search_internet]
    logger.info("Invoking fallback agent")
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    return agent


def evaluate_response(response: str) -> bool:
    """
    Evaluates if the response from Agent A is adequate.
    Returns True if it's acceptable, False otherwise.
    """
    if "No answer" in response or "Internal Error" in response:
        return False
    return True

