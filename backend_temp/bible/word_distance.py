import pandas as pd
import re
from collections import Counter
from matplotlib import pyplot as plt

FILE = "kjv.txt"
WORDS = ["god", "jesus", "lord", "man", "israel"]

def text_distance(text, word):
    word_pos = []
    last_word = []
    next_word = []

    # Skip the first word, since it has no prev
    start = text.find(word)
    end = text.find(word, start + len(word))
    if end == -1:
        return
    distance = end - start - len(word)
    start = text.find(word, end)

    while start != -1:
        end = text.find(word, start + len(word))
        if end == -1:
            break

        word_pos.append(start)
        last_word.append(distance)

        distance = end - start - len(word)

        next_word.append(distance)

        start = text.find(word, end)

    # Build pandas DataFrame
    pd_dict = {'word_pos': word_pos, 'last_word': last_word, 'next_word': next_word}
    return pd.DataFrame(pd_dict)

if __name__=="__main__":
    with open(FILE, "r") as f:
        lines = f.readlines()

    # Remove book references
    lines = [l.split(None, 1)[1] for l in lines]

    text = "".join(lines)
    text = text.replace("\n", " ").lower()

    # Count most frequent words
    # words = re.findall(r'\w+', text.lower())
    # Counter(words).most_common(100)

    for word in WORDS:
        df = text_distance(text, word)

        df.plot.scatter("last_word", "next_word", c="word_pos", colormap="viridis", alpha=0.3)
        plt.title("LaNe for "+word)
        plt.xscale("log")
        plt.yscale("log")
        plt.show()
