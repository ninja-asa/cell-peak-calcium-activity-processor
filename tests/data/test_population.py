import pytest
from pandas.testing import assert_frame_equal
from unittest.mock import patch

import pandas as pd

from app.data.population import CellPopulationActivity

@pytest.fixture(scope="function")
def test_data():
    return pd.DataFrame(
        {
            "FRAMES": [1, 2, 3, 4, 5],
            "TIME": [0, 1, 2, 3, 4],
            "CELL 1": [0.1, 0.2, 0.3, 0.4, 0.5],
            "CELL 2": [0.1, 0.5, 0.3, 0.6, 0.5],
            "CELL 3": [0.1, 0.2, 0.3, 0.4, 0.5],
        }
    )


def test_post_init_cell_population_activity():
    cell_population_activity = CellPopulationActivity(
        ignore_peaks_before_criteria="SAMPLES",
        ignore_peaks_before=11,
        time_unit="s"
    )

    assert cell_population_activity.ignore_peaks_before_criteria == "SAMPLES"
    assert cell_population_activity.ignore_peaks_before == 11
    assert cell_population_activity.time_unit == "s"

    with pytest.raises(ValueError):
        CellPopulationActivity(
            ignore_peaks_before_criteria="INVALID",
            ignore_peaks_before=11,
            time_unit="s"
        )
    
    with pytest.raises(ValueError):
        CellPopulationActivity(
            ignore_peaks_before_criteria="samples",
            ignore_peaks_before=11,
            time_unit="min"
        )

def test_set_time_column_as_index(test_data):
    # Arrange 
    test_data_test_1 = test_data.copy()
    cell_population_activity = CellPopulationActivity(time_unit="s")
    # Act - time unit of seconds
    cell_population_activity.set_time_column_as_index(test_data_test_1)
    # Assert :
    # confirm the index is a datetime index
    assert test_data_test_1.index.dtype == "datetime64[ns]"
    # confirm it yield the expect index
    assert test_data_test_1.index[0] == pd.Timestamp("1970-01-01 00:00:00")
    assert test_data_test_1.index[1] == pd.Timestamp("1970-01-01 00:00:01")
    assert test_data_test_1.index[2] == pd.Timestamp("1970-01-01 00:00:02")
    assert test_data_test_1.index[3] == pd.Timestamp("1970-01-01 00:00:03")
    assert test_data_test_1.index[4] == pd.Timestamp("1970-01-01 00:00:04")


    # Arrange 
    test_data_test_2 = test_data.copy()
    cell_population_activity = CellPopulationActivity(time_unit="ms")
    # Act - time unit of seconds
    cell_population_activity.set_time_column_as_index(test_data_test_2)
    # Assert :
    # confirm the index is a datetime index
    assert test_data_test_2.index.dtype == "datetime64[ns]"
    # confirm it yield the expect index
    assert test_data_test_2.index[0] == pd.Timestamp("1970-01-01 00:00:00")
    assert test_data_test_2.index[1] == pd.Timestamp("1970-01-01 00:00:00.001")
    assert test_data_test_2.index[2] == pd.Timestamp("1970-01-01 00:00:00.002")
    assert test_data_test_2.index[3] == pd.Timestamp("1970-01-01 00:00:00.003")
    assert test_data_test_2.index[4] == pd.Timestamp("1970-01-01 00:00:00.004")


def test_set_time_column_as_index_with_bad_data(test_data):
    # Arange
    test_data.columns = ["FRAMES", "TME", "CELL 1", "CELL 2", "CELL 3"]
    # Act and Assert
    with pytest.raises(ValueError):
        CellPopulationActivity(time_unit="s").set_time_column_as_index(test_data)

@pytest.fixture(scope="function")
def test_data_with_datetime_index():
    return pd.DataFrame(
        index = pd.date_range(start="1970-01-01 00:00:00", periods=5, freq="s"),
        data = {
            "CELL 1": [0.1, 0.2, 0.3, 0.4, 0.5],
            "CELL 2": [0.1, 0.5, 0.3, 0.6, 0.5],
            "CELL 3": [0.1, 0.2, 0.3, 0.4, 0.5],
        }
    )

