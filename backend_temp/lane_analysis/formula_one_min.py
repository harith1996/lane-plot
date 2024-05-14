import fastf1
import fastf1.plotting
import pandas as pd
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
        # for j, driver_number in enumerate(drivers):
        #     #driver_number = session.get_driver(driver)["DriverNumber"]

        #     try:
        #         car_data = pd.DataFrame(session.car_data[driver_number].add_distance())
        #         pos_data = pd.DataFrame(session.pos_data[driver_number])
        #     except:
        #         print("Skipped " + str(race_index))
        #         continue

        #     # Merge both dataframes at their closest points in time
        #     f1_df = pd.merge_asof(pos_data, car_data, on="Date", direction="nearest")
        #     f1_df = f1_df[["Date", "X", "Y", "Z", "Brake", "Throttle", "Distance", "RPM", "Speed", "nGear"]]

        #     # Add lap information
        #     lap_data = pd.DataFrame(session.laps)
        #     lap_data = lap_data[lap_data["DriverNumber"] == driver_number]
        #     lap_data = lap_data[["LapNumber", "LapStartDate"]]
        #     lap_data = lap_data[~lap_data["LapStartDate"].isnull()]
        #     f1_df = pd.merge_asof(f1_df, lap_data, left_on="Date", right_on="LapStartDate", direction="backward")

        #     # Filter out beginning and end of the race
        #     # TODO: Check every time
        #     # Delete first rows
        #     f1_df.dropna(subset="LapNumber", ignore_index=True, inplace=True)
        #     f1_df = f1_df[f1_df["Speed"] > 0]
        #     # f1_df = f1_df[~((f1_df["X"] == -8323) & (f1_df["Y"] == -6449))] # Missing pos values