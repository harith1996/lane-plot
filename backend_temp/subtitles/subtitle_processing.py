import os
import re
import numpy as np

from lane_utils import *
from text_utils import *

FILES = os.listdir('data/')
#FILES = ["math_class_lUUte2o2Sn8.txt", "talk_class_Unzc731iCUY.txt"]
#FILES = ["gameplay__t--dIfd-yI.txt"]

if __name__ == "__main__":
    names = WORD_TAG_TYPES

    for file in FILES:
        with open(os.path.join("data", file), "r") as f:
            text = f.readlines()

        # Combine all lines and delete intros
        text = "".join(text)
        #text = re.sub(r'(?<=[.,;?])\n', ' ', text)
        text = text.replace("\n", " ")

        tokens = nltk.word_tokenize(text)
        #token_list = np.array_split(np.array(tokens), 4)

        # lane_df = word_type_distances(tokens, delta=1, tags=["F"], mode="abs")[0]
        #
        # lane_hist(lane_df, file, to_file=False)
        # lane_hist(lane_df, file, to_file=False, scale="log")
        # continue

        if True:
            try:
                df = pd.Series(tokens).to_frame()
                df.rename(columns={0: "word"}, inplace=True)

                # Select only dots
                df = df[df["word"] == "."]
                df["pos"] = list(df.index)
                df.reset_index(drop=True, inplace=True)

                df = delta_lane_avg(df, key="pos", delta=9)

                lane_hist(df, file, to_file=False)
                lane_hist(df, file, to_file=False, scale="log")
            except:
                pass
            continue

        for delta in range(1, 10, 4):
            lane_dfs = word_type_distances(tokens, delta, mode="abs")

            for i, lane_df in enumerate(lane_dfs):
                lane_hist(lane_df, file+"_"+names[i]+"_lin_delta_"+str(delta), to_file=True)
                lane_hist(lane_df, file+"_"+names[i]+"_log_delta_"+str(delta), scale="log", to_file=True)

