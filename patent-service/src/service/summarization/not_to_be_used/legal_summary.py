from transformers import pipeline
from pypdf import PdfReader
import os
from openai import OpenAI
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pdfplumber
#from transformers import BartTokenizer, BartForConditionalGeneration

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import PyPDFLoader


class PdfSummarizer:
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.llm = OpenAI()
        model_name = "facebook/bart-large"
        #model_name="t5-large"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.base_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        #self.summarizer = pipeline("summarization", framework='pt')
        #self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn", framework='pt')
        #self.summarizer = AutoModelForSeq2SeqLM.from_pretrained("philschmid/bart-large-cnn-samsum")
        
    def validate_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The File '{file_path}' does not exist.")
        if not file_path.endswith(".pdf"):
            raise ValueError(f"The file is '{file_path}' not pdf file")        
    
    def summarize_pdf(self, file_path):
        self.validate_file(file_path)
        summary = ""
        try:
            #pdf_reader = PyPDFLoader(file_path) 
            #text = "" 
            #for page_num in range(len(pdf_reader.pages)): 
                #if page_num > 0:
                    #page = pdf_reader.pages[page_num] 
                    #text += page.extract_text()
            #text = ""
            #with pdfplumber.open(file_path) as pdf:
                #for i in range(len(pdf.pages)):
                    #page = pdf.pages[i]  
                    #text += page.extract_text()    
            #print(text)     
            #with pdfplumber.open(file_path) as pdf:
                #for i in range(len(pdf.pages)):
                    #if i > 0:
                        #page = pdf.pages[i]  
                        #text += page.extract_text()      
            # Load the pretrained BART model and tokenizer.
            #model = BartForConditionalGeneration.from_pretrained('sshleifer/distilbart-cnn-12-6')
            #tokenizer = BartTokenizer.from_pretrained('sshleifer/distilbart-cnn-12-6')

            # Tokenize the extracted text.
            #inputs = tokenizer([text], truncation=True, return_tensors='pt')

            # Generate a summary.
            #summary_ids = model.generate(inputs['input_ids'], num_beams=4, early_stopping=True, min_length=1000, max_length=10000) 
            #summarized_text = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in summary_ids]
            
            loader = PyPDFLoader(file_path)
            docs = loader.load_and_split()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
            texts = text_splitter.split_documents(docs)
            final_texts = ""
            for text in texts:
                final_texts = final_texts + text.page_content
                
            pipe_sum = pipeline(
                'summarization',
                model=self.base_model,
                tokenizer=self.tokenizer,
                min_length=50,
                truncation=True,
                max_length=8000,
                device=self.device
            )
            result = pipe_sum(text)
            result = result[0]['summary_text']
            #chain = load_summarize_chain(self.llm, chain_type="map_reduce")
            #summary = chain.run(docs)   
            print(result)
        except Exception as error:
            print(f"Error in summarizing the pdf file {file_path}",  type(error).__name__, "--", error)
            raise error
        return summary
    
def main():
    pdf_summarizer = PdfSummarizer()
    summary = pdf_summarizer.summarize_pdf("/Users/amitarora/workspace/poc-workspace/patentadvisor/patent-service/dataset/documents/AI_PATENT/US8874431.pdf")
    #summary = pdf_summarizer.summarize_pdf("/Users/amitarora/Downloads/e-EPIC_IBF0719369.pdf")
    print(summary)
        
if __name__ == "__main__":
    main()
        
        