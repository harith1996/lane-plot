import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_list_from_table(wikiurl, table_num, column_name):
    wikiurl="https://wikitech.wikimedia.org/wiki/Analytics/Data_Lake/Edits/Mediawiki_history_dumps"
    table_class="wikitable sortable jquery-tablesorter"
    response=requests.get(wikiurl)
    print(response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    indiatable=soup.findAll('table',{'class':"wikitable"})[table_num]
    df=pd.read_html(str(indiatable))
    # convert list to dataframe
    df=pd.DataFrame(df[0])
    columns = df[column_name].to_list()
    return columns