def test_drop_rows_before_time_not_in_place(test_data_with_datetime_index) -> None:
    # Arrange 1
    test_data_with_datetime_index_original = pd.DataFrame(
        index = pd.date_range(start="1970-01-01 00:00:00", periods=5, freq="s"),
        data = {
            "CELL 1": [0.1, 0.2, 0.3, 0.4, 0.5],
            "CELL 2": [0.1, 0.5, 0.3, 0.6, 0.5],
            "CELL 3": [0.1, 0.2, 0.3, 0.4, 0.5],
        }
    )

    test_data_with_datetime_index = test_data_with_datetime_index_original.copy()
    cell_population_activity = CellPopulationActivity(
        time_unit="s",
        ignore_peaks_before_criteria="TIME",
        ignore_peaks_before=2
        )
    

    # Act 1
    output_1 = cell_population_activity.drop_rows_before_time(test_data_with_datetime_index, inplace=False)
    # Assert
    assert len(output_1.index) == 3
    assert output_1.index[0] == pd.Timestamp("1970-01-01 00:00:02")
    assert output_1.index[1] == pd.Timestamp("1970-01-01 00:00:03")
    assert output_1.index[2] == pd.Timestamp("1970-01-01 00:00:04")
    assert_frame_equal(test_data_with_datetime_index_original, test_data_with_datetime_index)

def test_drop_rows_before_time_in_place(test_data_with_datetime_index):
    # Arrange 1
    test_data_with_datetime_index_original = test_data_with_datetime_index
    cell_population_activity = CellPopulationActivity(
        time_unit="s",
        ignore_peaks_before_criteria="TIME",
        ignore_peaks_before=2
        )
    
    test_data_with_datetime_index = test_data_with_datetime_index_original.copy()
    
    # Act 1
    cell_population_activity.drop_rows_before_time(test_data_with_datetime_index, inplace=True)
    # Assert 1
    assert len(test_data_with_datetime_index.index) == 3
    assert test_data_with_datetime_index.index[0] == pd.Timestamp("1970-01-01 00:00:02")
    assert test_data_with_datetime_index.index[1] == pd.Timestamp("1970-01-01 00:00:03")
    assert test_data_with_datetime_index.index[2] == pd.Timestamp("1970-01-01 00:00:04")


    # Arrange 2
    test_data_with_datetime_index = test_data_with_datetime_index_original.copy()
    cell_population_activity = CellPopulationActivity(
        time_unit="s",
        ignore_peaks_before_criteria="TIME",
        ignore_peaks_before=1
        )
    
    # Act 2
    cell_population_activity.drop_rows_before_time(test_data_with_datetime_index)

    # Assert 2
    assert len(test_data_with_datetime_index.index) == 4
    assert test_data_with_datetime_index.index[0] == pd.Timestamp("1970-01-01 00:00:01")
    assert test_data_with_datetime_index.index[1] == pd.Timestamp("1970-01-01 00:00:02")
    assert test_data_with_datetime_index.index[2] == pd.Timestamp("1970-01-01 00:00:03")
    assert test_data_with_datetime_index.index[3] == pd.Timestamp("1970-01-01 00:00:04")    


def test_drop_row_before_sample_not_in_place(test_data_with_datetime_index):
    # Arrange
    test_data_with_datetime_index_original = test_data_with_datetime_index
    cell_population_activity = CellPopulationActivity(
        time_unit="s",
        ignore_peaks_before_criteria="SAMPLES",
        ignore_peaks_before=2
        )
    
    test_data_with_datetime_index = test_data_with_datetime_index_original.copy()
    
    # Act
    output = cell_population_activity.drop_rows_before_sample(test_data_with_datetime_index, inplace=False)
    # Assert
    assert len(output.index) == 3
    assert output.index[0] == pd.Timestamp("1970-01-01 00:00:02")
    assert output.index[1] == pd.Timestamp("1970-01-01 00:00:03")
    assert output.index[2] == pd.Timestamp("1970-01-01 00:00:04")
    assert_frame_equal(test_data_with_datetime_index_original, test_data_with_datetime_index)


