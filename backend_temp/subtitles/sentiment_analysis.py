import os
import nltk
from tqdm import tqdm
import pickle
from nltk.sentiment import SentimentIntensityAnalyzer

PLAYLIST_NAME = "bio_class"
IN_FOLDER = "data/"+PLAYLIST_NAME+"_lines"
OUT_FOLDER = "data/"+PLAYLIST_NAME+"_sent"
GROUP_SIZE = 5

if __name__ == "__main__":
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()

    for file in tqdm(os.listdir(IN_FOLDER)):
        with open(os.path.join(IN_FOLDER, file), "r") as f:
            text = f.readlines()

        scores = []
        for i in range(0, len(text), GROUP_SIZE):
            merged_text = "".join(text[i:i+GROUP_SIZE])
            merged_text = merged_text.replace("\n", " ")
            # Perform sentiment analysis
            score = sia.polarity_scores(merged_text)
            # score["text"] = merged_text
            scores.append(score["compound"])

        # Dump output in a pickle file
        out_file = file.replace(".txt", "")+".pkl"
        with open(os.path.join(OUT_FOLDER, out_file), "wb") as f:
            pickle.dump(scores, f)