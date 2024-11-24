from langchain.chains.query_constructor.base import AttributeInfo
metadata_field_info = [
    AttributeInfo(
        name= "patentNumber",
        description= "The unique identifier for the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "applicationNumber",
        description= "The application number for the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "filingDate",
        description= "The date when the patent application was filed",
        type= "date"
    ),
    AttributeInfo(
        name= "grantDate",
        description= "The date when the patent was granted",
        type= "date"
    ),
    AttributeInfo(
        name= "publicationDate",
        description= "The date when the patent was published",
        type= "date"
    ),
    AttributeInfo(
        name= "title",
        description= "The title of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "abstract",
        description= "A summary of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "inventors",
        description= "The inventor(s) of the patent",
        type= "list"
    ),
    AttributeInfo(
        name= "assignees",
        description= "The assignee(s) of the patent",
        type= "list"
    ),
    AttributeInfo(
        name= "claims",
        description= "The number of claims and drawing sheets of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "countryOfFiling",
        description= "The country where the patent was filed",
        type= "string"
    ),
    AttributeInfo(
        name= "patentAuthority",
        description= "The patent authority responsible for granting the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "domain",
        description= "The domain or field of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "industry",
        description= "The industry related to the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "businessLine",
        description= "The business line related to the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "applicationArea",
        description= "The application area of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "sector",
        description= "The sector of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "legalStatus",
        description= "The legal status of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "provisionalApplicationDate",
        description= "The date of the provisional patent application",
        type= "date"
    ),
    AttributeInfo(
        name= "technologyKeywords",
        description= "Keywords related to the technology of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "assigneeType",
        description= "The type of assignee(s) of the patent",
        type= "string"
    ),
    AttributeInfo(
        name= "marketRelevanceIndicators",
        description= "Indicators of market relevance for the patent",
        type= "string"
    )
]

