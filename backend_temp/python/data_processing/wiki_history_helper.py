#methods to parse the wiki history data
import pandas as pd

def get_page_with_max_edits(df : pd.DataFrame):
    #filter out non-edit rows
    # df = df[df["event_entity"] == "revision"]
    
    #group by page_id and count number of edits
    df = df.groupby("article_id").count()
    
    #sort by number of edits
    df = df.sort_values(by="rev_id", ascending=False)
    
    #return page_id with most edits
    return df.index[0]

def get_user_with_max_edits(df : pd.DataFrame):
    #filter out non-edit rows
    df = df[df["event_entity"] == "revision"]
    
    #group by page_id and count number of edits
    df = df.groupby("event_user_id").count()
    
    #sort by number of edits
    df = df.sort_values(by="event_type", ascending=False)
    
    #return page_id with most edits
    return df.index[0]

def add_is_reverted(df : pd.DataFrame, as_name : str = "is_reverted"):
    #get all revisions that are reverts
    #articles with "reverted" or "undid" in the comment are reverts
    reverted_revisions = df[df["tags"].str.contains("revert|undo", case=False, na=False)]
    reverted_revisions2 = df[df["comment"].str.contains("revert|undid|false|delete", case=False, na=False)]
    
    reverted_revisions = pd.concat([reverted_revisions, reverted_revisions2])
    #make a new Series with all False
    is_reverted = pd.Series([False] * len(df), index=df.index)
    
    #set all reverted revisions to True
    is_reverted[reverted_revisions.index] = True
    
    #add the new Series to the dataframe
    df[as_name] = is_reverted
    
    #return dataframe
    return df