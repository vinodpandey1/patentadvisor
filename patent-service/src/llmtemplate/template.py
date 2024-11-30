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
    Remove space in attribute name 
    Attribute name should be in camel case
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

METADATA_PROMPT_TEMPLATE = PromptTemplate(input_variables=["content"], template=metadataprompt)

METADATAINFO_PROMPT_TEMPLATE = PromptTemplate(input_variables=["content"], template=medatainfo)

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

IMAGE_SUMMARY_PROMPT = '''Read the image carefully,to  write a short description for each block, and summarize the functionality depicted in the image in less than 50 words. Show output in the following format:
                    Image name:
                    Summary:
                    Guidelines: Try to write in bullet points. Do not use * as markers.
                '''