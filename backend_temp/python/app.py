import pandas as pd
import random
from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS
from data_processing.dataService import DataService
from data_processing.wiki_history_helper import get_page_with_max_edits

filename = "./backend_temp/raw_data/diff_revision_text_bytes.csv"

# check file extension
sep = ","
if filename.split(".")[-1] == "tsv":
    sep = "\t"

p = 1  # fraction of the data/
# if random from [0,1] interval is greater than p the row will be skipped
random.seed(4)

columns = open(
    "backend_temp/raw_data/2023-10.enwiki.2023-10_columns.txt", "r"
).readlines()
columns = list(line.split("\n")[0] for line in columns)

reader = pd.read_csv(
    filename,iterator=True,
    # header=0,
    skiprows=lambda i: i > 0 and random.random() > p,
    # skiprows = lambda i : i > 1000,
    on_bad_lines="skip",
    sep=sep,
    dtype={
        "event_user_id": str,
        "page_id": str,
        "user_id": str,
        "revision_id": str,
        "revision_parent_id": str,
        "revision_first_identity_reverting_revision_id": str
    }
    # names=columns,
)
df = reader.get_chunk(500)
app = Flask(__name__)
print(get_page_with_max_edits(df))
CORS(app)

ds = DataService(df, {"event_timestamp": "dateTime"})


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

@app.route(f"/get-diff-list")
def get_diff_list():
    fieldName = request.args.get("fieldName")
    linearOrderBy = request.args.get("linearOrderBy")
    out = ds.get_diff_list(fieldName, linearOrderBy)
    return out


@app.route(f"/add-diff-list")
def add_diff_list():
    fieldName = request.args.get("fieldName").split(",")[0]
    linearOrderBy = request.args.get("linearOrderBy")
    diffList = ds.get_diff_list(fieldName, linearOrderBy)
    prevFieldName = "_".join(["diffPrev", fieldName])
    prevValues = list(map(lambda x: [x["unique_id"], x["diffPrev"]], diffList))
    nextFieldName = "_".join(["diffNext", fieldName])
    nextValues = list(map(lambda x: [x["unique_id"], x["diffNext"]], diffList))
    ds.add_values_by_id(prevFieldName, prevValues)
    ds.add_values_by_id(nextFieldName, nextValues)
    print(ds.df)
    ds.df.to_csv('diff_' + fieldName + ".csv", sep=',')
    return jsonify(diffList)

if __name__ == "__main__":
    app.run(debug=False)
