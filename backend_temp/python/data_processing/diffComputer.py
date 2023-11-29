import pandas as pd
class DiffComputer:
    def __init__(self, dataType, relative = True):
        self.dataType = dataType
        self.relative = relative

    def compute_diff(self, v1, v2):
        out = None
        match self.dataType:
            case "dateTime": 
                #check which date comes later
                if(v1 > v2):
                    out = float(pd.Timedelta(v1 - v2).seconds)
                else:
                    out = float(pd.Timedelta(v2 - v1).seconds)
            case _:
                out = float(v1) - float(v2)
                if (self.relative == True):
                    if(v1 != 0):
                        out = (out / float(v1)) * 100
                    else:
                        out = 1
        return out

