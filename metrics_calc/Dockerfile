FROM python:3.10
WORKDIR /metrics_calc
COPY . /metrics_calc
RUN pip install -r requirements.txt
RUN mkdir /experiments_runs
RUN mkdir /config
RUN mkdir /volume /logs
RUN export PATH=$PATH:/metrics_calc

#CMD python3 main.py
ENTRYPOINT ["python", "main.py"]