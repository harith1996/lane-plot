import nltk
nltk.download('averaged_perceptron_tagger')
import pandas as pd
import matplotlib.pyplot as plt
import os

FILES = os.listdir("books/")
CONTENT_TAGS = ["FW", "JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS", "WRB", "VBZ", "VBP", "VBN", "VBG", "VBD", "VB", "RBS", "RB", "RBR"]
FUNCTION_TAGS = ["CC", "CD", "DT", "EX", "IN", "LS", "MD", "PDT", "WP$", "WP", "WDT", "UH", "TO", "RP", "PRP", "PRP$"]

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

def group_plot(df, file="", title=""):
    group_df = df.groupby(["last_f", "next_f"]).size().reset_index(name='count')
    plt.scatter(group_df["last_f"], group_df["next_f"], c=group_df["count"], cmap="viridis")

    plot_title = file+" LaNe chart "+title
    plt.title(plot_title)
    plt.xlabel("last_word")
    plt.ylabel("next_word")
    plt.colorbar()
    plt.ylim([0,40])
    plt.xlim([0,40])
    plt.savefig("plots/"+plot_title+".png")
    plt.clf()

if __name__ == "__main__":
    for file in FILES:
        with open("books/"+file, "r", encoding="utf8") as f:
            text = f.read()

        text = text.replace("\n", " ").lower()

        df = word_distance_type(text)
        group_plot(df, file, "function word")

        df_word = df[df["word"] == "the"]
        group_plot(df_word, file, "-the- word")

        df_word = df[df["word"] == "from"]
        group_plot(df_word, file, "-from- word")

        df_word = df[df["word"] == "and"]
        group_plot(df_word, file, "-and- word")
