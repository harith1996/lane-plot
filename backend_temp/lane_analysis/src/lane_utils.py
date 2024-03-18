import pandas as pd

def delta_lane_abs(df, key="timestamp", delta=1, time_metric=False):
    """
    Computes the absolute delta lane last and next values from a given sequence
    :param df: A pandas DataFrame containing the sequence
    :param key: The name of the column being indexed
    :param delta: The delay introduced to calculate the values
    :return: The df parameter with the columns "last" and "next" filled with the corresponding LaNe values
    """
    df = df.reset_index(drop=True)

    if time_metric:
        lane_last = [pd.Timedelta(seconds=0)]
    else:
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
    """
    Computes the average delta lane last and next values from a given sequence
    :param df: A pandas DataFrame containing the sequence
    :param key: The name of the column being indexed
    :param delta: The delay introduced to calculate the values
    :return: The df parameter with the columns "last" and "next" filled with the corresponding LaNe values
    """
    if delta == 1:
        return delta_lane_abs(df, key, delta)

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


def get_lane_distance(df1, df2, max_lane=None):
    """
    Computes the lane distance between two lane dataframes
    :param df1: One lane dataframe
    :param df2: Another lane dataframe
    :param max_lane: The max_value to compare between the two lanes
    :return:
    """
    if not max_lane:
        max_lane = max(df1["last"].max(), df1["next"].max(), df2["last"].max(), df2["next"].max())

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