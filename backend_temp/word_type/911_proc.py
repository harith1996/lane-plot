import pandas as pd

from sequence_utils import *
from lane_utils import lane_chart, line_chart

TOWNS = ["LOWER MERION", "ABINGTON", "NORRISTOWN", "UPPER MERION", "CHELTENHAM"]
TOWNS += ["POTTSTOWN", "UPPER MORELAND", "LOWER PROVIDENCE", "PLYMOUTH", "UPPER DUBLIN"]

CALL_TYPES = ["EMS", "Traffic", "Fire"]

# TOWNS = ["UPPER MERION"]
# CALL_TYPES = ["Traffic"]

if __name__ == '__main__':
    df = pd.read_csv("911/911.csv")

    split_cat_df = df["title"].str.split(pat=": ", n=2, expand=True)
    df.drop(columns=["title", "e"], inplace=True)
    df = pd.concat([df, split_cat_df], axis=1)

    df.rename(columns={"timeStamp": "timestamp", 0: "cat", 1: "title"}, inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.sort_values("timestamp", inplace=True, ignore_index=True)

    for town in TOWNS:
        for call_type in CALL_TYPES:
            df_town = df[(df["twp"] == town) & (df["cat"] == call_type)]
            #df_town = df[(df["twp"] == town) & (df["cat"] == "VEHI")]

            df_town["last"] = df_town["timestamp"].diff()
            df_town["last"] = df_town["last"].dt.seconds.fillna(-1)

            df_town["next"] = df_town["timestamp"].shift(-1) - df_town["timestamp"]
            df_town["next"] = df_town["next"].dt.seconds.fillna(-1)

            df_town = df_town.groupby(["last", "next"]).size().reset_index(name='count')

            lane_chart(df_town, title=town+"_"+call_type, color="count", min_lane=0, max_lane=1000)#, size="count")
            #lane_chart(df_town, title=town+"_"+call_type+"_log", color="count", min_lane=0, max_lane=1000, scale="log")#, size="count")

    pass