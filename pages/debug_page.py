import streamlit as st
import plotly.graph_objects as go


from app.data.population import CellPopulationActivity
from app.orchestrator.pipeline import read_from_file
from app.config import AppConfig, GITHUB_REPOSITORY_URL

config = AppConfig(
    ignore_peaks_criteria='samples',
    ignore_peaks_before=1,
    time_unit='s',
    custom_filters=None
)

st.markdown("# Debug View 🔍")
st.sidebar.markdown("# Debug View 🔍")
st.sidebar.markdown(f"Original code can be found [here]({GITHUB_REPOSITORY_URL})")

st.sidebar.markdown("This page is used to debug the cell peak calcium activity processor to tune the parameters")

mock_threshold = st.sidebar.number_input('Peak Threshold', value=0.4, help='The threshold for peak detection')
# Create a placeholder at the top of the page
line_plot_placeholder = st.empty()
error_placeholder = st.empty()
column_range_placeholder = st.empty()

def uploaded_file_callback_on_change():
    uploaded_file = st.session_state.uploaded_file
    if uploaded_file is not None:
        try:
            df = read_from_file(uploaded_file.name, raw_bytes=uploaded_file.getvalue())
            cell_population_activity = CellPopulationActivity(
                ignore_peaks_before_criteria=config._ignore_peaks_before_criteria,
                ignore_peaks_before=config.ignore_peaks_before,
                time_unit=config.time_unit,
                filters=config.filters
            )
            cell_population_activity.from_df(df)
            # Create a dropdown to select a range of columns
            num_columns = len(cell_population_activity.data.columns)
            column_ranges = [f'{i+1}-{min(i+10, num_columns)}' for i in range(0, num_columns, 10)]
            selected_range = column_range_placeholder.selectbox('Select column range', column_ranges)

            # Parse the selected range
            start, end = map(int, selected_range.split('-'))
            # Create a line plot for each column
            fig = go.Figure()
            if mock_threshold:
                fig.add_trace(go.Scatter(x=cell_population_activity.data.index, y=[mock_threshold] * len(cell_population_activity.data.index), mode='lines', name='Peak Threshold'))
            for column in cell_population_activity.data.columns[start-1:end]:
                fig.add_trace(go.Scatter(x=cell_population_activity.data.index, y=cell_population_activity.data[column], mode='lines+markers', name=column))
                fig.update_layout(title=f"Raw Data", xaxis_title='Time', yaxis_title='Value')
                line_plot_placeholder.plotly_chart(fig)
        except Exception as e:
            error_placeholder.error(e)
    
st.session_state.uploaded_file = st.sidebar.file_uploader(
    "Choose a file", type=["csv", "xlsx"],
    on_change=uploaded_file_callback_on_change, key="new_file")
# add url to a demo sample file
st.sidebar.markdown(f"Sample Data can be found [here]({GITHUB_REPOSITORY_URL}/blob/main/samples/sample.csv)")

uploaded_file_callback_on_change()
