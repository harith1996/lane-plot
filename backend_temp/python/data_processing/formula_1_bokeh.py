from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.sampledata.penguins import data
from bokeh.transform import factor_cmap, linear_cmap
from bokeh.palettes import Viridis7
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
    

...

# attach to VS Code debugger if this script was run with BOKEH_VS_DEBUG=true
# (place this just before the code you're interested in)
if os.environ['BOKEH_VS_DEBUG'] == 'true':
    # 5678 is the default attach port in the VS Code debug configurations
    print('Waiting for debugger attach')
    ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)
    ptvsd.wait_for_attach()


session = fastf1.get_session(2021, "Austrian Grand Prix", "Q")
session.load()

lap = session.laps.pick_fastest()
laps = filter(is_wet_lap, session.laps)
tel = lap.get_telemetry()
tel['nGear'] = tel['nGear'].astype(str)
tel = tel.reset_index(drop=True)

ds = DataService(tel, {
    "Speed": float
})
ds.df = ds.add_diff_list(fieldName = "Speed", linearizeBy="Date", df=tel)

SPECIES = sorted(data.species.unique())
GEARS = sorted(tel["nGear"].unique())
print(GEARS)
TOOLS = "box_select,lasso_select,help"

source = ColumnDataSource(ds.df)


left = figure(
    width=800, height=800, title=None, tools=TOOLS, background_fill_color="#fafafa"
)
left.scatter("X", "Y", source=source)

right = figure(
    width=800,
    height=800,
    title=None,
    tools=TOOLS,
    background_fill_color="#fafafa",
    y_axis_location="right",
)
right.scatter(
    "diffNext", "diffLast", source=source,
    color=factor_cmap("nGear", Viridis7, GEARS),
)

curdoc().add_root(gridplot([[left, right]]))
