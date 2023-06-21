FROM python:3.10
WORKDIR /search_engine
COPY . /search_engine
RUN mkdir -p /usr/local/nltk_data/
COPY corpora /usr/local/nltk_data/corpora
RUN pip install -r requirements.txt
RUN mkdir /volume /logs
RUN export PATH=$PATH:/search_engine

#CMD python main.py
ENTRYPOINT ["python", "main.py"]