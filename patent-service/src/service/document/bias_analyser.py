from textblob import TextBlob


class BiasAnalyser:

    @staticmethod
    def analyze_sentiment_and_bias(text):
        sentiment = TextBlob(text).sentiment
        bias_indicators = {
            "gendered_terms": ["he", "she", "man", "woman"],
            "political_terms": ["liberal", "conservative", "progressive", "republican", "democrat"],
            "racial_terms": ["black", "white", "asian", "hispanic"]
        }
        detected_biases = {category: [term for term in terms if term in text.lower()]
                           for category, terms in bias_indicators.items()}

        return {
            "sentiment": {"polarity": sentiment.polarity, "subjectivity": sentiment.subjectivity},
            "biases_detected": detected_biases
        }
