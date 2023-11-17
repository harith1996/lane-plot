import pandas as pd
from wikipedia_article_parser import get_list_from_table

def get_dataframe(filename, chunksize=300):
    column_names = get_list_from_table("https://wikitech.wikimedia.org/wiki/Analytics/Data_Lake/Edits/Mediawiki_history_dumps", 1, "Field name")
    reader = pd.read_csv(filename, iterator=True, sep="\t", names=column_names)
    df = reader.get_chunk(chunksize)
    for col in df.columns:
        if("timestamp" in col):
            df[col] = pd.to_datetime(df[col])
    return df

filename = "./raw_dumps/2023-10.enwiki.2023-10.tsv"
df = get_dataframe(filename)
print(df.head())
print(df.shape)