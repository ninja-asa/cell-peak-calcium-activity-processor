import os
import logging

# load logging level from environment variable
log_level = os.getenv("LOG_LEVEL", "INFO")
LOGGING_CONFIG = {
    "format": '%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
    "level": log_level,
    "handlers": [logging.StreamHandler(), logging.FileHandler(f"{__name__}.log")]
}

PEAK_THRESHOLD = os.getenv("PEAK_THRESHOLD", 0.4)
PEAK_WINDOW = os.getenv("PEAK_WINDOW", 5)
TIME_UNIT = os.getenv("TIME_UNIT", "s")
IGNORE_PEAKS_BEFORE_CRITERIA = os.getenv("IGNORE_PEAKS_BEFORE_CRITERIA", "samples")
IGNORE_PEAKS_BEFORE = os.getenv("IGNORE_PEAKS_BEFORE", 1)
OUTPUT_DIRECTORY = os.getenv("OUTPUT_DIRECTORY", "output") 

class AppConfig:
    def __init__(self) -> None:
        self._log_level = LOGGING_CONFIG["level"]
        self._peak_threshold = PEAK_THRESHOLD
        self._peak_window = PEAK_WINDOW
        self._time_unit = TIME_UNIT
        self._ignore_peaks_before_criteria = IGNORE_PEAKS_BEFORE_CRITERIA
        self._ignore_peaks_before = IGNORE_PEAKS_BEFORE
        self._output_directory = OUTPUT_DIRECTORY

    def __repr__(self) -> str:
        return f"AppConfig(log_level={self.log_level}, threshold={self.threshold}, n_neighbors={self.n_neighbors}, time_unit={self.time_unit}, ignore_peaks_before_criteria={self.ignore_peaks_before_criteria}, ignore_peaks_before={self.ignore_peaks_before}, output_directory={self.output_directory})"

    @property
    def log_level(self) -> str:
        return self._log_level
    
    @property
    def threshold(self) -> float:
        return float(self._peak_threshold)
    
    @property
    def n_neighbors(self) -> int:
        return int(self._peak_window)
    
    @property
    def time_unit(self) -> str:
        return self._time_unit
    
    @property
    def ignore_peaks_before_criteria(self) -> str:
        return self._ignore_peaks_before_criteria
    
    @property
    def ignore_peaks_before(self) -> int:
        return int(self._ignore_peaks_before)
    
    @property
    def output_directory(self) -> str:
        return self._output_directory
    