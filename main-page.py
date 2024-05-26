from multiprocessing import Value
import streamlit as st
import os
import logging

from app.config import AppConfig, LOGGING_CONFIG, GITHUB_REPOSITORY_URL
from app.orchestrator.pipeline import process_files_in_bulk

logging.basicConfig(**LOGGING_CONFIG)

def get_files_in_directory(directory_path):
    return [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith(".csv") or file.endswith(".xlsx")]

def process_files(directory_path, app_config: AppConfig):
    if directory_path is None:
        error = ValueError("Please enter a valid directory path")
        logging.error(error)
        raise error
    files = get_files_in_directory(input_directory)
    results, all_populations_summary = process_files_in_bulk(files, save_to_file=True, config=app_config)
    return results, all_populations_summary

# Create a sidebar
st.sidebar.title('Parameter Selection')
st.sidebar.markdown(f"Original code can be found [here]({GITHUB_REPOSITORY_URL})")

peak_threshold = st.sidebar.number_input('Peak Threshold', value=0.4, help='The threshold for peak detection')
peak_window = st.sidebar.slider('Peak Window', min_value=1, max_value=20, value=5, help="A peak must be the maximum within a windows of -n to +n samples")
time_unit = st.sidebar.selectbox('Time Unit', ('s', 'ms'), index=0, help='The unit of time used in the data')
ignore_peaks_before_criteria = st.sidebar.selectbox('Ignore Peaks Before Criteria', ('samples', 'time'), index=0, help='The criteria used to ignore peaks before a certain point - either amount of samples (frames) or time')
ignore_peaks_before = st.sidebar.number_input('Ignore Peaks Before', min_value=1, max_value=10, value=1, help='The number of samples or time units to ignore before')
input_directory = st.sidebar.text_input('Input Directory', value='', help='Please enter the path to the directory containing the input files')
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
        results, all_populations_summary = process_files(input_directory, app_config)
        st.write("Results can be found in the output directory")        
        st.header('All Populations Summary')
        st.dataframe(all_populations_summary, use_container_width=True)
        if show_population_summary:
            st.header('Results per File')            
            for filename in results.keys():
                st.subheader(filename)
                st.dataframe(results[filename][0], use_container_width=True)
                st.dataframe(results[filename][1], use_container_width=True)
    except ValueError as e:
        st.error(e)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        
    
