import os
from time import time
import argparse
import numpy as np
import pandas as pd
import datetime as dt

#create a connection to postgresql
import psycopg2
from sqlalchemy import create_engine

def convert_string_to_int(value):
    return int(value.replace(',', ''))

def ingest_data_to_postgresql(user,password,host,port,db,file_csv,year):

    #create dictionary with the years and urls
    #create dictionary with the years and urls of the maize data
    file_path = file_csv
    table = f'Horticulture_{year}'

    print('---------------------------------------')
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    engine.connect()

    ###TRANSFORMING THE DATA
    data = pd.read_csv(file_path)
    if year == '2017':
        #clean data
        data[['Value (Ksh)','Production (MT)','Area (HA)']] = data[['Value (Ksh)','Production (MT)','Area (HA)']].applymap(convert_string_to_int)
        data['Yield (MT/HA)'] = data['Production (MT)'] / data['Area (HA)']
    else:
        #clean data
        data.rename(columns={'COUNTY':'County'},inplace=True)
        data[['Value (KShs)','Quantity (Ton)','Area (Ha)']] = data[['Value (KShs)','Quantity (Ton)','Area (Ha)']].applymap(convert_string_to_int)
        data['Yield (Ton/Ha)'] = data['Quantity (Ton)'] / data['Area (Ha)']
    #make all counties uppercase
    data['County'] = data['County'].str.upper()
    #add features to the data
    data['Year'] = year
    data['Year'] = pd.to_datetime(data['Year'],format='%Y').dt.year
    start_time=time()
    data.to_sql(name=table, con=engine, if_exists='replace')
    end_time=time()
    print(f"Finished ingesting {year} data into the postgres database: took %.3f second" % (end_time - start_time))
    print('----------------------------------------')


