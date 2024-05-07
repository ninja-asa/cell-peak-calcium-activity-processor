# entrypoint for the application, receives directory path as argument

import os
import logging
import sys

from app.orchestrator.pipeline import process_files_in_bulk

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s', level=log_level, handlers=[logging.StreamHandler(), logging.FileHandler(f"{__name__}.log")])

def main(directory_path: str):
    """
    Process all files in a directory

    Args:
        directory_path (str): The path to the directory
    """
    # find excel and csv files in the samples directory
    file_paths = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith(".csv") or file.endswith(".xlsx")]
    logging.info(f"Found {len(file_paths)} files in the samples directory")
    logging.info(file_paths)
    # load logging level from environment variable

    # process files in bulk
    result, all_populations_summary = process_files_in_bulk(file_paths, save_to_file=True)
    return result, all_populations_summary

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Please provide the directory path as argument")
        sys.exit(1)
    directory_path = sys.argv[1]
    main(directory_path)