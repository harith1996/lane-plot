import os
from pytube import Playlist
import pickle
from tqdm import tqdm

from backend_temp.lane_analysis.src.plot_utils import *
from backend_temp.lane_analysis.src.text_utils import *

FILES = os.listdir('data/')
#FILES = ["math_class_lUUte2o2Sn8.txt", "talk_class_Unzc731iCUY.txt"]
#FILES = ["gameplay__t--dIfd-yI.txt"]

def minmax_normalization(array, axis=0):
    mins = np.min(array, axis=axis)
    maxs = np.max(array, axis=axis)
    print(maxs)
    array = (array - mins) / (maxs - mins)
    return np.nan_to_num(array)

def std_normalization(array, axis=0):
    mean = np.mean(array, axis=axis)
    std = np.std(array, axis=axis)
    array = (array - mean)/std
    return np.nan_to_num(array)

def get_video_list(url, reverse=True):
    playlist = Playlist(url)
    video_list = list(playlist.video_urls)
    if reverse:
        video_list.reverse()
    return video_list


def lane_sentiment(url, sentiment_folder, reverse=True):
    video_list = get_video_list(url, reverse=reverse)

    for video in tqdm(video_list):
        video_id = video.split('v=')[1]
        video_path = os.path.join(sentiment_folder, video_id + '.pkl')
        if not os.path.exists(video_path):
            continue

        with open(video_path, "rb") as f:
            sent_list = pickle.load(f)

        if len(sent_list) == 0:
            continue

        sent_df = pd.DataFrame(sent_list, columns=['sent'])
        sent_df = delta_lane_abs(sent_df, 'sent')

        lane_chart(sent_df, color="sent", file="lanechart_"+video_id+".png", title=video_id, to_file=True)
        lane_hist(sent_df, adjust_bins=False, draw_axis_lines=True, nbins=20, x_bins=[-2., 2.], y_bins=[-2., 2.], file="lanehist_"+video_id+".png", title=video_id, to_file=True)
        plt.hist(sent_df["sent"], 20)
        plot_config(file="hist_"+video_id+".png", title=video_id, to_file=True)
def playlist_fingerprinting(url, data_folder, reverse=True):
    video_list = get_video_list(url, reverse=reverse)

    names = ["F", "ADJ", "ADV", "N", "V"]
    deltas = [1, 3, 5, 7, 9]

    for delta in deltas:
        fingerprints = []
        for video in tqdm(video_list):
            video_id = video.split('v=')[1]
            video_path = os.path.join(data_folder, video_id + '.txt')
            if not os.path.exists(video_path):
                continue

            with open(video_path, "r") as f:
                text = f.readlines()[0]

            if not text:
                continue

            tokens = nltk.word_tokenize(text)

            lane_dfs = word_type_distances(tokens, delta=delta, mode="abs", tags=names)

            df_fingerprints = []
            for i, df in enumerate(lane_dfs):
                last_array = np.array(df["last"])
                #next_array = np.array(df["next"])

                percentiles = np.percentile(last_array, range(10, 100, 10))

                df_fingerprints.append(percentiles)

                # last_mean = df["last"].mean()
                # next_mean = df["next"].mean()
                # if not math.isclose(last_mean, next_mean):
                #     print("Difference found in "+names[i]+". last: "+str(last_mean)+" next: "+str(next_mean))
                # df_fingerprints.append(last_mean)
            fingerprints.append(np.array(df_fingerprints))

            #print("Processed "+video_id)

        fingerprints = np.array(fingerprints)
        for i, name in enumerate(names):
            fingerprinting_plot(minmax_normalization(fingerprints[:, i, :], axis=None), title=name+"_"+str(delta), file=name+"_"+str(delta), to_file=True)


if __name__ == "__main__":
    URL = "https://www.youtube.com/playlist?list=PLrAXtmErZgOdP_8GztsuKi9nrraNbKKp4"
    data_folder = 'data/lex_fridman'

    URL = "https://www.youtube.com/playlist?list=PLUl4u3cNGP63LmSVIVzy584-ZbjbJ-Y63"
    data_folder = "data/bio_class"
    #lane_sentiment(URL, data_folder+"_sent", reverse=False)
    playlist_fingerprinting(URL, data_folder, reverse=False)

    exit(0)
    names = WORD_TAG_TYPES

    for file in FILES:
        with open(os.path.join("data", file), "r") as f:
            text = f.readlines()

        # Combine all lines and delete intros
        text = "".join(text)
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

