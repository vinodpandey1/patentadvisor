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


def main():
    print(BiasAnalyser.analyze_sentiment_and_bias("A method and apparatus for automated general understanding of the meaning of words and phrases in a natural language, including machine translation of human languages, Voice recognition technology, search, retrieval and text mining systems, and artificial intelligence applications, require automated understanding of natural lan guage in order to be fully effective. The method and apparatus of the present invention provide automated general understanding of the meaning of words and phrases in a natural language, including machine translation of human languages, voice recognition technology, search, retrieval and text mining systems, and artificial intelligence applications, without the need for extensive human intervention or editing. The method and apparatus of the present invention provide automated general understanding of the meaning of words and phrases in a natural language, including machine translation of human languages, voice recognition technology, search, retrieval and text mining systems, and artificial intelligence applications."))

if __name__ == "__main__":
    main()