import pandas as pd

from app.data.cell import CellActivity

def test_from_peaks_with_no_peaks():
    peaks = pd.Series([], name="cell1")
    cell_activity = CellActivity.from_peaks(peaks)

    assert cell_activity.cell_id == "cell1"
    assert cell_activity.nr_peaks == 0
    assert cell_activity.is_active == False
    assert cell_activity.time_to_first_peak is None
    assert cell_activity.value_at_first_peak is None
    assert cell_activity.time_to_max_peak is None
    assert cell_activity.value_at_max_peak is None

def test_from_peaks_with_peaks():
    peaks = pd.Series([1, 2, 3], index=[pd.Timestamp("2022-01-01"), pd.Timestamp("2022-01-02"), pd.Timestamp("2022-01-03")], name="cell1")
    cell_activity = CellActivity.from_peaks(peaks)

    assert cell_activity.cell_id == "cell1"
    assert cell_activity.nr_peaks == 3
    assert cell_activity.is_active == True
    assert cell_activity.time_to_first_peak == pd.Timestamp("2022-01-01")
    assert cell_activity.value_at_first_peak == 1
    assert cell_activity.time_to_max_peak == pd.Timestamp("2022-01-03")
    assert cell_activity.value_at_max_peak == 3

def test_to_df():
    cell_activity = CellActivity(
        cell_id="cell1", 
        nr_peaks=3, 
        is_active=True, 
        time_to_first_peak=pd.Timestamp("2022-01-01 00:00:05.1"), 
        value_at_first_peak=1, 
        time_to_max_peak=pd.Timestamp("2022-01-01 00:00:10"),
        value_at_max_peak=3)
    df = cell_activity.to_df()

    assert df.index[0] == "cell1"
    assert df["nr_peaks"][0] == 3
    assert df["is_active"][0] == True
    assert df["time_to_first_peak"][0] == 5.1
    assert df["value_at_first_peak"][0] == 1
    assert df["time_to_max_peak"][0] == 10
    assert df["value_at_max_peak"][0] == 3


def test_to_series_non_active_cell():
    cell_activity = CellActivity(cell_id="cell1", nr_peaks=0, is_active=False)
    df = cell_activity.to_df()

    assert df.index[0] == "cell1"
    assert df["nr_peaks"][0] == 0
    assert df["is_active"][0] == False
    # confirm it has nan values
    assert pd.isna(df["time_to_first_peak"][0])
    assert pd.isna(df["value_at_first_peak"][0])
    assert pd.isna(df["time_to_max_peak"][0])
    