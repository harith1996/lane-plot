import matplotlib.pyplot as plt
import math
import numpy as np

MIN_LANE_DIST = -1
MAX_LANE_DIST = 1

def plot_config(file, title, to_file):
    plot_title = title
    plt.title(plot_title)

    if to_file:
        fig_name = "plots/" + file.replace(":", "colon").replace(";", "semicolon").replace(",", "comma").replace(".", "period") + ".png"
        plt.savefig(fig_name)
    else:
        plt.show()
    plt.clf()


def fingerprinting_plot(data, cmap="viridis", file="", title="", to_file=False):
    # Plotting
    plt.figure(figsize=(8, 6))

    # Create a colormap
    cmap = plt.colormaps.get_cmap(cmap)

    # Plot each square with its corresponding color
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            color = cmap(data[i, j])
            plt.fill_between([i, i+1], j, j+1, color=color)

    plt.xlim(0, data.shape[0])
    plt.ylim(0, data.shape[1])
    plt.gca().set_aspect('equal', adjustable='box')

    # Suppress axis ticks
    plt.xticks([])
    plt.yticks([])

    # Remove white space on all four sides
    plt.gca().set_axis_off()

    plot_config(file, title, to_file)


def line_chart(series, file=" ", title="", to_file=False):
    plt.plot(series)
    plot_config(file, title, to_file)


def lane_chart(df, file="", title="", last="last", next="next", color=None, to_file=False, size=8, min_lane=MIN_LANE_DIST, max_lane=MAX_LANE_DIST, log_scale=False,
               cmap="viridis"):
    # if size:
    #     size = 25*df[size].apply(math.log)
    # else:
    #     size = 8

    if color:
        plt.scatter(df[last], df[next], c=df[color], cmap=cmap, s=size, alpha=0.7)
    else:
        plt.scatter(df[last], df[next], s=size)

    plt.xlabel("last")
    plt.ylabel("next")
    plt.colorbar()

    if log_scale:
        plt.yscale('log')
        plt.xscale('log')
    else:
        plt.ylim([min_lane, max_lane])
        plt.xlim([min_lane, max_lane])

    plot_config(file=file, title=title, to_file=to_file)


def lane_hist(df, file="", title="", to_file=False, nbins=50, scale=None, adjust_bins=True, draw_axis_lines=False, x_bins=None, y_bins=None, min_lane=None, max_lane=None):
    x = df["last"]
    y = df["next"]

    if x_bins and y_bins:
        x_bins = [x_bins[0] + i * (x_bins[1] - x_bins[0]) / nbins for i in range(nbins)]+[x_bins[1]]
        y_bins = [y_bins[0] + i * (y_bins[1] - y_bins[0]) / nbins for i in range(nbins)]+[y_bins[1]]
    else:
        # Adjust nbins if few space
        if min_lane:
            x_min = min_lane
            y_min = min_lane
        else:
            x_min = x.min()
            y_min = y.min()
        if max_lane:
            x_max = max_lane
            y_max = max_lane
        else:
            x_max = x.max()
            y_max = y.max()

        if adjust_bins:
            nbins = int(min(nbins, x_max, y_max))

        if scale == "log":
            x_bins = [0]+np.logspace(0, np.log10(x_max), nbins-1)
            y_bins = [0]+np.logspace(0, np.log10(y_max), nbins-1)
            plt.xscale('log')
            plt.yscale('log')
        else:
            x_bins = [x_min+i*(x_max-x_min)/nbins for i in range(nbins)]
            y_bins = [y_min+i*(y_max-y_min)/nbins for i in range(nbins)]

    plt.hist2d(x, y, [x_bins, y_bins], cmin=1, cmap="viridis")

    plt.xlabel("last")
    plt.ylabel("next")

    plt.colorbar()

    if min_lane and max_lane:
        plt.ylim([min_lane, max_lane])
        plt.xlim([min_lane, max_lane])

    if draw_axis_lines:
        plt.axhline(0, color="black")
        plt.axvline(0, color="black")

    plot_config(file=file, title=title, to_file=to_file)