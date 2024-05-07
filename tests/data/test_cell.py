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

def test_to_series():
    cell_activity = CellActivity(
        cell_id="cell1", 
        nr_peaks=3, 
        is_active=True, 
        time_to_first_peak=pd.Timestamp("2022-01-01 00:00:05.1"), 
        value_at_first_peak=1, 
        time_to_max_peak=pd.Timestamp("2022-01-01 00:00:10"),
        value_at_max_peak=3)
    series = cell_activity.to_series()

    assert series.name == "cell1"
    assert series["nr_peaks"] == 3
    assert series["is_active"] == True
    assert series["time_to_first_peak"] == 5.1
    assert series["value_at_first_peak"] == 1
    assert series["time_to_max_peak"] == 10
    assert series["value_at_max_peak"] == 3


def test_to_series_non_active_cell():
    cell_activity = CellActivity(cell_id="cell1", nr_peaks=0, is_active=False)
    series = cell_activity.to_series()

    assert series.name == "cell1"
    assert series["nr_peaks"] == 0
    assert series["is_active"] == False
    # confirm it has nan values
    assert pd.isna(series["time_to_first_peak"])
    assert pd.isna(series["value_at_first_peak"])
    assert pd.isna(series["time_to_max_peak"])
    