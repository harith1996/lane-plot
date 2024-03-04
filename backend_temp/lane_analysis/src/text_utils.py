import string
import nltk
import pronouncing
import pandas as pd
import re

from backend_temp.lane_analysis.src.lane_utils import *

CONTENT_TAGS = ["FW"]

WORD_TAG_TYPES = ["F", "ADJ", "ADV", "N", "V", "U"]

STYLOMETYRIC_WORDS = ["the", "and", "to", "a", "an", "of", "in", "that", "those", "it", "not", "as", "with", "but",
                      "for", "at", "this", "these", "so", "all", "on", "from", "one", "ones", "up", "no", "out", "out",
                      "what", "then", "if", "there", "by", "who", "when", "into", "now", "down", "over", "back", "or",
                      "well", "which", "how", "here", "just", "very", "where", "before", "upon", "about", "after",
                      "more", "why", "some"]

PUNCTUATION_SIGNS = [".", ",", ";", ":"]

LETTERS = list(string.ascii_lowercase)


def classify_tag(tag):
    FUNCTION_TAGS = ["CC", "CD", "DT", "EX", "IN", "LS", "MD", "PDT", "WP$", "WP", "WDT", "UH", "TO", "RP", "PRP",
                     "PRP$"]
    ADJECTIVE_TAGS = ["JJ", "JJR", "JJS"]
    ADVERB_TAGS = ["WRB", "RBS", "RB", "RBR"]
    NOUN_TAGS = ["NN", "NNS", "NNP", "NNPS"]
    VERB_TAGS = ["VBZ", "VBP", "VBN", "VBG", "VBD", "VB"]

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

def tag_type_distance(tag, df_wtype, delta=1, mode="avg"):
    lane_func = delta_lane_avg if mode == "avg" else delta_lane_abs

    df_wtype = df_wtype[df_wtype["word_type"] == tag]
    df_wtype["pos"] = list(df_wtype.index)
    df_wtype.reset_index(drop=True, inplace=True)

    if len(df_wtype) <= delta:
        return pd.DataFrame()
    return lane_func(df_wtype, "pos", delta)


def word_type_distances(tokens, delta=1, mode="avg", tags=WORD_TAG_TYPES):
    assert mode in ["avg", "abs"]

    word_tags = nltk.pos_tag(tokens)

    df = pd.DataFrame(word_tags, columns=["word", "tag"])
    df["word_type"] = df["tag"].apply(classify_tag)

    if delta == 1:
        return simple_type_distance(df, tags=tags)

    lane_dfs = []
    for word_type in tags:
        df_wtype = tag_type_distance(word_type, df.copy(), delta=delta, mode=mode)
        lane_dfs.append(df_wtype)

    return lane_dfs


def simple_type_distance(df, tags=WORD_TAG_TYPES):
    lane_dfs = []
    for word_type in tags:
        df_wtype = df.copy()

        df_wtype = df_wtype[df_wtype["word_type"] == word_type]
        df_wtype["pos"] = list(df_wtype.index)

        df_wtype["last"] = df_wtype["pos"].diff()
        df_wtype["last"] = df_wtype["last"].fillna(0)

        df_wtype["next"] = df_wtype["pos"].shift(-1) - df_wtype["pos"]
        df_wtype["next"] = df_wtype["next"].fillna(0)

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

def cleanse_word(word):
    word = re.sub('[\d(),:.;?!“” ]', '', word)
    word = re.sub('’', "'", word)
    word = re.sub('œ', 'oe', word)
    return word

def lane_size(size_list, thres=0, element_content=None):
    last_list = []
    next_list = []

    keep_element = []

    start_index = len(size_list)

    for i, element in enumerate(size_list):
        keep_element.append(element >= thres)
        if element >= thres:
            last_list.append(float("-inf"))
            last = element

            start_index = i + 1
            break

    for element in size_list[start_index:]:
        keep_element.append(not (element < thres))
        if element < thres:
            continue
        diff = element - last
        next_list.append(-diff)
        last_list.append(diff)

        last = element

    if len(last_list) > 0:
        next_list.append(float("-inf"))

    # Loop to add only the contents of kept elements
    kept_size_list = []
    kept_element_content = []
    for i, keep in enumerate(keep_element):
        if keep:
            kept_size_list.append(size_list[i])
            if element_content:
                kept_element_content.append(element_content[i])

    if element_content:
        df = pd.DataFrame({'last': last_list, 'next': next_list, 'size': kept_size_list, 'content': kept_element_content})
    else:
        df = pd.DataFrame({'last': last_list, 'next': next_list, 'size': kept_size_list})

    df["count"] = 1
    df = df.groupby(["last", "next"]).agg({'size': 'mean', 'count': 'sum'}).rename(columns={'size': 'mean_size', 'count': 'count'}).reset_index()

    return df

def count_syllables(lines):
    syllable_list = []
    kept_lines = []
    for line in lines:
        syllables = 0
        for word in line.split():
            word = cleanse_word(word)
            if word in ["", "'", "-", "—"]:
                continue

            phones = pronouncing.phones_for_word(word)
            if phones:
                syllables += sum([pronouncing.syllable_count(p) for p in phones[0]])
            else:
                last_vowel = False
                for letter in word:
                    if letter in ["a", "e", "i", "o", "u"]:
                        if not last_vowel:
                            syllables += 1
                        last_vowel = True
                    else:
                        last_vowel = False

        if syllables > 0:
            syllable_list.append(syllables)
            kept_lines.append(line)
    return syllable_list, kept_lines