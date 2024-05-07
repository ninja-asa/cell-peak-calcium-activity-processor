from dataclasses import dataclass
import os
import pandas as pd
import logging

# load logging level from environment variable
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s', level=log_level, handlers=[logging.StreamHandler(), logging.FileHandler(__name__)])

@dataclass
class CellPopulationActivity:
    ignore_peaks_before_criteria: str = "SAMPLES"
    ignore_peaks_before: int = 11
    time_unit: str = "s"
    # data attribute is not initialized in the __init__ method
    data: pd.DataFrame = None
    
    def __post_init__(self):
        # check if ignore criteria is either samples or time, if not raise an error
        if self.ignore_peaks_before_criteria.lower() not in ["samples", "time"]:
            error = ValueError("Ignore peaks before criteria must be either SAMPLES or TIME")
            logging.error(error)
            raise error
    
        # sanity check if provided unit is supported by pandas
        if self.time_unit not in ["s", "ms", "us", "ns"]:
            error = ValueError("Time unit must be either s, ms, us or ns")
            logging.error(error)
            raise error
        return
        
    def from_csv(self, path: str) -> None:
        data = pd.read_csv(path, index_col=None, header=0)
        # check if any column name contains "time". If so, set it as the index
        data = self.from_df(data)

    
    def from_df(self,data: pd.DataFrame) -> None:
        """
        Read the data from a pandas DataFrame and performs some data cleaning

        Args:
            data (pd.DataFrame): The data to be read
        """
        try:
            # check if any column name contains "time". If so, set it as the index
            self.set_time_column_as_index(data)
            # drop columns containing "frame"
            self.drop_frames_column(data)
            # 
            self.drop_rows(data)
        except ValueError as e:
            logging.error(e)
            raise e
        except Exception as e:
            logging.error(e)
            raise e
        finally:
        # transform the index to a timestamp index
            self.data = data

        logging.info(
            f"Data loaded successfully. Data shape: {self.data.shape}. Data columns: {self.data.columns}"
        )

        return
    
    def drop_frames_column(self, data, inplace: bool = True) -> pd.DataFrame:
        """
        Drop columns containing "frame" in the data

        Args:
            inplace (bool): If True, the data is modified in place. If False, a copy of the data is returned

        Returns:
            pd.DataFrame. Changes can be made in place
        """
        return data.drop(columns=[column for column in data.columns if "frame" in column.lower()], inplace=inplace)
    
    def drop_rows(self, data, threshold: float = None, inplace: bool =True) -> pd.DataFrame:
        """
        Drop rows where the value is below the specified threshold, based on the criteria specified in the ignore_peaks_before_criteria attribute.

        Args:
            threshold (float): The threshold below which rows are dropped
            inplace (bool): If True, the data is modified in place. If False, a copy of the data is returned

        Returns:
            pd.DataFrame. Changes can be made in place
        """
        if threshold is None:
            threshold = self.ignore_peaks_before
        # check criteria and drop rows accordingly
        if self.ignore_peaks_before_criteria.lower() == "samples":
            return self.drop_rows_before_sample(data, threshold_sample=threshold, inplace=inplace)
        elif self.ignore_peaks_before_criteria.lower() == "time":
            return self.drop_rows_before_time(data, threshold_time=threshold, inplace=inplace)
        else:
            logging.warning("Ignore peaks before criteria not recognized. No rows were dropped")
    
    def drop_rows_before_time(self, data, threshold_time: float = None, inplace: bool =True) -> pd.DataFrame:
        """
        Drop rows before the specified time (in the unit specified in the time_unit attribute)

        Args:
            time (int): The time to drop rows before. If not provided, the value of the ignore_peaks_before attribute is used 
            inplace (bool): If True, the data is modified in place. If False, a copy of the data is returned

        Returns:
            pd.DataFrame. Changes can be made in place
        """
        if threshold_time is None:
            threshold_time = self.ignore_peaks_before
        
        # convert the time to a timestamp
        threshold_time_timestamp = pd.to_datetime(threshold_time, unit=self.time_unit)
        # drop rows before the specified time, in place
        return data.drop(data.index[data.index < threshold_time_timestamp], inplace=inplace)

    def drop_rows_before_sample(self, data, threshold_sample: float = None, inplace: bool =True) -> pd.DataFrame:
        """
        Drop rows before the specified sample

        Args:
            threshold_sample (int): The sample to drop rows before. If not provided, the value of the ignore_peaks_before attribute is used 
            inplace (bool): If True, the data is modified in place. If False, a copy of the data is returned

        Returns:
            pd.DataFrame. Changes can be made in place
        """
        if threshold_sample is None:
            threshold_sample = self.ignore_peaks_before
        
        # drop rows before the index number `threshold_sample`

        return data.drop(data.index[:threshold_sample], inplace=inplace)
    
    def set_time_column_as_index(self, data):
        """
        Set the time column as the index of the data

        Args:
            data (pd.DataFrame): The data to be read. Expected to have a column containing "time". 
                If any column containing "frame" is found, it is dropped.

        Returns:    
            None. Changes are made in place

        Raises:
            ValueError: If no column containing "time" is found in the data
        """
        time_column = [column for column in data.columns if "time" in column.lower()]
        if len(time_column) == 0:
            error = ValueError("Time column not found in the data")
            logging.error(error)
            raise error
        # set the time column as the index
        data.set_index(time_column[0], inplace=True)
        data.index = pd.to_datetime(data.index, unit=self.time_unit)

    
    
    
    