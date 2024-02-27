import matplotlib.pyplot as plt

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
    # y = [0.]
    # x = [0.]
    #
    # for i, element in enumerate(series):
    #     x.append(element.timestamp())
    #     y.append(i+1)
    #
    # plt.plot(x, y)
    plt.plot(series)

    plot_title = file+" line chart "+title
    plt.title(plot_title)

    # plt.xlim(0, x[-1])

    if to_file:
        fig_name = "plots/" + plot_title.replace(":", "colon").replace(";", "semicolon").replace(",", "comma").replace(".", "period") + ".png"
        plt.savefig(fig_name)
    else:
        plt.show()
    plt.clf()