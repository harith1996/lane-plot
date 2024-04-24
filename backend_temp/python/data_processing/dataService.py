import modin.pandas as pd
import numpy as np
from tqdm import tqdm

from data_processing.diffComputer import DiffComputer


class DataService:
    def __init__(
        self,
        df: pd.DataFrame,
        fieldTypeMap: dict,
        idFieldName: str = "unique_id",
        fileName: str = None,
    ):
        self.df = df
        self.fieldTypeMap = fieldTypeMap
        self.idFieldName = idFieldName
        self.df[self.idFieldName] = list(range(df.shape[0]))
        self.diffBy = None
        self.sliceBy = None
        # split filename to get diffBy and sliceBy
        if fileName != None:
            self.parse_filename(fileName)
    
    def parse_filename(self, fileName: str):
        fileName = fileName.split("/")[-1]
        fileName = fileName.split(".")[0]
        fileName = fileName.split(",")
        self.diffBy = fileName[0].split("=")[1]
        self.sliceBy = fileName[1].split("=")[1]

    def split_time(self, timeFieldName):
        df = self.df
        df[timeFieldName] = pd.to_datetime(df[timeFieldName])
        df["Year"] = df[timeFieldName].dt.year
        df["Month"] = df[timeFieldName].dt.month
        df["Day"] = df[timeFieldName].dt.day
        df["Day of Week"] = df[timeFieldName].dt.dayofweek
        df["Hour"] = df[timeFieldName].dt.hour
        try:
            df[timeFieldName] = df.apply(
                lambda x: x[timeFieldName].tz_convert("utc").tz_localize(None), axis=1
            )
        except:
            df["Timestamp"] = pd.to_timedelta(
                df[timeFieldName] - pd.Timestamp("1970-01-01"), unit="S"
            ) // pd.Timedelta("1s")

    def add_time_till_event(
        self,
        event_time_str: str,
        as_name: str = "time_till",
        time_column_name: str = "event_timestamp",
    ):
        df = self.df
        df[as_name] = (
            df[time_column_name] - pd.Timestamp(event_time_str)
        ) // pd.Timedelta("1s")
        # return dataframe
        return df

    def get_eq_filtered_data(self, columns, filter_col, filter_val):
        df = self.df
        out_attributes = columns + [self.idFieldName]
        df_filtered = None
        if filter_col != None:
            df_filtered = df[df[filter_col].astype(str) == str(filter_val)]
        df_filtered = df_filtered[out_attributes]
        return df_filtered.to_json(orient="values")

    def get_sorted_df(self, sortBy: str, df=None):
        sortedDf = df.sort_values(by=sortBy, kind="stable")
        return sortedDf

    def get_filtered_df(self, filterBy: str, filterValue: str, df=None):
        filteredDf = df[df[filterBy].astype(str) == str(filterValue)]
        return filteredDf

    def get_filter_values(self, filterMap: dict, df=None):
        df = self.df
        out = {
            "linearizeBy": [],
            "sliceBy": [],
            "sliceByValue": [],
            "shownPlots": [],
            "eventType": [],
        }
        # get default values from diffby and linearizeBy in file name
        for filterName in filterMap:
            match filterName:
                case "linearizeBy":
                    out[filterName] = []
                case "sliceBy":
                    out[filterName] = [self.sliceBy]
                case "sliceByValue":
                    match filterMap["sliceBy"]:
                        case _:
                            slices = df.groupby(self.sliceBy).size()
                            out[filterName] = slices.sort_values(ascending=False).keys().tolist()
                case "shownPlots":
                    out[filterName] = ["size", "timestamp", "relSize", "relDiff"]
                case "eventType":
                    out[filterName] = []
                case _:
                    out[filterName] = []
        return out

    def get_diff_col_names(self, relative=False):

        [nextCol, prevCol] = ["diffNext", "diffLast"]
        if relative:
            [nextCol, prevCol] = ["relDiffNext", "reldiffLast"]
        return [nextCol, prevCol]

    # TODO: add values directly to dataframe
    def get_diff_list(self, fieldName, linearizeBy, relative=False, df=None):
        # sort dataframe by df
        sortedDf = self.get_sorted_df(linearizeBy, df)
        # get list of values for column fieldName
        filteredDf = sortedDf[[self.idFieldName, fieldName]]
        keyValuePairs = filteredDf.values.tolist()
        try:
            keyValuePairs = list(filter(lambda x: not np.isnan(x[1]), keyValuePairs))
        except:
            keyValuePairs = list(filter(lambda x: x[1] != None, keyValuePairs))
        values = list(map(lambda x: x[1], keyValuePairs))
        fieldType = None
        try:
            fieldType = self.fieldTypeMap[fieldName]
        except:
            fieldType = self.df.dtypes[fieldName].name

        # initialize diffComputer
        diffC = DiffComputer(fieldType, relative=relative)

        [nextCol, prevCol] = self.get_diff_col_names(relative)
        # compute diffs
        diffList = []
        if len(values) == 1:
            diffList = []
        else:
            for i in range(len(values)):
                item = {}
                if i == 0:
                    item[prevCol] = None
                    item[nextCol] = diffC.compute_diff(values[i + 1], values[i])
                elif i == len(values) - 1:
                    item[prevCol] = diffC.compute_diff(values[i - 1], values[i])
                    item[nextCol] = None
                else:
                    item[prevCol] = diffC.compute_diff(values[i - 1], values[i])
                    item[nextCol] = diffC.compute_diff(values[i + 1], values[i])

                item[self.idFieldName] = int(keyValuePairs[i][0])
                diffList.append(item)
        return list(diffList)

    # filter data points within a rectangular extent, defined by points x1,y1 and x2,y2
    # x1,y1= top-left corner
    # x2,y2 = bottom-right corner
    def get_data_in_extent(
        self, xField, yField, x1, y1, x2, y2, queryFields
    ) -> pd.DataFrame:
        filtered_df = self.df[queryFields + [xField, yField, self.idFieldName]]
        filtered_df = filtered_df[
            (filtered_df[xField] >= float(x1)) & (filtered_df[xField] <= float(x2))
        ]
        filtered_df = filtered_df[
            (filtered_df[yField] >= float(y1)) & (filtered_df[xField] <= float(y2))
        ]
        return filtered_df

        # return list of diffs

    # TODO: improve performance
    def add_values_by_id(self, fieldName, keyValuePairs):
        df = self.df
        for keyValuePair in tqdm(keyValuePairs, desc="Mapping diffs"):
            df.loc[df[self.idFieldName] == int(keyValuePair[0]), fieldName] = (
                keyValuePair[1]
            )
        return df

    def get_human_readable_name(self, fieldName, fieldValue):
        df = self.df
        if fieldName == "article_id":
            # fetch the article from data
            article = df.loc[df["article_id"] == int(fieldValue)]
            return article["page_name"].iloc[0]
        elif fieldName == "page_name":
            return fieldValue
        
    def get_adjacent_event_ids(self, linearizeByField, sliceByField, sliceByValue, idFieldName, currentId):
        df = self.df
        # group dataframe by sliceByField
        groupedDf = df.groupby(sliceByField)
        # get the group with sliceByValue
        group = groupedDf.get_group(sliceByValue)
        # sort the group by linearizeByField
        sortedGroup = group.sort_values(by=linearizeByField, kind="stable")
        # get the index of the currentId
        currIndex = sortedGroup[sortedGroup[idFieldName] == int(currentId)].index[0]
        # get the previous and next rows
        prevRow = sortedGroup.loc[currIndex - 1]
        nextRow = sortedGroup.loc[currIndex + 1]
        return {
            "prevId": str(prevRow[idFieldName]),
            "currId": str(currentId),
            "nextId": str(nextRow[idFieldName])
        }