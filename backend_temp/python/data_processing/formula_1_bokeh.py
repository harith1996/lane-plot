from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.transform import factor_cmap, linear_cmap
from bokeh.palettes import Viridis256, Viridis7
from bokeh.util.hex import hexbin
from bokeh.models import Scatter
from bokeh.core.properties import field

from scipy.signal import find_peaks
import pandas as pd
import numpy as np

from diffComputer import DiffComputer
from dataService import DataService
import fastf1
import ptvsd
import os


def distance_to_curve(df, session):
    # Calculate next curve to every point
    corners = session.get_circuit_info().corners
    corners = corners.rename({"Distance": "distance_to_curve"})
    df = pd.merge_asof(
        df.sort_values("distance_in_lap", axis=0),
        corners[["Number", "Distance", "Angle"]].sort_values(
            "Distance", ignore_index=True
        ),
        left_on="distance_in_lap",
        right_on="Distance",
        direction="forward",
    )
    return df


def find_minimum_speed_within_range(df, start_index, end_index):
    return df.loc[start_index:end_index, "Speed"].idxmin()


def delta_lane_abs(df, key="timestamp", delta=1, time_metric=False):
    """
    Computes the absolute delta lane last and next values from a given sequence
    :param df: A pandas DataFrame containing the sequence
    :param key: The name of the column being indexed
    :param delta: The delay introduced to calculate the values
    :return: The df parameter with the columns "last" and "next" filled with the corresponding LaNe values
    """
    if len(df) == 0:
        return df

    df = df.reset_index(drop=True)

    if time_metric:
        lane_last = [pd.Timedelta(seconds=0)]
    else:
        lane_last = [0]

    for i in range(1, delta):
        lane_last.append(df[key][0] - df[key][i])

    for i in range(delta, len(df)):
        lane_last.append(df[key][i - delta] - df[key][i])

    lane_next = [-val for val in lane_last]
    lane_next = lane_next[delta:]

    for i in range(len(df) - delta, len(df)):
        lane_next.append(df[key][len(df) - 1] - df[key][i])

    df["last"] = lane_last
    df["next"] = lane_next

    return df


