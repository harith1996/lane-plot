import pickle
import pandas as pd
import matplotlib.pyplot as plt

if __name__=="__main__":
    # article_name = "Earth"
    article_names = ["Barack_Obama", "Donald_Trump", "Mike_Pence", "Hilary_Clinton", "Tim_Kaine", "Joe_Biden", "Kamala_Harris"]

    for article_name in article_names:
        file_path = "wiki_raw/"+article_name+".pkl"
        with open(file_path, "rb") as f:
            raw_data = pickle.load(f)

        df = pd.DataFrame.from_dict(raw_data)

        user_df = df['user'].apply(pd.Series)
        user_df.rename({"id": "user_id", "name": "username"}, axis=1, inplace=True)
        df = pd.concat([df, user_df], axis=1).drop('user', axis=1)

        # Convert to timestamp time
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        df.drop("delta", axis=1, inplace=True)

        # Count nans in user_id (anonymous contributions)
        print("There are", str(df['user_id'].isna().sum()), "anonymous revisions out of", str(len(df)))

        username_counts = df["username"].value_counts()
        # plt.hist(username_counts, bins=max(username_counts))  # //5)
        # plt.title(article_name)
        # plt.show()

        # plt.hist(username_counts, bins=max(username_counts)//5)
        # plt.ylim(0, 50)
        # plt.show()
        #
        # plt.hist(username_counts, bins=max(username_counts)//5)
        # plt.ylim(0, 10)
        # plt.show()
        #
        # plt.hist(username_counts[username_counts <= 200], bins=max(username_counts)//2)
        # plt.ylim(0, 10)
        # plt.show()

        # Calculate time dilation
        df.sort_values("timestamp", inplace=True)

        # df.plot.line("timestamp", "size")
        # # plt.ylim(0, 2.5*10**5)
        # plt.title(article_name)
        # plt.show()

        # Get LaNe from timestamp
        df["last_time"] = df["timestamp"].diff()
        df["last_time"].fillna(-1)

        df["next_time"] = df["timestamp"].shift(-1) - df["timestamp"]
        df["next_time"].fillna(-1)

        # df.plot.scatter("last_time", "next_time", alpha=0.3)
        # plt.title(article_name)
        # plt.show()

        # Get LaNe from size
        df.sort_values("size", inplace=True)

        df["last_size"] = df["size"].diff()
        df["last_size"].fillna(-1)

        df["next_size"] = df["size"].shift(-1) - df["size"]
        df["next_size"].fillna(-1)

        df.plot.scatter("last_size", "next_size", alpha=0.3)
        # plt.title(article_name)
        # plt.xlim(0, 2500)
        # plt.ylim(0, 2500)º
        # plt.show()

        df.sort_values("timestamp", inplace=True)

        df.set_index("id", drop=False, inplace=True)
        df.to_json("wiki_json/"+article_name+".json", orient="records")
