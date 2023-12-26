import nltk
nltk.download('averaged_perceptron_tagger')
import pandas as pd
import matplotlib.pyplot as plt
import os

FILES = os.listdir("books/")
FILES = ["2020_trump.txt", "2021_biden.txt"]

CONTENT_TAGS = ["FW", "JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS", "WRB", "VBZ", "VBP", "VBN", "VBG", "VBD", "VB", "RBS", "RB", "RBR"]
FUNCTION_TAGS = ["CC", "CD", "DT", "EX", "IN", "LS", "MD", "PDT", "WP$", "WP", "WDT", "UH", "TO", "RP", "PRP", "PRP$"]

STYLOMETYRIC_WORDS = ["the", "and", "to", "a", "an", "of", "in", "that", "those", "it", "not", "as", "with", "but", "for", "at", "this", "these", "so", "all", "on", "from", "one", "ones", "up", "no", "out", "out", "what", "then", "if", "there", "by", "who", "when", "into", "now", "down", "over", "back", "or", "well", "which", "how", "here", "just", "very", "where", "before", "upon", "about", "after", "more", "why", "some"]

def classify_tag(tag):
    if tag in CONTENT_TAGS:
        return "C"
    elif tag in FUNCTION_TAGS:
        return "F"
    else:
        return "O"

def word_distance_type(text):
    tokens = nltk.word_tokenize(text)
    word_tags = nltk.pos_tag(tokens)

    df = pd.DataFrame(word_tags, columns=["word", "tag"])
    df["word_type"] = df["tag"].apply(classify_tag)

    function_words = df.copy()

    function_words = function_words[function_words["word_type"] == "F"]
    function_words["pos_f"] = list(function_words.index)

    function_words["last_f"] = function_words["pos_f"].diff()
    function_words["last_f"].fillna(-1)

    function_words["next_f"] = function_words["pos_f"].shift(-1) - function_words["pos_f"]
    function_words["next_f"].fillna(-1)

    return function_words

def lane_plot(df, file="", title="", to_file=True):
    # group_df = df.groupby(["last_f", "next_f"]).size().reset_index(name='count')
    plt.scatter(df["last_f"], df["next_f"], c=df["count"], cmap="viridis")

    plot_title = file+" LaNe chart "+title
    plt.title(plot_title)
    plt.xlabel("last_word")
    plt.ylabel("next_word")
    plt.colorbar()
    plt.ylim([0, 40])
    plt.xlim([0, 40])
    if to_file:
        plt.savefig("plots/" + plot_title + ".png")
    else:
        plt.show()
    plt.clf()

def get_stylometric_signature(df):
    dfs = []

    # df_word = df[df["word"].isin(STYLOMETYRIC_WORDS)]
    # df_word = df_word.groupby(["last_f", "next_f"]).size().reset_index(name='count')
    # return df_word

    for word in STYLOMETYRIC_WORDS:
        df_word = df[df["word"] == word]
        df_word = df_word.groupby(["last_f", "next_f"]).size().reset_index(name='count')

        # Normalize count values
        df_word["count"] = df_word["count"]/len(df)

        df_word["word"] = word
        dfs.append(df_word)

    return dfs

def get_lane_distance(df1, df2, max_word_distance=40):
    dist_sum = 0.
    sum_counts = 0.
    for i in range(1, max_word_distance+1):
        for j in range(1, max_word_distance+1):
            count_1 = df1[(df1["last_f"] == i) & (df1["next_f"] == j)]["count"]
            count_2 = df2[(df2["last_f"] == i) & (df2["next_f"] == j)]["count"]

            if len(count_1) == 0:
                count_1 = 0.
            else:
                count_1 = count_1.iloc[0]
            if len(count_2) == 0:
                count_2 = 0.
            else:
                count_2 = count_2.iloc[0]

            dist_sum += abs(count_1-count_2)
            sum_counts += count_1 + count_2

    if sum_counts == 0.:
        return 0., 0.
    return dist_sum/sum_counts, sum_counts


def get_function_distances(dfs1, dfs2):
    dists = []
    counts = []
    for df1, df2 in zip(dfs1, dfs2):
        dist, count = get_lane_distance(df1, df2)
        dists.append(dist)
        counts.append(count)
    return pd.DataFrame({'word': STYLOMETYRIC_WORDS, 'distance': dists, 'count': counts})


if __name__ == "__main__":
    df_signs_list = []
    for file in FILES:
        with open("state_of_union/"+file, "r", encoding="utf8") as f:
            text = f.read()

        text = text.replace("\n", " ").lower()

        df = word_distance_type(text)

        df_signs = get_stylometric_signature(df)
        for i, sign in enumerate(df_signs):
            continue
            lane_plot(sign, file=file, title=STYLOMETYRIC_WORDS[i], to_file=True)

        df_signs_list.append(df_signs)

    distances = get_function_distances(df_signs_list[0], df_signs_list[1])
    pass