from langchain.chains.query_constructor.base import AttributeInfo
metadata_field_info = [
    AttributeInfo(
        name= "PatentNumber",
        description= "The unique identifier for the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "ApplicationNumber",
        description= "The application number for the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "FilingDate",
        description= "The date when the patent application was filed",
        type= "date"
    ),
    AttributeInfo(
        name= "GrantDate",
        description= "The date when the patent was granted",
        type= "date"
    ),
    AttributeInfo(
        name= "PublicationDate",
        description= "The date when the patent was published",
        type= "date"
    ),
    AttributeInfo(
        name= "Title",
        description= "The title of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "Abstract",
        description= "A summary of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "Inventor(s)",
        description= "The inventor(s) of the patent",
        type= "list"
    ),
    AttributeInfo(
        name= "Assignee(s)",
        description= "The assignee(s) of the patent",
        type= "list"
    ),
    AttributeInfo(
        name= "Claims",
        description= "The number of claims and drawing sheets of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "CountryOfFiling",
        description= "The country where the patent was filed",
        type= "string"
    ),
    AttributeInfo(
        name= "PatentAuthority",
        description= "The patent authority responsible for granting the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "Domain",
        description= "The domain or field of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "Industry",
        description= "The industry related to the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "BusinessLine",
        description= "The business line related to the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "ApplicationArea",
        description= "The application area of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "Sector",
        description= "The sector of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "LegalStatus",
        description= "The legal status of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "ProvisionalApplicationDate",
        description= "The date of the provisional patent application",
        type= "date"
    ),
    AttributeInfo(
        name= "TechnologyKeywords",
        description= "Keywords related to the technology of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "AssigneeType",
        description= "The type of assignee(s) of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "MarketRelevanceIndicators",
        description= "Indicators of market relevance for the patent",
        type= "string"
    )
]

