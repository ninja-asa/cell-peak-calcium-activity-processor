import pandas as pd

import os
import logging
import datetime
from io import BytesIO


# load logging level from environment variable
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s', level=log_level, handlers=[logging.StreamHandler(), logging.FileHandler(f"{__name__}.log")])


def read_file_using_function(file_path: str, read_function: callable, raw_bytes: bytes = None) -> pd.DataFrame:
    """
    Read a file using a read function

    Args:
        file_path (str): The path to the file
        read_function (callable): The function to read the file

    Returns:
        pd.DataFrame: The read DataFrame
    """
    if raw_bytes is not None:
        return read_function(BytesIO(raw_bytes), index_col=None, header=None)
    
    return read_function(file_path, index_col=None, header=None)

def post_clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a DataFrame by dropping rows and columns with all NaN values

    Args:
        df (pd.DataFrame): The DataFrame to be cleaned

    Returns:
        pd.DataFrame: The cleaned DataFrame
    """
    # try to convert to numeric all columns
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except ValueError:
            df = df.drop(columns=col)
        except TypeError as e:
            logging.error(e)
            raise e
    return df

def read_from_file(file_path: str, raw_bytes: bytes = None) -> pd.DataFrame:
    """
    Read a pandas DataFrame from a file

    Args:
        file_path (str): The path to the file

    Returns:
        pd.DataFrame: The read DataFrame
    """
    # check if file exists
    if raw_bytes is None and not os.path.exists(file_path):
        e = FileNotFoundError(f"File not found: {file_path}")
        logging.error(e)
        raise e
    try:
        if file_path.endswith(".csv"):
            df = read_file_using_function(file_path, pd.read_csv, raw_bytes=raw_bytes)
        elif file_path.endswith(".xlsx"):
            df = read_file_using_function(file_path, pd.read_excel, raw_bytes=raw_bytes)
        else:
            e = ValueError(f"File format not supported: {file_path}")
            logging.error(e)
            raise e
    except Exception as e:
        logging.error(f"Could not read file {file_path}")
        logging.error(e)
        raise e
    
    # find and set the header
    try:
        df = pre_clean_df(df)
        df = find_and_set_header(df)
        df = post_clean_df(df)
    except Exception as e:
        logging.error(f"Could not clean DataFrame from file {file_path}")
        logging.error(e)
        raise e
    
    if df.empty:
        e = ValueError(f"DataFrame is empty: {file_path}")
        logging.error(e)
        raise e
    return df
   
   
def pre_clean_df(df: pd.DataFrame) -> pd.DataFrame:
    # drop columns which are only NaN
    df = df.dropna(axis=1, how="all")
    # drop rows which are only NaN
    df = df.dropna(axis=0, how="all")
    return df
        
def find_and_set_header(df: pd.DataFrame) -> pd.DataFrame:
    """
    Find the header of the DataFrame and set it as the header

    Args:
        df (pd.DataFrame): The DataFrame to find and set the header of

    Returns:
        pd.DataFrame: The DataFrame with the header set
    """
    
    # find rows where "time" can be found (partially or fully), skipping the numeric values
    header_index = df.apply(lambda x: x.str.contains("time", case=False)).any(axis=1).idxmax() 
    
    # set the header
    df.columns = df.loc[header_index]
    # drop the header row
    df = df.drop(header_index)
    return df

def create_new_file_from_input_filepath(file_path: str, suffix: str = None) -> str:
    """
    Create a new file path from the input file path

    Args:
        file_path (str): The input file path
        suffix (str): The suffix to add to the file path

    Returns:
        str: The new file path
    """
    file_name, file_extension = os.path.splitext(file_path)
    # get the file name without the directory
    file_name = os.path.basename(file_name)
    if suffix is None:
        suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    new_file_path = f"{file_name}_{suffix}{file_extension}"
    return new_file_path

def write_to_file(df: pd.DataFrame, file_path: str) -> None:
    """
    Write a DataFrame to a file, either csv or excel
    """
    if file_path.endswith(".csv"):
        df.to_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df.to_excel(file_path)
    else:
        e = ValueError(f"File format not supported: {file_path}")
        logging.error(e)
        raise e
    logging.info(f"Data written to {file_path}")
    return

def get_directory_of_filepath(file_path: str) -> str:
    """
    Get the directory of a file path

    Args:
        file_path (str): The file path

    Returns:
        str: The directory of the file path
    """
    return os.path.dirname(file_path)

if __name__=="__main__":
    filename = "samples/no.peaks.csv"
    df = read_from_file(filename)
    print(df.head())
