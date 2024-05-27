from altair import to_json
from dotenv import load_dotenv

import os
import logging
import json

load_dotenv()

GITHUB_REPOSITORY_URL="https://github.com/ninja-asa/cell-peak-calcium-activity-processor"
# load logging level from environment variable
log_level = os.getenv("LOG_LEVEL", "INFO")
LOGGING_CONFIG = {
    "format": '%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
    "level": log_level,
    "handlers": [logging.StreamHandler(), logging.FileHandler(f"{__name__}.log")]
}
logging.basicConfig(**LOGGING_CONFIG)

PEAK_THRESHOLD = os.getenv("PEAK_THRESHOLD", 0.4)
PEAK_WINDOW = os.getenv("PEAK_WINDOW", 5)
TIME_UNIT = os.getenv("TIME_UNIT", "s")
IGNORE_PEAKS_BEFORE_CRITERIA = os.getenv("IGNORE_PEAKS_BEFORE_CRITERIA", "samples")
IGNORE_PEAKS_BEFORE = os.getenv("IGNORE_PEAKS_BEFORE", 1)
OUTPUT_DIRECTORY = os.getenv("OUTPUT_DIRECTORY", "output") 
FILTER_SETTINGS = os.getenv("FILTER_SETTINGS", "").split(";")
try:
    FILTERS = [(float(setting.split(",")[0]), setting.split(",")[1]) for setting in FILTER_SETTINGS if setting]
except Exception as e:
    logging.error(f"Error while parsing filters: {e}")
    FILTERS = []
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

class AppConfig:
    _supported_time_units = ["s", "ms", "us", "ns"]
    _supported_ignore_peaks_before_criteria = ["samples", "time"]
    _supported_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    _supported_filters = ["above", "below"]

    def __init__(self, custom_filters = None, time_unit = None, 
                    ignore_peaks_criteria = None,
                    ignore_peaks_before = None,
                    output_directory = None,
                    peak_threshold = None,
                    peak_window = None,
                    log_level = None
                 ) -> None:
        
        if custom_filters is not None:
            filters = custom_filters
        else: 
            filters = FILTERS
                    
        if not self.check_if_filters_are_valid(filters=filters):
            # no filters are set
            self._filters = []
            logging.warning("No filters are set. Please set filters in the format 'value,type' where type is either 'above' or 'below'")
            logging.warning("Assuming no filters are set")
        else:
            self._filters = filters
            
        if time_unit is None:
            time_unit = TIME_UNIT     
        
        if not self.check_if_time_unit_is_valid(time_unit):
            logging.warning(f"Time unit {self.time_unit} is not supported. Supported time units are {self._supported_time_units}")
            logging.warning("Assuming time unit is set to 's'")
            self._time_unit = "s"
        else:
            self._time_unit = time_unit
        
        if ignore_peaks_criteria is None:
            ignore_peaks_criteria = IGNORE_PEAKS_BEFORE_CRITERIA
        
        if not self.check_if_ignore_peaks_before_criteria_is_valid(ignore_peaks_criteria):
            logging.warning(f"Ignore peaks before criteria {self.ignore_peaks_before_criteria} is not supported. Supported criteria are {self._supported_ignore_peaks_before_criteria}")
            logging.warning("Assuming ignore peaks before criteria is set to 'samples'")
            self._ignore_peaks_before_criteria = "samples"
        else:
            self._ignore_peaks_before_criteria = ignore_peaks_criteria
            
        if log_level is None:
            log_level = LOG_LEVEL
        
        if not self.check_if_log_level_is_valid(log_level):
            logging.warning(f"Log level {self.log_level} is not supported. Supported log levels are {self._supported_log_levels}")
            logging.warning("Assuming log level is set to 'INFO'")
            self._log_level = "INFO"
        else:
            self._log_level = LOGGING_CONFIG["level"]
        
        self._peak_threshold = peak_threshold if peak_threshold is not None else PEAK_THRESHOLD
        self._peak_window = peak_window if peak_window is not None else PEAK_WINDOW
        self._ignore_peaks_before = ignore_peaks_before if ignore_peaks_before is not None else IGNORE_PEAKS_BEFORE
        self._output_directory = output_directory if output_directory is not None else OUTPUT_DIRECTORY

    def check_if_filters_are_valid(self, filters: list) -> bool:
        # check if first tuple element is a number (int, float)
        are_types_valid = all(isinstance(setting[0], (int, float)) for setting in filters)
        are_values_valid = all(setting[1] in self._supported_filters for setting in filters)
        return are_types_valid and are_values_valid
    
    def check_if_time_unit_is_valid(self, time_unit: str) -> bool:
        return time_unit in self._supported_time_units
    
    def check_if_ignore_peaks_before_criteria_is_valid(self, criteria: str) -> bool:
        return criteria in self._supported_ignore_peaks_before_criteria
    
    def check_if_log_level_is_valid(self, log_level: str) -> bool:
        return log_level in self._supported_log_levels
    
    def __repr__(self) -> str:
        return f"AppConfig(peak_threshold={self.threshold}, peak_window={self.n_neighbors}, time_unit={self.time_unit}, ignore_peaks_before_criteria={self.ignore_peaks_before_criteria}, ignore_peaks_before={self.ignore_peaks_before}, output_directory={self.output_directory}, filters={self.filters})"
    
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
    
    @property
    def filters(self) -> list:
        return self._filters
    
    def to_dict(self) -> dict:
        return self.__dict__
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
                        

logging.info("Initializing AppConfig")
logging.info(f"Peak threshold: {PEAK_THRESHOLD}")
logging.info(f"Peak window: {PEAK_WINDOW}")
logging.info(f"Time unit: {TIME_UNIT}")
logging.info(f"Ignore peaks before criteria: {IGNORE_PEAKS_BEFORE_CRITERIA}")
logging.info(f"Ignore peaks before: {IGNORE_PEAKS_BEFORE}")
logging.info(f"Output directory: {OUTPUT_DIRECTORY}")
logging.info(f"Filters: {FILTERS}")

if __name__=="__main__":
    config = AppConfig()
    logging.info(f"Initialized with the following config{config}")
