import nltk
nltk.download('averaged_perceptron_tagger')
import pandas as pd
import os
import string

from lane_utils import get_lane_distance, lane_plot

FILES = os.listdir("news/")
FILES = ["cnn", "foxnews"]
FILES = ["BUSINESS", "ENTERTAINMENT", "HEALTH", "NATION", "SCIENCE", "SPORTS", "TECHNOLOGY", "WORLD"]
# FILES = ["Ashashi_Shimbun", "BuzzFeed", "CNN", "Fox-News", "Globe-Mail", "Mail-Guardian", "Peoples-Daily", "The-Guardian", "Times-India", "Wall-Street"]

CONTENT_TAGS = ["FW"]
FUNCTION_TAGS = ["CC", "CD", "DT", "EX", "IN", "LS", "MD", "PDT", "WP$", "WP", "WDT", "UH", "TO", "RP", "PRP", "PRP$"]
ADJECTIVE_TAGS = ["JJ", "JJR", "JJS"]
ADVERB_TAGS = ["WRB", "RBS", "RB", "RBR"]
NOUN_TAGS = ["NN", "NNS", "NNP", "NNPS"]
VERB_TAGS = ["VBZ", "VBP", "VBN", "VBG", "VBD", "VB"]

WORD_TAG_TYPES = ["F", "ADJ", "ADV", "N", "V", "U"]

STYLOMETYRIC_WORDS = ["the", "and", "to", "a", "an", "of", "in", "that", "those", "it", "not", "as", "with", "but",
                      "for", "at", "this", "these", "so", "all", "on", "from", "one", "ones", "up", "no", "out", "out",
                      "what", "then", "if", "there", "by", "who", "when", "into", "now", "down", "over", "back", "or",
                      "well", "which", "how", "here", "just", "very", "where", "before", "upon", "about", "after",
                      "more", "why", "some"]

PUNCTUATION_SIGNS = [".", ",", ";", ":"]

LETTERS = list(string.ascii_lowercase)

def classify_tag(tag):
    if tag in FUNCTION_TAGS:
        return "F"
    elif tag in ADJECTIVE_TAGS:
        return "ADJ"
    elif tag in ADVERB_TAGS:
        return "ADV"
    elif tag in NOUN_TAGS:
        return "N"
    elif tag in VERB_TAGS:
        return "V"
    else:
        return "U"


def word_type_distance(tokens):
    word_tags = nltk.pos_tag(tokens)

    df = pd.DataFrame(word_tags, columns=["word", "tag"])
    df["word_type"] = df["tag"].apply(classify_tag)

    lane_dfs = []
    for word_type in WORD_TAG_TYPES:
        df_wtype = df.copy()

        df_wtype = df_wtype[df_wtype["word_type"] == word_type]
        df_wtype["pos"] = list(df_wtype.index)

        df_wtype["last"] = df_wtype["pos"].diff()
        df_wtype["last"].fillna(-1)

        df_wtype["next"] = df_wtype["pos"].shift(-1) - df_wtype["pos"]
        df_wtype["next"].fillna(-1)

        df_wtype = df_wtype.groupby(["last", "next"]).size().reset_index(name='count')

        lane_dfs.append(df_wtype)

    return lane_dfs


def get_lane_signature(df):
    dfs = []

    for word in STYLOMETYRIC_WORDS:
        df_word = df[df["word"] == word]
        df_word = df_word.groupby(["last", "next"]).size().reset_index(name='count')

        # Normalize count values
        df_word["count"] = df_word["count"] / len(df)

        df_word["word"] = word
        dfs.append(df_word)

    return dfs


def token_word_distance(tokens, keyword):
    word_pos = []
    last_word = []
    next_word = []

    for i, word in enumerate(tokens):
        if word == keyword:
            word_pos.append(i)
            last_word.append(-1)
            break

    last_index = i
    index = i + 1

    for word in tokens[index:]:
        if word == keyword:
            word_pos.append(index)
            next_word.append(index - last_index)
            last_word.append(index - last_index)
            last_index = index

        index += 1

    if len(last_word) > 0:
        next_word.append(-1)

    pd_dict = {'word_pos': word_pos, 'last': last_word, 'next': next_word}
    df_word = pd.DataFrame(pd_dict)
    df_word = df_word.groupby(["last", "next"]).size().reset_index(name='count')
    return df_word


def get_function_distances(dfs1, dfs2, names):
    dists = []
    counts = []
    for df1, df2, name in zip(dfs1, dfs2, names):
        print("Getting distances for",name)
        dist, count = get_lane_distance(df1, df2)
        dists.append(dist)
        counts.append(count)
    return pd.DataFrame({'lane_name': names, 'distance': dists, 'count': counts})

def get_lane_letters(text):
    lanes = []
    for letter in LETTERS:
        letter_pos = []
        last_letter = []
        next_letter = []

        # Skip the first word, since it has no prev
        start = text.find(letter)
        end = text.find(letter, start + 1)
        if end == -1:
            return
        distance = end - start
        start = text.find(letter, end)

        while start != -1:
            end = text.find(letter, start + 1)
            if end == -1:
                break

            letter_pos.append(start)
            last_letter.append(distance)

            distance = end - start

            next_letter.append(distance)

            start = text.find(letter, end)

        df = pd.DataFrame({'position': letter_pos, 'last': last_letter, 'next': next_letter})
        df = df.groupby(["last", "next"]).size().reset_index(name='count')
        lanes.append(df)

    return lanes


if __name__ == "__main__":
    lane_dfs = []
    names = LETTERS + WORD_TAG_TYPES + STYLOMETYRIC_WORDS + PUNCTUATION_SIGNS
    #names = [s + "_letters" for s in LETTERS]
    for file in FILES:

        # with open("news/" + file, "r", encoding="utf8") as f:
        #     text = f.read()

        # text = ""
        # for i in range(5):
        #     with open("news/"+file+"_"+str(i)+".txt", encoding="utf8") as f:
        #         text += f.read()

        path = "E:/news/news_"+file+"_2023-10-31.csv"
        if os.path.isfile(path):
            df = pd.read_csv(path)
        else:
            path = "E:/news/news_" + file + "_2023-10-31.0.csv"
            if os.path.isfile(path):
                df = pd.read_csv(path)
            else:
                continue
        try:
            text = df["text"].str.cat(sep=" ")
        except:
            continue

        text = text.replace("\n", " ").lower().replace("  ", " ")

        file_dfs = get_lane_letters(text)

        tokens = nltk.word_tokenize(text)

        file_dfs += word_type_distance(tokens)

        for word in STYLOMETYRIC_WORDS:
            file_dfs.append(token_word_distance(tokens, word))

        for word in PUNCTUATION_SIGNS:
            file_dfs.append(token_word_distance(tokens, word))

        for i, lane_df in enumerate(file_dfs):
            lane_plot(lane_df, file+"_"+names[i], file+"_"+names[i], to_file=True)

        lane_dfs.append(file_dfs)

    distances = get_function_distances(lane_dfs[0], lane_dfs[1], names)
    pass
