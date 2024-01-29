import modin.pandas as pd
import numpy as np
from tqdm import tqdm

from data_processing.diffComputer import DiffComputer


class DataService:
    def __init__(
        self, df: pd.DataFrame, fieldTypeMap: dict, idFieldName: str = "unique_id"
    ):
        self.df = df
        self.fieldTypeMap = fieldTypeMap
        self.idFieldName = idFieldName
        self.df[self.idFieldName] = list(range(df.shape[0]))

    def split_time(self, timeFieldName):
        df = self.df
        df[timeFieldName] = pd.to_datetime(df[timeFieldName])
        df["Year"] = df[timeFieldName].dt.year
        df["Month"] = df[timeFieldName].dt.month
        df["Day"] = df[timeFieldName].dt.day
        df["Day of Week"] = df[timeFieldName].dt.dayofweek
        df["Hour"] = df[timeFieldName].dt.hour
        # df[timeFieldName] = df.apply(lambda x: x[timeFieldName].tz_convert("utc").tz_localize(None), axis=1)
        df["Timestamp"] = pd.to_timedelta(df[timeFieldName] - pd.Timestamp("1970-01-01"), unit="S") // pd.Timedelta('1s')

    def get_eq_filtered_data(
        self,
        columns,
        filter_col,
        filter_val,
    ):
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
        out = {
            "linearizeBy": [],
            "sliceBy": [],
            "sliceByValue": [],
            "shownPlots": [],
            "eventType": [],
        }
        #get default values from diffby and linearizeBy in file name
        for filterName in filterMap:
            match filterName:
                case "linearizeBy":
                    out[filterName] = []
                case "sliceBy":
                    out[filterName] = [
                        "article_id",
                        "event_user_id",
                    ]
                case "sliceByValue":
                    match filterMap["sliceBy"]:
                        case "article_id":
                            out[filterName] = [
                                "49514870",
                                "52547512",
                                "37816935",
                                "54266373",
                                "45623450",
                            ]
                        case "event_user_id":
                            out[filterName] = [
                                "3455093",
                                "7903804",
                                "7852030",
                                "2842084",
                                "15996738",
                            ]
                        case _:
                            out[filterName] = []
                case "shownPlots":
                    out[filterName] = ["diff", "time_stamp"]
                case "eventType":
                    out[filterName] = []
                case _:
                    out[filterName] = []
        return out

    # TODO: add values directly to dataframe
    def get_diff_list(self, fieldName, linearOrderBy, df=None):
        # sort dataframe by df
        sortedDf = self.get_sorted_df(linearOrderBy, df)
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
        diffC = DiffComputer(fieldType, relative=True)

        # compute diffs
        diffList = []
        if len(values) == 1:
            diffList = []
        else:
            for i in range(len(values)):
                item = {}
                if i == 0:
                    item["diffPrev"] = None
                    item["diffNext"] = diffC.compute_diff(values[i + 1], values[i])
                elif i == len(values) - 1:
                    item["diffPrev"] = diffC.compute_diff(values[i - 1], values[i])
                    item["diffNext"] = None
                else:
                    item["diffPrev"] = diffC.compute_diff(values[i - 1], values[i])
                    item["diffNext"] = diffC.compute_diff(values[i + 1], values[i])

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
            df.loc[
                df[self.idFieldName] == int(keyValuePair[0]), fieldName
            ] = keyValuePair[1]
        return df
