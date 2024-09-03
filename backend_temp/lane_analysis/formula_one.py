from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from scipy.signal import argrelextrema, find_peaks
import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np

from src.plot_utils import lane_hist, lane_chart
from src.lane_utils import delta_lane_abs

def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)

def plot_circuit(session, linewidth=3, rotate_circuit=True, curve_tags=True):
    circuit_info = session.get_circuit_info()
    lap = session.laps.pick_fastest()
    pos = lap.get_pos_data()

    # Get an array of shape [n, 2] where n is the number of points and the second
    # axis is x and y.
    track = pos.loc[:, ('X', 'Y')].to_numpy()

    if rotate_circuit:
        # Convert the rotation angle from degrees to radian.
        track_angle = circuit_info.rotation / 180 * np.pi

        # Rotate and plot the track map.
        track = rotate(track, angle=track_angle)
    plt.plot(track[:, 0], track[:, 1], linewidth=linewidth)

    plt.title(session.event['Location'])
    plt.xticks([])
    plt.yticks([])
    plt.axis('equal')

    if curve_tags:
        offset_vector = [500, 0]  # offset length is chosen arbitrarily to 'look good'

        # Iterate over all corners.
        for _, corner in circuit_info.corners.iterrows():
            # Create a string from corner number and letter
            txt = f"{corner['Number']}{corner['Letter']}"

            # Convert the angle from degrees to radian.
            offset_angle = corner['Angle'] / 180 * np.pi

            # Rotate the offset vector so that it points sideways from the track.
            offset_x, offset_y = rotate(offset_vector, angle=offset_angle)

            # Add the offset to the position of the corner
            text_x = corner['X'] + offset_x
            text_y = corner['Y'] + offset_y

            # Rotate the text position equivalently to the rest of the track map
            text_x, text_y = rotate([text_x, text_y], angle=track_angle)

            # Rotate the center of the corner equivalently to the rest of the track map
            track_x, track_y = rotate([corner['X'], corner['Y']], angle=track_angle)

            # Draw a circle next to the track.
            plt.scatter(text_x, text_y, color='grey', s=140)

            # Draw a line from the track to this circle.
            plt.plot([track_x, text_x], [track_y, text_y], color='grey')

            # Finally, print the corner number inside the circle.
            plt.text(text_x, text_y, txt,
                     va='center_baseline', ha='center', size='small', color='white')

