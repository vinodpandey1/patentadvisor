import fitz  # PyMuPDF for PDF reading
from transformers import T5Tokenizer, T5ForConditionalGeneration

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    """
    text = ""
    try:
        with fitz.open(pdf_path) as pdf:
            for page_num in range(len(pdf)):
                text += pdf[page_num].get_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def generate_summary(text, model, tokenizer, max_input_length=10000, max_output_length=1000):
    """
    Generates an abstractive summary using a T5 model.
    """
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=max_input_length, truncation=True)
    outputs = model.generate(inputs, max_length=max_output_length, min_length=400, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary

def summarize_in_chunks(text, model, tokenizer, chunk_size=10000, max_output_length=1000):
    """
    Summarizes a large text in chunks and combines the summaries.
    """
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    chunk_summaries = []
    
    for i, chunk in enumerate(chunks):
        print(f"Summarizing chunk {i + 1}/{len(chunks)}...")
        summary = generate_summary(chunk, model, tokenizer, max_input_length=chunk_size, max_output_length=max_output_length)
        chunk_summaries.append(summary)
    
    # Combine chunk summaries for final summarization
    combined_text = " ".join(chunk_summaries)
    final_summary = generate_summary(combined_text, model, tokenizer, max_input_length=10000, max_output_length=1000)
    return final_summary

# Main execution
if __name__ == "__main__":
    # Load the pre-trained T5 model and tokenizer
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    
    pdf_path = "/Users/amitarora/workspace/poc-workspace/patentadvisor/patent-service/dataset/documents/AI_PATENT/US8874431.pdf"  # Path to your PDF file
    text = extract_text_from_pdf(pdf_path)
    
    if text:
        print("Processing hierarchical summarization...")
        final_summary = summarize_in_chunks(text, model, tokenizer, chunk_size=10000)
        
        print("\nFinal Summary:")
        print(final_summary)
    else:
        print("No text extracted from the PDF.")