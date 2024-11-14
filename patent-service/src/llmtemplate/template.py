from langchain_core.prompts import PromptTemplate

# Define the prompt for metadata extraction
  
# find out the Domain, Industry, Business Line, Application Area, Sector from title and abstract of patent
#and calculate Patent Duration by substracting grant date from current system date
# find out all these information of patent from first two pages of file
metadataprompt = """
    Extract the following metadata from the patent text:
    1. Patent Number
    2. Application Number
    3. Filing Date
    4. Grant Date
    5. Publication Date
    6. Title
    7. Abstract
    8. Inventor(s)
    9. Assignee(s)
    10. Claims
    11. Country of Filing
    12. Patent Authority
    13. Domain
    14. Industry
    15. Business Line
    16. Application Area
    17. Sector
    18. Legal Status
    19. Provisional Application Date
    20. Technology Keywords
    21. Abstract Summary
    22. Assignee Type
    23. Market Relevance Indicators

    find out all these information from first two pages of patent
    and some information like Domain, Industry, Business Line, Application Area, Sector from title and abstract of patent
    Abstract Summary:= Extract Abstract from patent and summarized into 15 words

    Text:
    {content}  # Limit input to first 4000 characters if it's long (due to token limits)
    """
    
METADATA_PROMPT_TEMPLATE =    PromptTemplate(input_variables=["content"], template=metadataprompt)