def compute_corner_lanes(df):
    corners = df["Number"].unique()

    df.sort_values(by="Number", inplace=True)
    df.reset_index(drop=True, inplace=True)

    last_lane = []
    next_lane = []
    for corner in corners:
        df_corner = df[df["Number"] == corner]

        df_corner["Distance_to_corner"] = df_corner["Distance_y"] - df_corner["distance_in_lap"]
        df_corner = delta_lane_abs(df_corner, key="Distance_to_corner", delta=1)

        last_lane.append(df_corner["last"])
        next_lane.append(df_corner["next"])

    last_lane = pd.concat(last_lane, axis=0)
    next_lane = pd.concat(next_lane, axis=0)

    df["last"] = last_lane.reset_index(drop=True)
    df["next"] = next_lane.reset_index(drop=True)

    df.sort_values(by="Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def compute_lane_between_corners(df, corners):
    lap_distances = df[["LapNumber", "lap_start_distance"]].groupby("LapNumber", group_keys=True).mean().reset_index()

    last_lap = df["LapNumber"].max()

    last_lane = []
    next_lane = []

    first_corner = corners.iloc[0]
    last_corner = corners.iloc[len(corners) - 1]

    for _, brake_point in df.iterrows():
        # Look for last lap
        if brake_point["distance_in_lap"] < first_corner["Distance"]:
            if brake_point["LapNumber"] == 1:
                # First lap, no curve before
                last_lane.append(0)
            else:
                # Distance to last curve since the beggining of the current lap
                distance_to_last_curve = (brake_point["lap_start_distance"]
                                          - lap_distances[lap_distances["LapNumber"] == brake_point["LapNumber"]-1]["lap_start_distance"].iloc[0]
                                          - last_corner["Distance"])
                last_lane.append(brake_point["distance_in_lap"] + max(distance_to_last_curve, 0))
        else:
            last_corner_dist = corners[corners["Distance"] <= brake_point["distance_in_lap"]]["Distance"].max()
            last_lane.append(brake_point["distance_in_lap"] - last_corner_dist)

        # Append next
        if brake_point["distance_in_lap"] > last_corner["Distance"]:
            if brake_point["LapNumber"] == last_lap:
                # Last lap, no curves ahead
                next_lane.append(0)
            else:
                next_lane.append(
                    lap_distances[lap_distances["LapNumber"] == brake_point["LapNumber"]+1]["lap_start_distance"].iloc[0]
                    - brake_point["Distance_y"] + first_corner["Distance"])
        else:
            next_corner_dist = corners[corners["Distance"] >= brake_point["distance_in_lap"]]["Distance"].min()
            next_lane.append(next_corner_dist - brake_point["distance_in_lap"])

    df["last"] = last_lane
    df["next"] = next_lane

    return df

def distance_to_curve(df, session):
    # Calculate next curve to every point
    corners = session.get_circuit_info().corners
    corners = corners.rename({"Distance": "distance_to_curve"})
    df = pd.merge_asof(df.sort_values("distance_in_lap", axis=0),
                                 corners[["Number", "Distance", "Angle"]].sort_values("Distance", ignore_index=True),
                                 left_on="distance_in_lap",
                                 right_on="Distance", direction="forward")
    return df

def lane_curve(brake_points, session, race_index):
    corners = session.get_circuit_info().corners
    if isinstance(brake_points, list):
        brake_lane = []
        for brake_points_e in brake_points:
            # Calculate next curve to every point
            brake_points_e = distance_to_curve(brake_points_e, session)
            brake_points_e = brake_points_e[brake_points_e['Number'].notna()]

            brake_points_e = compute_lane_between_corners(brake_points_e, corners)

            brake_lane.append(brake_points_e)
        brake_lane = pd.concat(brake_lane)
    else:
        # Calculate next curve to every point
        brake_points = distance_to_curve(brake_points, session)
        brake_points = brake_points[brake_points['Number'].notna()]

        brake_lane = compute_lane_between_corners(brake_points, corners)
    
    lane_chart(
        brake_lane,
        min_lane=0,
        max_lane=brake_lane["last"].max(),
        color="Number",
        cmap=plt.colormaps["Paired"],
        title=race_index
    )
    lane_hist(
        brake_lane,
        min_lane=0,
        max_lane=brake_lane["last"].max(),
        title=race_index
    )
    plot_circuit(session)
    plt.show()

def find_minimum_speed_within_range(df, start_index, end_index):
    return df.loc[start_index:end_index, 'Speed'].idxmin()

def lane_max(df, session, key="RPM", nGear=None, color="Speed", title="", display_lane_hist=False, plot=True):
    df = distance_to_curve(df, session)
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
    for i in range(len(min_points)*2 - 1):
        i = i//2
        if start_max:
            start_index = peaks[i]
            end_index = min_points[i]

            if start_index >= end_index or np.min(d2[start_index:end_index]) > 1000: # -35
                infls_down.append(-1)
                infls_down.append(start_index)
            else:
                infls_down.append(start_index + np.argmin(d2[start_index:end_index]))
        else:
            start_index = min_points[i]
            end_index = peaks[i + 1]

            if start_index >= end_index or np.max(d2[start_index:end_index]) < -1000: # 25
                infls_up.append(-1)
                infls_up.append(start_index)
            else:
                infls_up.append(start_index + np.argmax(d2[start_index:end_index]))
        start_max = not start_max

    events = [item for pair in zip(peaks, infls_down, min_points, infls_up) for item in pair]
    # events = [item for pair in zip(infls_down, infls_up) for item in pair]
    # events = [item for pair in zip(peaks, min_points) for item in pair]
    # events = [item for item in events if item >= 0]

    # line_chart_max(df, key=key, peaks=peaks, valleys=min_points, infls_down=infls_down, infls_up=infls_up)

    # line_chart_max(df, key=key, peaks=peaks, valleys=min_points, infls_down=infls_down, infls_up=infls_up,
    #                min_value=11000, max_value=12000)

    df_max = df.iloc[events]
    df_max = delta_lane_abs(df_max, key=key, delta=2)

    point_type = ["max", "infl_down", "min", "infl_up"]
    df_max['point_type'] = point_type * (len(df_max) // len(point_type)) + point_type[:len(df_max) % len(point_type)]

    # events = [item for pair in zip(events, infls) for item in pair]
    #
    # Select only inflation points
    # df_infl = delta_lane_abs(df.iloc[events], key=key)
    # df_infl = df_infl[df_infl["last"] * df_infl["next"] < 0]

    # df_max = pd.concat([df_max, df_infl])

    if nGear:
        df_max = df_max[df_max["nGear"] == nGear]

    if plot:
        lane_chart(
            df_max,
            min_lane=df_max["last"].min(),
            max_lane=df_max["last"].max(),
            color=color,
            title=title
        )

    if display_lane_hist:
        lane_hist(
            df_max,
            min_lane=df_max["last"].min(),
            max_lane=df_max["last"].max(),
            title=title
        )

    return df_max

def prune_range(values, min_value, max_value):
    return [item-min_value for item in values if item in range(min_value, max_value)]

def line_chart_max(df, key, peaks=None, valleys=None, infls_down=None, infls_up=None, nGear_background=False, min_value=None, max_value=None):
    color = "black" if nGear_background else "white"

    if min_value is None:
        min_value = 0
    if max_value is None:
        max_value = len(df)
    df = df.iloc[min_value:max_value]

    # Plot the line chart
    plt.plot(df.index, df[key], color=color, label='sequence')

    # Find local maxima
    if peaks is not None:
        peaks = prune_range(peaks, min_value, max_value)
        plt.scatter(df.index[peaks], df[key].iloc[peaks], color='red')

    if valleys is not None:
        valleys = prune_range(valleys, min_value, max_value)
        plt.scatter(df.index[valleys], df[key].iloc[valleys], color='blue')

    if infls_down is not None:
        infls_down = prune_range(infls_down, min_value, max_value)
        plt.scatter(df.index[infls_down], df[key].iloc[infls_down], color='green')

    if infls_up is not None:
        infls_up = prune_range(infls_up, min_value, max_value)
        plt.scatter(df.index[infls_up], df[key].iloc[infls_up], color='yellow')

    if nGear_background:
        legend_patches = {}
        # Shade the background based on nGear
        for i in range(len(df) - 1):
            nGear = df.iloc[i]["nGear"]
            handle = mpatches.Patch(color=f'C{nGear}', label=f'nGear {nGear}')
            legend_patches[nGear] = handle
            plt.axvspan(df.index[i], df.index[i + 1], color=f'C{nGear}', alpha=0.3)
        # Add labels and title
        plt.legend(handles=list(legend_patches.values()))

    plt.ylabel(key)
    # Show the plot
    plt.show()


if __name__ == "__main__":
    #fastf1.plotting.setup_mpl()

    # country = "Belgium"

    race_index = 1
    #for session_identifier in ["Q", "S", "SS", "R"]:
    #for race_index in [5]:
    while True:
        try:
            session = fastf1.get_session(2023, race_index, 'R')
            #session = fastf1.get_session(2023, country, session_identifier)
            session.load(telemetry=True)
        except:
            print("No session " + str(race_index))
            break
            # race_index += 1
            # continue

        lane_points = []
        f1_list = []
        drivers = session.drivers
        for j, driver_number in enumerate(drivers):
            #driver_number = session.get_driver(driver)["DriverNumber"]

            try:
                car_data = pd.DataFrame(session.car_data[driver_number].add_distance())
                pos_data = pd.DataFrame(session.pos_data[driver_number])
            except:
                print("Skipped " + str(race_index))
                continue

            # Merge both dataframes at their closest points in time
            f1_df = pd.merge_asof(pos_data, car_data, on="Date", direction="nearest")
            f1_df = f1_df[["Date", "X", "Y", "Z", "Brake", "Throttle", "Distance", "RPM", "Speed", "nGear"]]

            # Add lap information
            lap_data = pd.DataFrame(session.laps)
            lap_data = lap_data[lap_data["DriverNumber"] == driver_number]
            lap_data = lap_data[["LapNumber", "LapStartDate"]]
            lap_data = lap_data[~lap_data["LapStartDate"].isnull()]
            f1_df = pd.merge_asof(f1_df, lap_data, left_on="Date", right_on="LapStartDate", direction="backward")

            # Filter out beginning and end of the race
            # TODO: Check every time
            # Delete first rows
            f1_df.dropna(subset="LapNumber", ignore_index=True, inplace=True)
            f1_df = f1_df[f1_df["Speed"] > 0]
            # f1_df = f1_df[~((f1_df["X"] == -8323) & (f1_df["Y"] == -6449))] # Missing pos values

            # start_race_index = f1_df.eq(f1_df.shift(-1))[["X", "Y"]].all(axis=1).idxmin() + 1  # We assume that the race starts when the car changes X, Y position between measures
            # f1_df = f1_df[start_race_index:].reset_index()
            #
            # # Delte last rows
            # diff = f1_df.diff().abs()
            # end_race_index = (~((diff["X"] > 1000) | (diff["Y"] > 1000))).idxmin()

            # Calculate the initial distance for each lapnumber
            f1_df['lap_start_distance'] = f1_df.groupby('LapNumber')['Distance'].transform('first')
            # Subtract initial distance from distance
            f1_df['distance_in_lap'] = f1_df['Distance'] - f1_df['lap_start_distance']
            # Drop the initial_distance column if not needed
            #f1_df.drop(columns=['initial_distance'], inplace=True)

            #lane_max(f1_df, session)
            #f1_df = f1_df.iloc[10000:]
            f1_list.append(f1_df)

            max_points = lane_max(f1_df, session, key="Speed", color="distance_in_lap", title="Speed "+str(driver_number)+" "+str(race_index), display_lane_hist=False, plot=False)
            max_points["Driver"] = driver_number
            lane_points.append(max_points)
            continue

            # lane_chart(
            #     max_points,
            #     min_lane=max_points["last"].min(),
            #     max_lane=max_points["last"].max(),
            #     color="Speed",
            #     title=str(driver_number)
            # )
            # lane_chart(
            #     max_points,
            #     min_lane=max_points["last"].min(),
            #     max_lane=max_points["last"].max(),
            #     color="distance_in_lap",
            #     title=str(driver_number)
            # )
            # plt.clf()
            continue

            brake_points = f1_df[(f1_df['Brake']==True) & (f1_df['Brake'].shift(-1)==False)]
            brake_points["Driver"] = driver_number
            lane_curve(brake_points, session, race_index)
            continue

            # brake_points.sort_values("Date", axis=0, inplace=True)

            # plot_circuit(session)
            # plt.scatter(brake_points_l1['X'], brake_points_l1['Y'], color="blue", zorder=2.5)
            # plt.show()

            # Brake points
            # brake_points = delta_lane_abs(brake_points, key="Distance_x")
            # Compute distance to curve
            #brake_points = compute_corner_lanes(brake_points)
            # lane_chart(brake_points, min_lane=0, max_lane=brake_points["last"].max(), color="Number", cmap=plt.colormaps["Paired"], title=driver+"_"+str(race_index), log_scale=True)

            # for corner in brake_points["Number"].unique():
            #     df_corner = brake_points[brake_points["Number"] == corner]
            #     lane_chart(df_corner, min_lane=0, max_lane=df_corner["last"].max()+50, title=driver + "_" + str(race_index) + "_" + str(corner), size=24)
            #
            #     if corner == 4: break

                # plot_circuit(session)
                #
                # corner_pos = corners[corners["Number"] == corner]
                #
                # plt.scatter(df_corner['X'], df_corner['Y'], c=df_corner["LapNumber"], zorder=2.5)
                # plt.scatter(corner_pos['X'], corner_pos['Y'], color="red", marker="x", s=10, zorder=2.5)
                #
                # plt.xlim([min(corner_pos['X'].min(), df_corner['X'].min())-200, max(corner_pos['X'].max(), df_corner['X'].max())+200])
                # plt.ylim([min(corner_pos['Y'].min(), df_corner['Y'].min())-100, max(corner_pos['Y'].max(), df_corner['Y'].max())+100])
                #
                # plt.show()


            lane_points.append(brake_points)

        lane_points = pd.concat(lane_points)
        lane_chart(
            lane_points,
            min_lane=-300,
            max_lane=+300,
            color="Speed",
            title=session.event.EventName,
            to_file=True,
            file="speed_"+str(race_index)
        )
        plt.clf()

        lane_chart(
            lane_points,
            min_lane=-300,
            max_lane=300,
            color="distance_in_lap",
            title=session.event.EventName,
            to_file=True,
            file="distance_"+str(race_index)
        )
        plt.clf()

        lane_hist(
            lane_points,
            min_lane=-300,
            max_lane=300,
            title=session.event.EventName,
            nbins=200,
            to_file=True,
            file="hist_"+str(race_index)
        )
        plt.clf()

        # lane_max(pd.concat(f1_list), session, key="Speed", color="Speed", title="Speed Global "+session_identifier, display_lane_hist=True)
        # lane_max(pd.concat(f1_list), session, key="Speed", color="distance_in_lap", title="Speed Global " + session_identifier, display_lane_hist=True)
        # lane_max(pd.concat(f1_list), session, key="RPM", color="nGear", title="RPM Global "+session_identifier, display_lane_hist=True)
        # lane_max(pd.concat(f1_list), session, key="RPM", color="Speed", title="RPM Global " + session_identifier, nGear=8, display_lane_hist=True)

        # lane_curve(lane_points, session, race_index)
        race_index += 1

    pass

