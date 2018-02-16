"""
Python script to download bhav copy from BSE and store it in redis.
"""

import ast
import datetime as dt
import io
import os
import zipfile

import pandas as pd
import redis
import requests


redis_url = os.environ.get("REDIS_URL")
redis_client = redis.from_url(redis_url, decode_responses=True)


def get_bhav_file(date):
    year = str(date.year)[2:]
    identifier = '%02d%02d%02s' % (date.day, date.month, year)
    bhav_url = 'https://www.bseindia.com/download/BhavCopy/Equity/EQ{}_CSV.ZIP'.format(identifier)

    response = requests.get(bhav_url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    zip_file.extractall()

    file_name = 'EQ{}.CSV'.format(identifier)
    return file_name


def dump_bhav_data(file_name):
    df = pd.read_csv(file_name, index_col=['SC_NAME'])
    df['NAME'] = df.index
    df = df[['NAME', 'SC_CODE', 'OPEN', 'HIGH', 'LOW', 'CLOSE']]
    data = {index.strip(): data.tolist() for index, data in df.iterrows()}
    redis_client.mset(data)


def filter_bhav_data(pattern):
    keys = redis_client.keys(pattern)
    data = redis_client.mget(keys)
    data = [ast.literal_eval(row) for row in data]
    return data


def dump_sample_data():
    now = dt.datetime.now()
    date = now.date() - dt.timedelta(days=2)
    print('Downloading file. Please wait...')
    file_name = get_bhav_file(date)
    dump_bhav_data(file_name)


if __name__ == "__main__":
    dump_sample_data()
