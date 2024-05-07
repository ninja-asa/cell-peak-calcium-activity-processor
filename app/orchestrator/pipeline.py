
import pandas as pd
import logging
import os
from app.data import population
from app.data.population import CellPopulationActivity
from app.data.process import ActivityProcessor
from app.file.tables import read_from_file, write_to_file, create_new_file_from_input_filepath, get_directory_of_filepath
from app.config import AppConfig, LOGGING_CONFIG

config = AppConfig()
logging.basicConfig(**LOGGING_CONFIG)
logging.info(f"Initialized with the following config{config}")


def get_cell_activity_features_from_file_or_df(file_path: str = None, df: pd.DataFrame = None):
    """
    Get cell activity features from a file or dataframe

    Args:
        file_path (str): The path to the file

    Returns:
        pd.DataFrame: The cell activity features
        pd.Series: The summary of the population
    """
    if df is None:
        try:
            df = read_from_file(file_path)
        except FileNotFoundError as e:
            logging.error(e)
            raise e
        except ValueError as e:
            logging.error(e)
            raise e
    
    cell_population_activity = CellPopulationActivity(
        ignore_peaks_before_criteria=config.ignore_peaks_before_criteria,
        ignore_peaks_before=config.ignore_peaks_before,
        time_unit=config.time_unit
    )

    cell_population_activity.from_df(df)
    activity_processor = ActivityProcessor(
        threshold=config.threshold,
        n_neighbors=config.n_neighbors
    )

    cell_population_activity_features: pd.DataFrame = activity_processor.run(cell_population_activity)
    summary_population: pd.Series = activity_processor.summary_of_population(cell_population_activity_features)
    return cell_population_activity_features, summary_population


def process_files_in_bulk(file_paths: list, save_to_file: bool = False):
    """
    Process a list of files in bulk

    Args:
        file_paths (list): The list of file paths

    Returns:
        dict: A dictionary with the file path as key and the summary of the population as value
    """
    result = {}
    for file_path in file_paths:
        try:
            cell_population_activity_features, summary_population = get_cell_activity_features_from_file_or_df(file_path)
            summary_population.name = file_path
            result[file_path] = (cell_population_activity_features, summary_population)
        except Exception as e:
            logging.error(e)
    logging.info(f"Processed {len(result)} files")
    all_populations_summary = pd.DataFrame({key: value[1] for key, value in result.items()})
        
    if save_to_file:
        logging.info("Writing population data to files")
        write_population_data_to_files(result, all_populations_summary)

    return result, all_populations_summary


def process_dataframes_in_bulk(dataframes: list, save_to_file: bool = False):
    """
    Process a list of dataframes in bulk

    Args:
        file_paths (list): The list of DataFrames

    Returns:
        dict: A dictionary with the file path as key and the summary of the population as value
    """
    result = {}
    for idx, df in enumerate(dataframes):
        try:
            cell_population_activity_features, summary_population = get_cell_activity_features_from_file_or_df(df)
            summary_population.name = str(idx)
            result[summary_population.name] = (cell_population_activity_features, summary_population)
        except Exception as e:
            logging.error(e)

    all_populations_summary = pd.DataFrame({key: value[1] for key, value in result.items()})
        
    if save_to_file:
        write_population_data_to_files(result, all_populations_summary)

    return result, all_populations_summary

def write_population_data_to_files(result, all_populations_summary):
    # check if app config directory exists
    if not os.path.exists(config.output_directory):
        os.makedirs(config.output_directory)
    datetime_now = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
    output_dir = os.path.join(config.output_directory, datetime_now)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    logging.info(f"Writing population data to {output_dir}")
    for key, value in result.items():
        suffix = "features"
        features_file_path = create_new_file_from_input_filepath(key, suffix)
        features_file_path = os.path.join(config.output_directory, features_file_path)
        write_to_file(value[0], features_file_path)

        suffix = "summary"
        summary_file_path = create_new_file_from_input_filepath(key, suffix)
        summary_file_path = os.path.join(output_dir, summary_file_path)
        write_to_file(value[1], summary_file_path)
    populations_output_dir = os.path.join(output_dir, "all_populations_summary.csv")
    write_to_file(all_populations_summary, populations_output_dir)
    logging.info("Finished writing population data")
    return

def main():
    current_module_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_module_dir, "..", "..", "samples")
    # find excel and csv files in the samples directory
    file_paths = [os.path.join(samples_dir, file) for file in os.listdir(samples_dir) if file.endswith(".csv") or file.endswith(".xlsx")]
    logging.info(f"Found {len(file_paths)} files in the samples directory")

    # process the files in bulk
    result, all_populations_summary = process_files_in_bulk(file_paths, save_to_file=True)
    logging.info(f"Processed {len(result)} files")
    return result, all_populations_summary

if __name__ == "__main__":
    main()
