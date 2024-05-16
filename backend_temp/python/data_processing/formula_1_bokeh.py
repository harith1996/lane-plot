from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.transform import factor_cmap, linear_cmap
from bokeh.palettes import Viridis256, Viridis7
from bokeh.util.hex import hexbin
from scipy.signal import find_peaks
import pandas as pd
import numpy as np

from diffComputer import DiffComputer
from dataService import DataService
import fastf1
import ptvsd
import os


def is_wet_lap(lap):
    weather_data = lap.get_weather_data()
    if weather_data.Rainfall:
        return True
    else:
        return False


# attach to VS Code debugger if this script was run with BOKEH_VS_DEBUG=true
# (place this just before the code you're interested in)
if os.environ['BOKEH_VS_DEBUG'] == 'true':
    # 5678 is the default attach port in the VS Code debug configurations
    print('Waiting for debugger attach')
    ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)
    ptvsd.wait_for_attach()

session = fastf1.get_session(2021, "Austrian Grand Prix", "Q")
session.load()
fastest_lap = session.laps.pick_fastest()

tel = fastest_lap.get_telemetry()
tel['nGear'] = tel['nGear'].astype(str)
tel = tel.reset_index(drop=True)

ds = DataService(tel, {
    "Speed": float
})


lane_processed_df = ds.add_diff_list(fieldName = "Speed", linearizeBy="Date", df=tel)
GEARS = sorted(tel["nGear"].unique())
print(GEARS)
TOOLS = "box_select,lasso_select,help"

source = ColumnDataSource(lane_processed_df)


left = figure(
    width=800, height=800, title=None, tools=TOOLS, background_fill_color="#fafafa"
)
left.scatter("X", "Y", source=source)
bins = hexbin(lane_processed_df['diffNext'], lane_processed_df['diffLast'], 0.1)
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

bottom.line("Date", "Speed", source=source)

right.scatter("diffNext", "diffLast", source=source, color=factor_cmap("nGear", Viridis7, GEARS))
# right.hex_tile(
#     "diffNext", "diffLast", source=source,
#     fill_color=linear_cmap('counts', Viridis256, 0, max(bins.counts)),
# )



curdoc().add_root(gridplot([[left, right],[bottom]]))
