import streamlit as st
import pandas as pd

from zipfile import ZipFile
import os
import logging
from datetime import datetime

from app.config import AppConfig, LOGGING_CONFIG, GITHUB_REPOSITORY_URL
from app.orchestrator.pipeline import process_dataframes_in_bulk
from app.file.tables import read_from_file

logging.basicConfig(**LOGGING_CONFIG)

def get_files_in_directory(directory_path):
    return [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith(".csv") or file.endswith(".xlsx")]

def process_files(files, app_config: AppConfig):
    if files is None:
        error = ValueError("Please upload files to process")
        logging.error(error)
        raise error
    
    dfs = [read_from_file(file.name, raw_bytes=file.getvalue()) for file in files]

    results, all_populations_summary = process_dataframes_in_bulk(dfs, save_to_file=False, config=app_config)
    # replace results keys with filenames
    filenames = [file.name for file in files]
    results_with_filenames = dict(zip(filenames, results.values()))
    
    # rename columns of all_populations_summary
    all_populations_summary.columns = filenames
    return results_with_filenames, all_populations_summary

download_all_placeholder = st.empty()

# Create a sidebar
st.sidebar.title('Parameter Selection 🛠️')

list_of_files = st.sidebar.file_uploader(
    "Upload Files",
    accept_multiple_files=True,
    type=['csv', 'xlsx'],
    help='Upload the files to be processed'
)
st.sidebar.markdown(f"Sample Data can be found [here]({GITHUB_REPOSITORY_URL}/blob/main/samples/sample.csv)")

peak_threshold = st.sidebar.number_input('Peak Threshold', value=0.4, help='The threshold for peak detection')
peak_window = st.sidebar.slider('Peak Window', min_value=1, max_value=20, value=5, help="A peak must be the maximum within a windows of -n to +n samples")
time_unit = st.sidebar.selectbox('Time Unit', ('s', 'ms'), index=0, help='The unit of time used in the data')
ignore_peaks_before_criteria = st.sidebar.selectbox('Ignore Peaks Before Criteria', ('samples', 'time'), index=0, help='The criteria used to ignore peaks before a certain point - either amount of samples (frames) or time')
ignore_peaks_before = st.sidebar.number_input('Ignore Peaks Before', min_value=1, max_value=10, value=1, help='The number of samples or time units to ignore before')
output_directory = st.sidebar.text_input('Output Directory', 'output', help='The directory to save the output files')
logging_level = st.sidebar.selectbox('Logging Level', ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'), index=1, help='The level of logging to use')
remove_values_aboves = st.sidebar.number_input('Remove Values Above', value=None, help='Remove values above this threshold')
remove_values_belows = st.sidebar.number_input('Remove Values Below', value=None, help='Remove values below this threshold')
show_population_summary = st.sidebar.checkbox('Show Population Summary', value=True, help='Show the summary of the population')
if st.sidebar.button('Submit'):
    app_config = AppConfig(
        custom_filters=[(remove_values_aboves, 'above'), (remove_values_belows, 'below')],
        peak_threshold=peak_threshold,
        peak_window=peak_window,
        time_unit=time_unit,
        ignore_peaks_criteria=ignore_peaks_before_criteria,
        ignore_peaks_before=ignore_peaks_before,
        output_directory=output_directory,
        log_level=logging_level
    )
    # loading the data
    try:
        results, all_populations_summary = process_files(list_of_files, app_config)
        st.header('All Populations Summary')
        
        # stylze the dataframe with gradient per column with cmap="YlGnBu"
        ai = all_populations_summary.style.background_gradient(axis=1, cmap="coolwarm")  
                
        st.dataframe(ai, use_container_width=True)
        filenames = [file.name for file in list_of_files]
        if show_population_summary:
            st.header('Results per File')            
            for filename in results.keys():
                st.subheader(filename)
                st.dataframe(results[filename][0], use_container_width=True)
                st.dataframe(results[filename][1], use_container_width=True)
        
        def prepare_zip_file(results: dict, all_populations_summary: pd.DataFrame, config: AppConfig):
            dt_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            zip_filename = f"output-{dt_now}.zip" 
            with ZipFile(zip_filename, 'w') as zipObj:
                for filename in results.keys():
                    csv_filename = f"{filename}_cell_activity_features.csv"
                    zipObj.write(csv_filename, results[filename][0].to_csv(csv_filename))
                    csv_filename = f"{filename}_population_summary.csv"
                    zipObj.write(csv_filename, results[filename][1].to_csv(csv_filename))
                csv_filename = "all_populations_summary.csv"
                zipObj.write(csv_filename, all_populations_summary.to_csv(csv_filename))
                # write app config to a json file
                app_config_filename = "app_config.json"
                # write app config to a json file
                with open(app_config_filename, "w") as f:
                    f.write(config.to_json())
                zipObj.write(app_config_filename)
                
            # get datetime now as a str
            return zip_filename
        
        # results if not empty dict 
        if results:
            zip_filename = prepare_zip_file(results, all_populations_summary, config=app_config)
            with open(zip_filename, "rb") as f:
                download_all_placeholder.download_button(
                    data=f,
                    label="Download All Results",
                    key="download_all",
                    help="Download all the results in a zip file",
                    mime="application/zip",
                    file_name=zip_filename,
                    on_click=None)
            
    except ValueError as e:
        st.error(e)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        
    