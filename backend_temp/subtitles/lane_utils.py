from matplotlib import pyplot as plt
import numpy as np
import math

from plot_utils import plot_config

MIN_LANE_DIST = -1
MAX_LANE_DIST = 1


def delta_lane(df, key="timestamp", delta=1):
    lane_last = [0]

    for i in range(1, delta):
        lane_last.append(df[key][i]-df[key][0])

    for i in range(delta, len(df)):
        lane_last.append(df[key][i]-df[key][i-delta])

    lane_next = lane_last.copy()
    lane_next = lane_next[delta:]

    for i in range(len(df)-delta, len(df)):
        lane_next.append(df[key][len(df)-1] - df[key][i])

    df["last"] = lane_last
    df["next"] = lane_next

    return df


def delta_lane_avg(df, key="timestamp", delta=2):
    if delta == 1:
        return delta_lane(df, key, delta)

    # Compute last values
    lane_last = [0]

    for i in range(1, delta):
        # Compute the average
        avg_value = 0
        for j in range(0, i):
            avg_value += df[key][i] - df[key][j]
        avg_value /= i

        lane_last.append(avg_value)

    for i in range(delta, len(df)):
        avg_value = 0
        for j in range(i-delta, i):
            avg_value += df[key][i] - df[key][j]
        avg_value /= delta
        lane_last.append(avg_value)

    # Compute next values
    lane_next = []
    for i in range(0, len(df)-delta):
        avg_value = 0
        for j in range(i+1, i+delta+1):
            avg_value += df[key][j] - df[key][i]
        avg_value /= delta
        lane_next.append(avg_value)

    for i in range(len(df)-delta, len(df)-1):
        avg_value = 0
        for j in range(i+1, len(df)):
            avg_value += df[key][j] - df[key][i]
        avg_value /= len(df)-i-1

        lane_next.append(avg_value)
    lane_next.append(0)

    df["last"] = lane_last
    df["next"] = lane_next

    return df


def get_lane_distance(df1, df2, max_lane=MAX_LANE_DIST):
    dist_sum = 0.

    df1_sum = df1["count"].sum()
    df2_sum = df2["count"].sum()

    if df1_sum+df2_sum == 0.:
        return 0., 0.

    for i in range(1, max_lane+1):
        for j in range(1, max_lane+1):
            count_1 = df1[(df1["last"] == i) & (df1["next"] == j)]["count"]
            count_2 = df2[(df2["last"] == i) & (df2["next"] == j)]["count"]

            if len(count_1) == 0:
                count_1 = 0.
            else:
                count_1 = count_1.iloc[0]
            if len(count_2) == 0:
                count_2 = 0.
            else:
                count_2 = count_2.iloc[0]

            dist_sum += abs(count_1/df1_sum-count_2/df2_sum)

    return dist_sum, df1_sum+df2_sum


def lane_chart(df, file="", title="", last="last", next="next", color=None, to_file=False, size=None, min_lane=MIN_LANE_DIST, max_lane=MAX_LANE_DIST, scale=None):
    # group_df = df.groupby(["last_f", "next_f"]).size().reset_index(name='count')
    if size:
        size = 25*df[size].apply(math.log)
        # size = df[size]/10
    else:
        size = 8

    if color:
        plt.scatter(df[last], df[next], c=df[color], cmap="viridis", s=size, alpha=0.7)
    else:
        plt.scatter(df[last], df[next], s=size)

    plt.xlabel("last")
    plt.ylabel("next")
    plt.colorbar()

    plt.ylim([min_lane, max_lane])
    plt.xlim([min_lane, max_lane])

    if scale == "log":
        plt.yscale('log')
        plt.xscale('log')

    plot_config(file=file, title=title, to_file=to_file)

def lane_hist(df, file="", title="", to_file=False, nbins=50, scale=None, adjust_bins=True, draw_axis_lines=False, x_bins=None, y_bins=None):
    x = df["last"]
    y = df["next"]

    if x_bins and y_bins:
        x_bins = [x_bins[0] + i * (x_bins[1] - x_bins[0]) / nbins for i in range(nbins)]+[x_bins[1]]
        y_bins = [y_bins[0] + i * (y_bins[1] - y_bins[0]) / nbins for i in range(nbins)]+[y_bins[1]]
    else:
        # Adjust nbins if few space
        if adjust_bins:
            nbins = int(min(nbins, x.max(), y.max()))

        if scale == "log":
            x_bins = [0]+np.logspace(0, np.log10(x.max()), nbins-1)
            y_bins = [0]+np.logspace(0, np.log10(y.max()), nbins-1)
            plt.xscale('log')
            plt.yscale('log')
        else:
            x_bins = [x.min()+i*(x.max()-x.min())/nbins for i in range(nbins)]
            y_bins = [y.min()+i*(y.max()-y.min())/nbins for i in range(nbins)]

    plt.hist2d(x, y, [x_bins, y_bins], cmin=1, cmap="viridis")

    plt.xlabel("last")
    plt.ylabel("next")

    plt.colorbar()

    if draw_axis_lines:
        plt.axhline(0, color="black")
        plt.axvline(0, color="black")

    plot_config(file=file, title=title, to_file=to_file)