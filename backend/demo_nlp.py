from textblob import TextBlob
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import spacy

# Ensure NLTK data (vader) is downloaded
try:
    nltk.download('vader_lexicon', quiet=True)
except Exception:
    pass

def test_nlp_capabilities():
    text = "The Federal Reserve's decision to increase interest rates by 25 basis points has caused some volatility in the market, but general sentiment remains optimistic for long-term growth in the tech sector."
    
    # 1. TextBlob Sentiment
    blob = TextBlob(text)
    print(f"--- TextBlob Analysis ---")
    print(f"Polarity: {blob.sentiment.polarity:.2f}")
    print(f"Subjectivity: {blob.sentiment.subjectivity:.2f}\n")
    
    # 2. NLTK VADER Sentiment
    try:
        sid = SentimentIntensityAnalyzer()
        scores = sid.polarity_scores(text)
        print(f"--- NLTK VADER Analysis ---")
        print(f"Scores: {scores}\n")
    except Exception as e:
        print(f"NLTK VADER not available: {e}\n")
        
    # 3. spaCy Named Entity Recognition (Basic)
    try:
        nlp = spacy.blank("en")
        # Just an example of loading custom NLP or blank for now
        print(f"--- spaCy Analysis ---")
        doc = nlp(text)
        print(f"Tokens: {[token.text for token in doc[:10]]}...\n")
    except Exception as e:
        print(f"spaCy not initialized correctly: {e}\n")

if __name__ == "__main__":
    test_nlp_capabilities()
