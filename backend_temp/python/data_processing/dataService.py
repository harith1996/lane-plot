import pandas as pd
import numpy as np

from diffComputer import DiffComputer


class DataService:
    def __init__(self, df: pd.DataFrame, fieldTypeMap: dict):
        self.df = df
        self.fieldTypeMap = fieldTypeMap
        self.df["unique_id"] = list(range(df.shape[0]))

    def split_time(self, timeFieldName):
        df = self.df
        df["Time"] = pd.to_datetime(df[timeFieldName])
        df["Year"] = df["Time"].dt.year
        df["Month"] = df["Time"].dt.month
        df["Day"] = df["Time"].dt.day
        df["Day of Week"] = df["Time"].dt.dayofweek
        df["Hour"] = df["Time"].dt.hour
        df["Timestamp"] = (df["Time"] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

    def get_filtered_data(
        self,
        APP_ROOT,
        x_axis,
        y_axis,
        nullColumnName,
        run_pivot_column,
        run_pivot_value,
    ):
        df = self.df
        df_filtered = None
        df_filtered = df[df[run_pivot_column].astype(str) == str(run_pivot_value)]
        df_filtered = df_filtered[[x_axis, y_axis, nullColumnName, "unique_id"]]
        return df_filtered.to_json(orient="values")

    def get_null_perc(self, targetAtts, runPivotAtt):
        df = self.df
        unique_pivot_values = df[runPivotAtt].unique()
        unique_pivot_values = sorted(unique_pivot_values)
        out = []
        for t in targetAtts:
            null_perc = {"targetAtt": str(t)}
            for value in unique_pivot_values:
                null_perc["runPivotValue"] = str(value)
                df_filtered = df[df[runPivotAtt] == value]
                null_perc["nullPerc"] = df_filtered[t].isnull().sum() / len(df_filtered)
                out.append(null_perc.copy())
        return list(out)

    def get_sorted_df(self, sortBy: str):
        df = self.df
        sortedDf = df.sort_values(by=sortBy, kind="stable")
        return sortedDf

    def get_diff_list(self, fieldName, linearOrderBy):
        df = self.df
        # sort dataframe by df
        sortedDf = self.get_sorted_df(linearOrderBy)
        # get list of values for column fieldName
        filteredDf = sortedDf[["unique_id", fieldName]]
        keyValuePairs = filteredDf.values.tolist()
        keyValuePairs = list(filter(lambda x: not np.isnan(x[1]), keyValuePairs))
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

            item["unique_id"] = int(keyValuePairs[i][0])
            diffList.append(item)
        return list(diffList)

    # filter data points within a rectangular extent, defined by points x1,y1 and x2,y2
    # x1,y1= top-left corner
    # x2,y2 = bottom-right corner
    def get_data_in_extent(
        self, xField, yField, x1, y1, x2, y2, queryFields
    ) -> pd.DataFrame:
        filtered_df = self.df[queryFields + [xField, yField, "unique_id"]]
        filtered_df = filtered_df[
            (filtered_df[xField] >= float(x1))
            & (filtered_df[xField] <= float(x2))
        ]
        filtered_df = filtered_df[
            (filtered_df[yField]>= float(y1))
            & (filtered_df[xField] <= float(y2))
        ]
        return filtered_df

        # return list of diffs

    def add_values_by_id(self, fieldName, keyValuePairs):
        df = self.df
        for keyValuePair in keyValuePairs:
            df.loc[df["unique_id"] == int(keyValuePair[0]), fieldName] = keyValuePair[1]
        return df