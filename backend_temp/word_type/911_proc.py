import pandas as pd
import time

from sequence_utils import *
from lane_utils import *

TOWNS = ["LOWER MERION", "ABINGTON", "NORRISTOWN", "UPPER MERION", "CHELTENHAM"]
TOWNS += ["POTTSTOWN", "UPPER MORELAND", "LOWER PROVIDENCE", "PLYMOUTH", "UPPER DUBLIN"]

CALL_TYPES = ["EMS", "Traffic", "Fire"]

# TOWNS = ["UPPER MERION"]
# CALL_TYPES = ["EMS", "Traffic", "Fire"]

def compute_lane_time(df, key="timestamp", delta=1):

    lane_last = [pd.Timedelta(0)]

    for i in range(1, delta):
        lane_last.append(df[key][i]-df[key][0])

    for i in range(delta, len(df)):
        lane_last.append(df[key][i]-df[key][i-delta])

    lane_next = lane_last.copy()
    lane_next = lane_next[delta:]

    for i in range(len(df)-delta, len(df)):
        lane_next.append(df[key][len(df)-1] - df[key][i])

    df["last"] = [round(diff.total_seconds()/60) for diff in lane_last]
    df["next"] = [round(diff.total_seconds()/60) for diff in lane_next]

    return df

    # df_town["last"] = df_town["timestamp"].diff()
    # df_town["last"] = df_town["last"].dt.seconds.fillna(0)
    #
    # df_town["next"] = df_town["timestamp"].shift(-1) - df_town["timestamp"]
    # df_town["next"] = df_town["next"].dt.seconds.fillna(0)
    #
    # df_town["last"] = (df_town["last"]/60).apply(round)
    # df_town["next"] = (df_town["next"]/60).apply(round)
    #
    # df_town[df_town["last"] > 262800] = 0
    # df_town[df_town["next"] > 262800] = 0



def compute_lane_geo(df, lat="lat", lon="lng", delta=1):
    distances = []

    for index, row in df[1:].iterrows():
        prev_row = df.iloc[index-1]
        distance = ((row["lat"]-prev_row["lat"])**2+(row["lng"]-prev_row["lng"])**2)**0.5
        distances.append(distance)

    last = [0]+distances
    next = distances+[0]

    df["last"] = last
    df["next"] = next

    return df

if __name__ == '__main__':
    df = pd.read_csv("911/911.csv")

    split_cat_df = df["title"].str.split(pat=": ", n=2, expand=True)
    df.drop(columns=["title", "e"], inplace=True)
    df = pd.concat([df, split_cat_df], axis=1)

    df.rename(columns={"timeStamp": "timestamp", 0: "cat", 1: "title"}, inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # # We'll only look at 2016 data
    # df = df[(df['timestamp'] >= '2016-01-01') & (df['timestamp'] < '2017-01-01')]
    # # We'll only look at the Dec Jan data
    # df = df[(df['timestamp'].dt.month == 12) & (df['timestamp'].dt.day >= 23) | (df['timestamp'].dt.month == 1) & (df['timestamp'].dt.day <= 5)]
    # Only look at weekdays
    # df = df[df['timestamp'].dt.dayofweek.isin(list(range(0, 5)))]
    # Look at specific times of the day
    # df = df[(df['timestamp'].dt.hour >= 16) & (df['timestamp'].dt.hour < 24)]
    # Select christmas day
    df = df[df['timestamp'].dt.month.isin([9, 10, 11])]

    df.sort_values("timestamp", inplace=True, ignore_index=True)

    for town in TOWNS:
        #for call_type in CALL_TYPES:
        for delta in range(1, 11):
            #df_town = df[(df["twp"] == town) & (df["cat"] == call_type)].copy()
            df_town = df[df["twp"] == town].copy()

            df_town.reset_index(inplace=True)

            df_town = compute_lane_time(df_town, delta=delta)

            df_town["last"][df_town["last"] > 43200] = 0
            df_town["next"][df_town["next"] > 43200] = 0

            # pd.options.mode.chained_assignment = None
            df_town['cumsum'] = range(1, len(df_town) + 1)
            # pd.options.mode.chained_assignment = "warn"

            #print(town, call_type, str(len(df_town)))
            # Plot cumulative line chart
            # plt.plot(df_town['timestamp'], df_town['cumsum'])
            # plt.show()

            #df_town = df_town.groupby(["last", "next"]).size().reset_index(name='count')

            # lane_hist(df_town, title=town+"_"+call_type, scale="log", nbins=100, to_file=False)
            # lane_hist(df_town, title=town+"_"+call_type, nbins=100, to_file=False)
            lane_hist(df_town, scale="log", file="fal_"+town+"_log_delta_"+str(delta), nbins=100, to_file=True)
            lane_hist(df_town, file="fal_"+town+"_lin_delta_"+str(delta), nbins=100, to_file=True)
            #lane_chart(df_town, title=town + "_" + call_type, min_lane=0, max_lane=1000, scale="log")
            # lane_chart(df_town, title=town+"_"+call_type, color="count", min_lane=0, max_lane=1000)#, size="count")
            #lane_chart(df_town, title=town+"_"+call_type+"_log", color="count", min_lane=0, max_lane=1000, scale="log")#, size="count")
        pass
    pass