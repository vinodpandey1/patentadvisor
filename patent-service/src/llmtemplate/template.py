from langchain_core.prompts import PromptTemplate

# Define the prompt for metadata extraction
  
# find out the Domain, Industry, Business Line, Application Area, Sector from title and abstract of patent
#and calculate Patent Duration by substracting grant date from current system date
# find out all these information of patent from first two pages of file
metadataprompt = """
    Extract the following metadata from the Text and provide it in JSON format.
    1.Patent Number
    2.Application Number
    3.Filing Date
    4.Grant Date
    5.Publication Date
    6.Title
    7.Abstract
    8.Inventors
    9.Assignees
    10.Claims
    11.Country of Filing
    12.Patent Authority
    13.Domain
    14.Industry
    15.Business Line
    16.Application Area
    17.Sector
    18.Legal Status
    19.Provisional Application Date
    20.Technology Keywords
    21.Assignee Type
    22.Market Relevance Indicators

    find out all these information from first two pages of patent
    and some information like Domain, Industry, Business Line, Application Area, Sector from title and abstract of patent
    Keep full value of Abstract and Claims
    Remove space in attribute name and make camel case
    Remove space between attribute name and colon(:) and between colon(:) and attribute value
    Remove trailing and leading spaces from attribute value
    keep date format as dd//mm/yyyy and type as date
    if not able to find any attribute then keep it as blank string and not null value
    Text:
    {content}  # Limit input to first 4000 characters if it's long (due to token limits)
    
    JSON Format:
    """

medatainfo = """
    Use patent document metadata provided in text Return a JSON list with an entry for each attribute in JSON Format. 
    Each entry should have 
    "name": "attribute name", "description": "attribute description", "type": "attribute data type"
    
    type can be "string", "integer", "date", "list", "boolean"
    Type for FilingDate, GrantDate, PublicationDate, ProvisionalApplicationDate should be "date"
    
    Text:
    {content}  
    
    JSON Format:   
"""

METADATA_PROMPT_TEMPLATE =    PromptTemplate(input_variables=["content"], template=metadataprompt)

METADATAINFO_PROMPT_TEMPLATE =    PromptTemplate(input_variables=["content"], template=medatainfo)  
