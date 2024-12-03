from textblob import TextBlob
from src.utils import logger

class BiasAnalyser:

    @staticmethod
    def analyze_sentiment_and_bias(text):
        sentiment = TextBlob(text).sentiment
        bias_indicators = {
            "gendered_terms": ["he", "she", "man", "woman"],
            "political_terms": ["liberal", "conservative", "progressive", "republican", "democrat"],
            "racial_terms": ["black", "white", "asian", "hispanic"]
        }
       
        text_lower = text.lower()
        contains_bias = any(term in text_lower for terms in bias_indicators.values() for term in terms)

        tokens = text_lower.split()
        
        detected_biases = {category: [term for term in terms if term in tokens]
                           for category, terms in bias_indicators.items()}

        return {
            "sentiment": {"polarity": sentiment.polarity, "subjectivity": sentiment.subjectivity},
            "biases_detected": detected_biases
        }
