FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && python -m spacy download en_core_web_sm \
 && python -m nltk.downloader vader_lexicon punkt punkt_tab wordnet stopwords averaged_perceptron_tagger
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
