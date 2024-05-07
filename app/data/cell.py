from dataclasses import dataclass
import pandas as pd
import os
import logging
# load logging level from environment variable
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s', level=log_level, handlers=[logging.StreamHandler(), logging.FileHandler(f"{__name__}.log")])

@dataclass
class CellActivity:
    cell_id: str
    time_to_first_peak: pd.Timestamp = None
    value_at_first_peak: float = None
    time_to_max_peak: pd.Timestamp = None
    value_at_max_peak: float = None
    is_active: bool = False
    nr_peaks: int = 0
    
    @classmethod
    def from_peaks(cls, peaks: pd.Series) -> "CellActivity":
        """
        Initialize the class from a pandas Series containing the peaks

        Args:
            peaks (pd.Series): A pandas Series containing the peaks

        Returns:
            None
        """
        cell_id = peaks.name
        # initialize the class
        instance = cls(str(cell_id))
        # set the cell ID
        # set the number of peaks
        instance.nr_peaks = len(peaks)
        # if there are no peaks, set cell as inactive
        if instance.nr_peaks == 0:
            return instance

        # set the activity status
        instance.is_active = True
        # set the time and value to first peak
        instance.time_to_first_peak, instance.value_at_first_peak = instance.get_first_peak(peaks)

        # set the time and value to max peak
        instance.time_to_max_peak, instance.value_at_max_peak = instance.get_greatest_peak(peaks)

        return instance
    
    def to_series(self):
        return pd.Series({
            "time_to_first_peak": self.time_to_first_peak.to_pydatetime().timestamp() if self.time_to_first_peak else None,
            "value_at_first_peak": self.value_at_first_peak,
            "time_to_max_peak": self.time_to_max_peak.to_pydatetime().timestamp() if self.time_to_max_peak else None,
            "value_at_max_peak": self.value_at_max_peak,
            "is_active": self.is_active,
            "nr_peaks": self.nr_peaks
        }, name=self.cell_id)
    
    def get_greatest_peak(self, peaks: pd.Series):
        return (peaks.idxmax(), peaks.max())
    
    def get_first_peak(self, peaks: pd.Series):
        """
        Get the first peak in the peaks Series

        Args:
            peaks (pd.Series): The peaks Series

        Returns:
            tuple: The index and value of the first peak
        """
        return (peaks.index[0], peaks.iloc[0])