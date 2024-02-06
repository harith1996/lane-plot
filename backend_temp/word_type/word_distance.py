import nltk
import pandas as pd
from generate_lanes import lane_chart
import os

FILES = ["2020_trump.txt", "2021_biden.txt"]
FILES = os.listdir("books/")

KEYWORDS = [
    # "god", "america", "american", "americans", "country", "people",
    ".", ",", ";", ":"]

if __name__ == '__main__':
    for file in FILES:
        with open("books/"+file, "r", encoding="utf8") as f:
            text = f.read()

        text = text.replace("\n", " ").lower()

        for keyword in KEYWORDS:
            df = token_word_distance(text, keyword)
            df_word = df.groupby(["last_word", "next_word"]).size().reset_index(name='count')
            #lane_chart(df_word, file=file, title=keyword, last="last_word", next="next_word", to_file=True)