def test_drop_row_before_sample_inplace(test_data_with_datetime_index):
    # Arrange 1
    test_data_with_datetime_index_original = test_data_with_datetime_index
    cell_population_activity = CellPopulationActivity(
        time_unit="s",
        ignore_peaks_before_criteria="SAMPLES",
        ignore_peaks_before=2
        )
    
    test_data_with_datetime_index = test_data_with_datetime_index_original.copy()
    
    # Act 1
    cell_population_activity.drop_rows_before_sample(test_data_with_datetime_index, inplace=True)
    # Assert 1
    assert len(test_data_with_datetime_index.index) == 3
    assert test_data_with_datetime_index.index[0] == pd.Timestamp("1970-01-01 00:00:02")
    assert test_data_with_datetime_index.index[1] == pd.Timestamp("1970-01-01 00:00:03")
    assert test_data_with_datetime_index.index[2] == pd.Timestamp("1970-01-01 00:00:04")

    # Arrange 2
    test_data_with_datetime_index = test_data_with_datetime_index_original.copy()
    cell_population_activity = CellPopulationActivity(
        time_unit="s",
        ignore_peaks_before_criteria="SAMPLES",
        ignore_peaks_before=1
        )
    
    # Act 2
    cell_population_activity.drop_rows_before_sample(test_data_with_datetime_index, inplace=True)
    # Assert 2
    assert len(test_data_with_datetime_index.index) == 4
    assert test_data_with_datetime_index.index[0] == pd.Timestamp("1970-01-01 00:00:01")
    assert test_data_with_datetime_index.index[1] == pd.Timestamp("1970-01-01 00:00:02")
    assert test_data_with_datetime_index.index[2] == pd.Timestamp("1970-01-01 00:00:03")
    assert test_data_with_datetime_index.index[3] == pd.Timestamp("1970-01-01 00:00:04")
    
@patch("app.data.population.CellPopulationActivity.drop_rows_before_time")
def test_drop_rows_by_time(mock_drop_row_before_time, test_data_with_datetime_index):
    # confirm the function `drop_rows_by_time` is called
    
    # Arrange
    cell_population_activity = CellPopulationActivity(
        ignore_peaks_before=2,
        ignore_peaks_before_criteria="TIME")
    
    # Act
    cell_population_activity.drop_rows(test_data_with_datetime_index)

    # Assert
    
    mock_drop_row_before_time.assert_called_once
    mock_drop_row_before_time.assert_called_with(
        test_data_with_datetime_index, threshold_time=2, inplace=True
    )

@patch("app.data.population.CellPopulationActivity.drop_rows_before_sample")
def test_drop_rows_by_sample(mock_drop_row_before_sample, test_data_with_datetime_index):
    # confirm the function `drop_rows_by_sample` is called
    
    # Arrange
    cell_population_activity = CellPopulationActivity(
        ignore_peaks_before=2,
        ignore_peaks_before_criteria="SAMPLES")
    
    # Act
    cell_population_activity.drop_rows(test_data_with_datetime_index)

    # Assert
    mock_drop_row_before_sample.assert_called_once
    mock_drop_row_before_sample.assert_called_with(
        test_data_with_datetime_index, threshold_sample=2, inplace=True
    )


def test_read_df_cell_population_activity(test_data):
    cell_population_activity = CellPopulationActivity(
        ignore_peaks_before_criteria="SAMPLES",
        ignore_peaks_before=2,
        time_unit="s"
    )
    cell_population_activity.from_df(test_data)
    # confirm the index is a datetime index
    assert cell_population_activity.data.index.dtype == "datetime64[ns]"
    # confirm the columns are as expected
    assert len(cell_population_activity.data.columns) == 3
    assert "CELL 1" in cell_population_activity.data.columns
    assert len(cell_population_activity.data) == 3