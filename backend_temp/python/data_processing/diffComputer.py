import pandas as pd
class DiffComputer:
    def __init__(self, dataType, relative = True):
        self.dataType = dataType
        self.relative = relative

    def compute_diff(self, v1, v2):
        out = None
        match self.dataType:
            case "dateTime": 
                out = float(pd.Timedelta(v1 - v2).seconds)
            case _:
                out = float(v1) - float(v2)
                if (self.relative == True):
                    if(v1 != 0):
                        out = (out / float(v1)) * 100
                    else:
                        out = 1
        return out

