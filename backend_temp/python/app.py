import pandas as pd
import random
from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS
from data_processing.dataService import DataService
from data_processing.wiki_history_helper import (
    get_page_with_max_edits,
    get_user_with_max_edits,
    add_is_reverted,
)
from tqdm import tqdm

filename = "./backend_temp/raw_data/diffBy=size,sliceBy=page_name.csv"

# check file extension
sep = ","
columns = None
if filename.split(".")[-1] == "tsv":
    sep = "\t"
    columns = open(
        "backend_temp/raw_data/2023-10.enwiki.2023-10_columns.txt", "r"
    ).readlines()
    columns = list(line.split("\n")[0] for line in columns)

p = 1  # fraction of the data/
# if random from [0,1] interval is greater than p the row will be skipped
random.seed(4)

df = pd.read_csv(
    filename,
    # header=0,
    skiprows=lambda i: i > 0 and random.random() > p,
    # skiprows = lambda i : i > 1000,
    on_bad_lines="skip",
    sep=sep,
    # dtype={
    #     "event_user_id": str,
    #     "page_id": str,
    #     "user_id": str,
    #     "revision_id": str,
    #     "revision_parent_id": str,
    #     "revision_first_identity_reverting_revision_id": str,
    # },
    names=columns,
)
app = Flask(__name__)
CORS(app)

ds = DataService(df, {"timestamp": "dateTime"}, fileName=filename)
ds.split_time("timestamp")
# ds.add_time_till_event("2016-11-08 00:00:00", "time_till_election", "time_stamp")
# add_is_reverted(ds.df, "is_reverted")


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
    return df.to_json(orient="values")


# set nullColumnName
@app.route(f"/get-data")
def get_data():
    # extract arguments from request
    filterCol = request.args.get("filterColumn")
    filterVal = request.args.get("filterValue")

    attributes = request.args.get("attributes").split(",")
    return ds.get_eq_filtered_data(attributes, filterCol, filterVal)


@app.route(f"/filters", methods=["POST"])
def get_filter_values():
    filterMap = request.get_json()
    return ds.get_filter_values(filterMap)


@app.route(f"/get-diff-list")
def get_diff_list():
    fieldName = request.args.get("fieldName")
    linearizeBy = request.args.get("linearizeBy")
    relative = request.args.get("relative")
    out = ds.get_diff_list(fieldName, linearizeBy, relative)
    return out


@app.route(f"/add-diff-list")
def add_diff_list():
    fieldName = request.args.get("fieldName").split(",")[0]
    linearizeBy = request.args.get("linearizeBy")
    sliceBy = request.args.get("sliceBy")
    relative = request.args.get("relative", type=bool, default=False)
    diffList = []
    distinctValues = list(df[sliceBy].unique())
    for val in tqdm(distinctValues, desc="Computing diffs"):
        filteredDf = ds.get_filtered_df(sliceBy, val, ds.df)
        diffList += ds.get_diff_list(fieldName, linearizeBy, relative, filteredDf)
    [nextCol, prevCol] = ds.get_diff_col_names(relative)
    prevFieldName = "_".join([prevCol, fieldName])
    prevValues = list(map(lambda x: [x["unique_id"], x[prevCol]], diffList))
    nextFieldName = "_".join([nextCol, fieldName])
    nextValues = list(map(lambda x: [x["unique_id"], x[nextCol]], diffList))
    ds.add_values_by_id(prevFieldName, prevValues)
    ds.add_values_by_id(nextFieldName, nextValues)
    print(ds.df)
    ds.df.to_csv("diffBy=" + fieldName + ",sliceBy=" + sliceBy + ".csv", sep=",")
    return jsonify(diffList)


@app.route(f"/get-human-readable-name")
def get_human_readable_name():
    fieldName = request.args.get("fieldName")
    fieldValue = request.args.get("fieldValue")
    res = {
        "fieldName": fieldName,
        "fieldValue": fieldValue,
        "humanReadableName": ds.get_human_readable_name(fieldName, fieldValue),
    }
    return jsonify(res)


@app.route(f"/get-adjacent-event-ids")
def get_adjacent_event_ids():
    linearizeBy = request.args.get("linearizeBy")
    sliceByField = request.args.get("sliceByField")
    sliceByValue = request.args.get("sliceByValue")
    eventIdField = request.args.get("eventIdField")
    currentId = request.args.get("currentId")
    return ds.get_adjacent_event_ids(
        linearizeBy, sliceByField, sliceByValue, eventIdField, currentId
    )


if __name__ == "__main__":
    app.run(debug=False)
