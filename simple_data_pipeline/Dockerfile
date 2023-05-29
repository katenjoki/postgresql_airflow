FROM python:3.9.1

RUN pip install pandas sqlalchemy psycopg2 
RUN apt-get install wget

WORKDIR /app

COPY ingest_agri_data.py ingest_agri_data.py  

ENTRYPOINT [ "python","ingest_agri_data.py" ]
