import pandas as pd
import random
from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS
from data_processing.dataService import DataService

filename = "raw_data/2023-10.enwiki.2023-10.tsv"

#check file extension
sep = ","
if filename.split(".")[-1] == "tsv":
    sep = "\t"

p = 1  # fraction of the data/
# if random from [0,1] interval is greater than p the row will be skipped
random.seed(4)

df = pd.read_csv(
    filename,
    # header=0,
    skiprows=lambda i: i > 0 and random.random() > p,
    # skiprows = lambda i : i > 1000,
    on_bad_lines="skip",
    sep = sep
)
app = Flask(__name__)
CORS(app)

ds = DataService(df, {"Time": "dateTime"})

@app.route("/")
def hello_world():
    return "Hello world"


@app.route(f"/attributes")
def data_attributes():
    return jsonify(df.columns.tolist())


@app.route(f"/scales")
def data_scales():
    return (
        df.max(axis=0, numeric_only=True) - df.min(axis=0, numeric_only=True)
    ).to_json()


@app.route(f"/mins")
def data_mins():
    return (df.min(axis=0, numeric_only=True)).to_json()

@app.route(f"/preview")
def data_preview():
    return df.head(100).to_json(orient="values")