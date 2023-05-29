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

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db

    #create dictionary with the years and urls, for maize 2017 and 2018 data
    years_dict = dict()
    years_dict['2017'] = 'http://kilimodata.org/datastore/dump/63fa57a5-a7c2-40e1-a728-f9546fa383ef?bom=True'
    years_dict['2018'] = 'http://kilimodata.org/datastore/dump/e1a72ec2-e347-4264-8ac9-d4ec3659610a?bom=True'

    #loop the dictionary
    for year,url in years_dict.items():
        file_path = f'maize_{year}.csv'
        table = f'maize_{year}'

        ###EXTRACTING DATA
        print(f'Downloading {year} data')
        os.system(f'wget --no-check-certificate {url} -O {file_path}')
        print('---------------------------------------')
        engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
        engine.connect()
        print(f'Uploading {year} data to postgres...')

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

if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Ingest csv data into postgres')

    #user, password, host, port, DB name, table name, url of the csv file

    parser.add_argument('--user',help='username for postgres')
    parser.add_argument('--password',help='password for postgres')
    parser.add_argument('--host',help='hostname for postgres')
    parser.add_argument('--port',help='port for postgres')
    parser.add_argument('--db',help='DB name for postgres')

    args = parser.parse_args()

    main(args)

