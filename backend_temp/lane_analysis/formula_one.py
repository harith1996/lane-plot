from matplotlib import pyplot as plt
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
                last_lane.append(brake_point["distance_in_lap"] + distance_to_last_curve)
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
                    - brake_point["Distance"] + first_corner["Distance"])
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
                                 corners[["Number", "Distance", "Angle"]], left_on="distance_in_lap",
                                 right_on="Distance", direction="forward")
    return df

def lane_curve(brake_points, session):
    corners = session.get_circuit_info().corners
    # Calculate next curve to every point
    distance_to_curve(brake_points, session)
    brake_points = brake_points[brake_points['Number'].notna()]

    brake_points = compute_lane_between_corners(brake_points, corners)

    lane_chart(
        brake_points,
        min_lane=0,
        max_lane=brake_points["last"].max(),
        color="Number",
        cmap=plt.colormaps["Paired"]
    )
    plot_circuit(session)
    plt.show()

def lane_rpm(df, session):
    df = distance_to_curve(df, session)
    df = df.sort_values("Date", axis=0).reset_index(drop=True)
    # Get local maxima
    df_max = df[(df["RPM"].shift(1) < df["RPM"]) & (df["RPM"].shift(-1) < df["RPM"])]

    df_max = delta_lane_abs(df_max, key="RPM")
    lane_chart(
        df_max,
        min_lane=df_max["last"].min(),
        max_lane=df_max["last"].max(),
        color="nGear"
    )


DRIVERS = ["VER", "HUL", "SAI", "HAM"]

if __name__ == "__main__":
    fastf1.plotting.setup_mpl()

    race_index = 1
    while True:
        session = fastf1.get_session(2022, race_index, 'R')
        session.load(telemetry=True)

        lane_points = []
        drivers = session.drivers
        for j, driver_number in enumerate(drivers):
            #driver_number = session.get_driver(driver)["DriverNumber"]

            car_data = pd.DataFrame(session.car_data[driver_number].add_distance())
            pos_data = pd.DataFrame(session.pos_data[driver_number])

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

            lane_rpm(f1_df, session)
            continue

            brake_points = f1_df[(f1_df['Brake']==True) & (f1_df['Brake'].shift(-1)==False)]
            lane_curve(brake_points, session)

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

        race_index += 1

    pass

