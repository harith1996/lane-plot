import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np

REQUESTING_ADDRESS = "163.206.89.4" # "piweba4y.prodigy.com" # "edams.ksc.nasa.gov"

if __name__ == "__main__":
    df = pd.read_csv("nasa_aug95_c.csv")
    df["datetime"] = pd.to_datetime(df["datetime"])

    df = df[df["requesting_host"] == REQUESTING_ADDRESS]

    df.sort_values("datetime", axis=0, inplace=True, ignore_index=True)

    df["last_time"] = df["datetime"].diff()
    df["last_time"].fillna(-1)

    df["next_time"] = df["datetime"].shift(-1) - df["datetime"]
    df["next_time"].fillna(-1)

    plt.scatter(df["last_time"], df["next_time"], c=df["response_size"], cmap="viridis", alpha=0.3)
    plt.title("Requests from "+REQUESTING_ADDRESS)
    plt.xscale("log")
    plt.yscale("log")
    plt.show()