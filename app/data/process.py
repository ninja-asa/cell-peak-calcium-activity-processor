import pandas as pd
import os
import logging
import numpy as np
from scipy.signal import argrelmax

from app.data.population import CellPopulationActivity
from app.data.cell import CellActivity

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s', level=log_level, handlers=[logging.StreamHandler(), logging.FileHandler(f"{__name__}.log")])

class ActivityProcessor:
    def __init__(self, threshold: float, n_neighbors: int = 3):
        self.threshold = threshold
        self.n_neighbors = n_neighbors
        logging.info(f"ActivityProcessor initialized with threshold {threshold} and n_neighbors {n_neighbors}")

    def _sanity_check_data(self, cell_population_activity: CellPopulationActivity) -> None:
        """
        Check if the data is valid

        Args:
            cell_population_activity (CellPopulationActivity): The cell population activity

        Raises:
            error: if the data is not a CellPopulationActivity
            error: if the data is not a pandas DataFrame
            error: if the data is empty
            error: if the index is not a datetime index
            error: if the columns are not numerical
        """
        
        if not isinstance(cell_population_activity, CellPopulationActivity):
            error = ValueError("Data must be a CellPopulationActivity")
            logging.error(error)
            raise error
        if not isinstance(cell_population_activity.data, pd.DataFrame):
            error = ValueError("Data must be a pandas DataFrame")
            logging.error(error)
            raise error
        # check if there is data
        if cell_population_activity.data.empty:
            error = ValueError("Data must not be empty")
            logging.error(error)
            raise error
        # check if index is datetime index
        if not isinstance(cell_population_activity.data.index, pd.DatetimeIndex):
            error = ValueError("Data index must be a datetime index")
            logging.error(error)
            raise error
        # check if dtypes of columns are numerical
        if not cell_population_activity.data.dtypes.apply(pd.api.types.is_numeric_dtype).all():
            error = ValueError("Data columns must be numerical")
            logging.error(error)
            raise error
        return       
        

    def run(self, cell_population_activity: CellPopulationActivity) -> pd.DataFrame:
        """
        Process the cell population activity and return a summary DataFrame

        Args:
            cell_population_activity (CellPopulationActivity): The cell population activity

        Returns:
            pd.DataFrame: The summary DataFrame with the activity features of each cell
        """
        
        self._sanity_check_data(cell_population_activity)
        
        summary_df = self._initialize_summary_df(cell_population_activity)
        for column in cell_population_activity.data.columns:
            cell_activity_row: pd.DataFrame = self.process_cell_activity(cell_population_activity.data[column])
            summary_df.update(cell_activity_row)
        
        # sort the index alphabetically
        summary_df = summary_df.sort_index()
        
        return summary_df

    def _initialize_summary_df(self, cell_population_activity: CellPopulationActivity) -> pd.DataFrame:
        """
        Initialize the summary DataFrame, where the columns are the same as the data DataFrame

        Args:
            cell_population_activity (CellPopulationActivity): The cell population activity

        Returns:
            pd.DataFrame: The initialized summary DataFrame
        """
        summary_df = pd.DataFrame(CellActivity("").to_df(), index=cell_population_activity.data.columns)
        return summary_df
    
    def process_cell_activity(self, cell_activity_time_series: pd.Series) :
        """
        Process the cell activity time series and return a series with the summary of the activity

        Args:
            cell_activity_time_series (pd.Series): The cell activity time series

        Returns:
            pd.DataFrame: The summary of the cell activity - each column is a feature
        """
        peaks: pd.Series = self.get_local_maxima_per_column(cell_activity_time_series, self.n_neighbors, self.threshold)
        cell_activity: CellActivity = CellActivity.from_peaks(peaks)
        return cell_activity.to_df()
    
    @staticmethod
    def get_local_maxima_per_column(series: pd.Series, n_neighbors: int = 3, threshold: float = None) -> pd.Series:
        """
        Find the local maxima in the data and return only those rows

        Args:
            data (pd.Series): datetime index and columns with numerical values
            threshold (float): The threshold to consider a value as a local maxima

        Returns:
            pd.Series: The rows that are local maxima
        """
        if not isinstance(series, pd.Series):
            error = ValueError("Data must be a pandas Series")
            logging.error(error)
            raise error
        if threshold is None:
            threshold = series.mean()
        idx_local_maxima = argrelmax(series.values, order=n_neighbors)[0]
        is_local_maxima = pd.Series(False, index=series.index)
        is_local_maxima.iloc[idx_local_maxima] = series.iloc[idx_local_maxima] >= threshold
        return series[is_local_maxima]
    
    @staticmethod
    def summary_of_population(cell_population_activity_features: pd.DataFrame):
        """
        Get mean, nr of instances and % number of each column in the cell population activity features

        Args:
            cell_population_activity_features (pd.DataFrame): The cell population activity features (each row
                represents a cell and each column represents a feature)

        Returns:
            pd.Series: The mean of each column in the cell population activity features
        """
        total_instances = pd.Series(
            {
                "total_instances": cell_population_activity_features.shape[0]
            }
        )
        # for column which are numeric get the mean
        # find numeric columns and determine average
        numeric_features = cell_population_activity_features.select_dtypes(include=[np.number])

        mean_features:pd.Series = numeric_features.mean()
        # update the index to include "mean " before to each index value
        mean_features.index = mean_features.index.map(lambda x: 'mean ' + x)

        # convert to boolean columns whose name contains "is", for example "is_active"

        #convert column to boolean
        candidate_boolean_features = [col for col in cell_population_activity_features.columns if "is" in col]
        for column in candidate_boolean_features:
            cell_population_activity_features[column] = cell_population_activity_features[column].astype(bool)

        # find boolean columns and count total number of rows, total number of true and % of true
        boolean_features = cell_population_activity_features.select_dtypes(include=[bool])
        nr_true = boolean_features.sum()
        percent_true = nr_true / total_instances[0] * 100
        
        nr_true.index = nr_true.index.map(lambda x: 'nr_true ' + x)
        percent_true.index = percent_true.index.map(lambda x: 'percentage_true ' + x)
        
        # combine all features
        summary = pd.concat([mean_features, nr_true, percent_true, total_instances], axis=0).transpose()
        return summary
        
