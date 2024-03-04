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


def lane_chart(df, file="", title="", last="last", next="next", color=None, to_file=False, size=None, min_lane=MIN_LANE_DIST, max_lane=MAX_LANE_DIST, log_scale=False):
    if size:
        size = 25*df[size].apply(math.log)
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

    if log_scale:
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