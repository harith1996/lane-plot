#methods to parse the wiki history data
import pandas as pd

def get_page_with_max_edits(df : pd.DataFrame):
    #filter out non-edit rows
    df = df[df["event_entity"] == "revision"]
    
    #group by page_id and count number of edits
    df = df.groupby("page_id").count()
    
    #sort by number of edits
    df = df.sort_values(by="event_type", ascending=False)
    
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