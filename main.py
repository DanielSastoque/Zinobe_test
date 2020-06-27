""" Challenge Python L1 - Zinobe Test """

import requests
import hashlib
import time
import sqlite3
import os

import pandas as pd

__author__ = "Jose Daniel Sastoque Buitrago"
__email__ = "jdsastoqueb@correo.udistrital.edu.co"


# --------------------------- Get all regions ----------------------------------

url = "https://restcountries-v1.p.rapidapi.com/all"

headers = {
    'x-rapidapi-host': "restcountries-v1.p.rapidapi.com",
    'x-rapidapi-key': os.environ.get('API_KEY')
    }

response = requests.request("GET", url, headers=headers)
regions = pd.read_json(response.text)["region"].unique().tolist()
regions.remove("")


# -------------------------- Building the rows ---------------------------------

data = {"Region": regions,
        "Country_Name": [],
        "Language": [],
        "Time": []}

for region in regions:
    t = time.time()

    url = f"https://restcountries.eu/rest/v2/region/{region}"
    response = requests.request("GET", url, headers=headers)
    country_name = pd.read_json(response.text)["name"][0]
    data["Country_Name"].append(country_name)

    url = f"https://restcountries.eu/rest/v2/name/{country_name}"
    response = requests.request("GET", url, headers=headers)
    language = pd.read_json(response.text)["languages"][0][0]["name"]
    data["Language"].append(
        hashlib.sha1(language.encode()).hexdigest().upper())

    data["Time"].append(time.time() - t)


# -------------------------- Save as dataframe ---------------------------------

data_df = pd.DataFrame.from_dict(data)
time_series = data_df["Time"]


# --------------------------  Print statistics ---------------------------------

print("Total time: {}\n\
Mean  time: {}\n\
Max   time: {}".format(time_series.sum(), time_series.mean(), 
                       time_series.max()))


# -------------------------- Save to sqlite db ---------------------------------

conn = sqlite3.connect('result_db.db')
c = conn.cursor()
data_df.to_sql(name='results', con=conn, if_exists="replace")


# ---------------------------- Save to json ------------------------------------

data_df.to_json("data.json")
