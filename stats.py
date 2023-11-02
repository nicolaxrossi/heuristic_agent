import pandas as pd


class Statistics:
    
    def __init__(self, columns:[str]):
        """ instantiate a new Pandas DataFrame, with columns specified """
        self.sample = pd.DataFrame(columns=columns)
        self.size = 0
        
    def insert_record(self, observation):
        """ observation is a non-empty list of measurements taken over different quantities
            such a list is appended at the end of the dataframe, as the i-th observation. """
        
        self.sample.loc[self.size] = observation
        self.size += 1
        
    def mean(self, column):
        """ returns the sample mean of the variable (column) specified """
        return self.sample[column].mean()
    
    def st_dev(self, column):
        """ returns the sample standard deviation of the variable (column) specified """
        return self.sample[column].std()
    
    def retrieve_observation(self, index):
        """ returns the i-th observation (i-th row) in the dataframe """
        return pd.DataFrame(self.sample.iloc[index,:]).T
    
    def cumulative_sum(self, column):
        """ returns the cumulative sum of column's values """
        return self.sample[column].sum()
    
    def view(self):
        return self.sample