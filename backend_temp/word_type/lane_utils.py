from matplotlib import pyplot as plt
import math

MIN_LANE_DIST = -20
MAX_LANE_DIST = 20

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

def lane_plot(df, file="", title="", last="last", next="next", color="mean_size", to_file=False, size="count"):
    # group_df = df.groupby(["last_f", "next_f"]).size().reset_index(name='count')
    plt.scatter(df[last], df[next], c=df[color], cmap="viridis", s=(10*df[size].apply(math.log)))

    plot_title = file+" LaNe chart "+title
    plt.title(plot_title)
    plt.xlabel("last")
    plt.ylabel("next")
    plt.colorbar()
    plt.ylim([MIN_LANE_DIST, MAX_LANE_DIST])
    plt.xlim([MIN_LANE_DIST, MAX_LANE_DIST])
    if to_file:
        plt.savefig("plots/" + plot_title.replace(":", "colon").replace(";", "semicolon").replace(",", "comma").replace(".", "period") + ".png")
    else:
        plt.show()
    plt.clf()