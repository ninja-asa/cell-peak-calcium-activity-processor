import os
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal
from app.orchestrator.pipeline import main
from app.config import AppConfig

def test_main_end_to_end():
    # set environment variables
    my_test_config = AppConfig(
        custom_filters=[(0, "below"), (10, "above")],
    )
    
    result, all_populations_summary = main(my_test_config)
    # assert that the function runs without error
    assert isinstance(result, dict)
    assert isinstance(all_populations_summary, pd.DataFrame)

    # confirm that there are only 2 keys (i.e. only two files were processed)
    assert len(result) == 2
    
    first_key = list(result.keys())[0]
    second_key = list(result.keys())[1]
    # confirm contents of the first key are the same as the second key
    assert_frame_equal(result[first_key][0], result[second_key][0], check_names=False)
    assert_series_equal(result[first_key][1], result[second_key][1], check_names=False)
    
    # confirm the first row of the summary is the same as the second row
    first_column = all_populations_summary.columns[0]
    second_column = all_populations_summary.columns[1]
    assert all_populations_summary[first_column].equals(all_populations_summary[second_column])