def lane_max(df, session, key="RPM", nGear=None):
    df = df.sort_values("Date", axis=0).reset_index(drop=True)

    if len(df) == 0:
        return df

    # df = df.iloc[3000:4000].reset_index(drop=True)

    peaks = find_peaks(df["Speed"].values)[0]

    prev_peak = 0

    new_peaks = []
    for peak in peaks:
        if peak - prev_peak > 5:
            new_peaks.append(peak)
    peaks = new_peaks

    new_peaks = []
    min_points = []
    same_start_index = False
    for i in range(len(peaks) - 1):
        if not same_start_index:
            start_index = peaks[i]
        same_start_index = False

        end_index = peaks[i + 1]

        valley = find_minimum_speed_within_range(df, start_index, end_index)
        # if df.iloc[start_index]["Speed"] - df.iloc[valley]["Speed"] > 40 and valley - start_index > 5:
        if valley - start_index > 5:
            new_peaks.append(start_index)
            min_points.append(valley)
        else:
            same_start_index = True

    min_points = np.array(min_points)
    peaks = np.array(new_peaks)

    # Compute inflation points
    d2 = np.gradient(df["Speed"])

    infls_down = []
    infls_up = []
    start_max = True
    for i in range(len(min_points) * 2 - 1):
        i = i // 2
        #TODO: finding infls is basically find_peaks(gradient) & find_valleys(gradient). Rewrite this to use find_peaks and find_valleys 
        if start_max:
            start_index = peaks[i]
            end_index = min_points[i]

            infls_down.append(start_index + np.argmin(d2[start_index:end_index]))
        else:
            start_index = min_points[i]
            end_index = peaks[i + 1]

            if (
                start_index >= end_index or np.max(d2[start_index:end_index]) < -1000
            ):  # 25
                infls_up.append(-1)
                infls_up.append(start_index)
            else:
                infls_up.append(start_index + np.argmax(d2[start_index:end_index]))
        start_max = not start_max

    events = [
        item for pair in zip(peaks, infls_down, min_points, infls_up) for item in pair
    ]
    # events = [item for pair in zip(infls_down, infls_up) for item in pair]
    # events = [item for pair in zip(peaks, min_points) for item in pair]
    # events = [item for item in events if item >= 0]

    # line_chart_max(df, key=key, peaks=peaks, valleys=min_points, infls_down=infls_down, infls_up=infls_up)

    # line_chart_max(df, key=key, peaks=peaks, valleys=min_points, infls_down=infls_down, infls_up=infls_up,
    #                min_value=11000, max_value=12000)

    df_max = df.iloc[events]
    #why delta=2? because we want to compare peaks against valleys only. and inflection down against inflection up
    #TODO: How to frame this concept in the paper?
    df_max = delta_lane_abs(df_max, key=key, delta=2)

    point_type = ["max", "infl_down", "min", "infl_up"]
    df_max["point_type"] = (
        point_type * (len(df_max) // len(point_type))
        + point_type[: len(df_max) % len(point_type)]
    )

    # events = [item for pair in zip(events, infls) for item in pair]
    #
    # Select only inflation points
    # df_infl = delta_lane_abs(df.iloc[events], key=key)
    # df_infl = df_infl[df_infl["last"] * df_infl["next"] < 0]

    # df_max = pd.concat([df_max, df_infl])

    if nGear:
        df_max = df_max[df_max["nGear"] == nGear]

    return df_max


def is_wet_lap(lap):
    weather_data = lap.get_weather_data()
    if weather_data.Rainfall:
        return True
    else:
        return False


# attach to VS Code debugger if this script was run with BOKEH_VS_DEBUG=true
# (place this just before the code you're interested in)
if os.environ["BOKEH_VS_DEBUG"] == "true":
    # 5678 is the default attach port in the VS Code debug configurations
    print("Waiting for debugger attach")
    ptvsd.enable_attach(address=("localhost", 5678), redirect_output=True)
    ptvsd.wait_for_attach()

session = fastf1.get_session(2023, "British Grand Prix", "R")
session.load(telemetry=True)
fastest_lap = session.laps.pick_fastest()

fastest_tel = fastest_lap.get_telemetry()
fastest_tel["nGear"] = fastest_tel["nGear"].astype(str)
fastest_tel = fastest_tel.reset_index(drop=True)

drivers = session.drivers
all_tel = session.laps.pick_driver(drivers[0]).get_telemetry()
all_tel["nGear"] = all_tel["nGear"].astype(str)
all_tel = all_tel.reset_index(drop=True)

ds = DataService(all_tel, {"Speed": float})


lane_processed_df = lane_max(all_tel, session, key="Speed")
lane_processed_df['acceleration'] = np.gradient(lane_processed_df["Speed"])
lane_processed_df['isPeak'] = False

peaks = find_peaks(lane_processed_df["Speed"].values)[0]

for index in peaks:
    lane_processed_df.loc[index, "isPeak"] = True

GEARS = sorted(fastest_tel["nGear"].unique())
print(GEARS)
TOOLS = "box_select,lasso_select,help"

source = ColumnDataSource(lane_processed_df)


left = figure(
    width=800, height=800, title=None, tools=TOOLS, background_fill_color="#fafafa"
)
renderer = left.scatter("X", "Y", size=3, source=source, selection_color="firebrick")

left.line("X", "Y", source=fastest_tel, color="grey")

bins = hexbin(lane_processed_df["next"], lane_processed_df["last"], 0.1)
right = figure(
    width=800,
    height=800,
    title=None,
    tools=TOOLS,
    background_fill_color="#ffffff",
    y_axis_location="right",
)

bottom = figure(
    width=800, height=300, title=None, tools=TOOLS, background_fill_color="#ffffff"
)

bottom.line("Date", "Speed", source=source, color='black')
bottom.circle("Date", "Speed", size = 3, source=source, color="black")


bottom2 = figure(
    width=800, height=300, title=None, tools=TOOLS, background_fill_color="#ffffff"
)
bottom2.line("Date", "acceleration", source=source, color="red")
bottom2.circle("Date", "acceleration", size = 3, source=source, color="black")

right.scatter(
    "next", "last", source=source, color=factor_cmap("nGear", Viridis7, GEARS)
)
# right.hex_tile(
#     "diffNext", "diffLast", source=source,
#     fill_color=linear_cmap('counts', Viridis256, 0, max(bins.counts)),
# )


curdoc().add_root(gridplot([[left, right], [bottom, bottom2]]))
