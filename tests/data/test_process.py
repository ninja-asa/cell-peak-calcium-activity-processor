import pytest
import pandas as pd
from unittest.mock import create_autospec, patch
from app.data.process import ActivityProcessor, CellPopulationActivity, CellActivity

@pytest.fixture()
def test_processor():
    return ActivityProcessor(
        threshold=0.5,
        n_neighbors=3
    )

def test_init(test_processor):
    summary = ActivityProcessor(
        threshold=0.5,
        n_neighbors=3
    )
    assert summary.threshold == 0.5
    assert summary.n_neighbors == 3

def test_sanity_check_data(test_processor):
    # Arrange
    mock_cell_population_activity = create_autospec(CellPopulationActivity)
    mock_cell_population_activity.data = pd.DataFrame({
        'column1': [1, 2, 3],
        'column2': [4, 5, 6]
    }, index=pd.date_range(start='1/1/2022', periods=3))
    
    # Act and Assert that no exception is raised
    try:
        test_processor._sanity_check_data(mock_cell_population_activity)
    except ValueError:
        pytest.fail("sanity_check_data() raised ValueError unexpectedly!")

def test_sanity_check_data_with_wrong_data(test_processor):
    # Arrange
    mock_cell_population_activity = create_autospec(CellPopulationActivity)
    mock_cell_population_activity.data = pd.DataFrame()

    # Act and Assert that ValueError is raised
    # test with empty data
    with pytest.raises(ValueError):
        test_processor._sanity_check_data(mock_cell_population_activity)

def test_sanity_check_data_with_wrong_index(test_processor):
    # Arrange
    mock_cell_population_activity = create_autospec(CellPopulationActivity)
    mock_cell_population_activity.data = pd.DataFrame({
        'column1': [1, 2, 3],
        'column2': [4, 5, 6]
    }, index=[1, 2, 3])

    # Act and Assert that ValueError is raised    # test with non datetime index
    with pytest.raises(ValueError):
        test_processor._sanity_check_data(mock_cell_population_activity)


def test_sanity_check_data_with_non_numerical_columns(test_processor):
    # Arrange
    mock_cell_population_activity = create_autospec(CellPopulationActivity)
    mock_cell_population_activity.data = pd.DataFrame({
        'column1': [1, 2, 3],
        'column2': [4, 5, 6]
    }, index=pd.date_range(start='1/1/2022', periods=3))
    mock_cell_population_activity.data['column1'] = mock_cell_population_activity.data['column1'].astype(str)

    # Act and Assert that ValueError is raised
    # test with non numerical columns
    with pytest.raises(ValueError):
        test_processor._sanity_check_data(mock_cell_population_activity)

def test_sanity_check_data_with_wrong_data_type(test_processor):
    # Arrange
    mock_cell_population_activity = create_autospec(CellPopulationActivity)
    mock_cell_population_activity.data = pd.Series(
        [1, 2, 3], index=pd.date_range(start='1/1/2022', periods=3))

    # Act and Assert that ValueError is raised
    # test with wrong data type
    with pytest.raises(ValueError):
        test_processor._sanity_check_data(mock_cell_population_activity)

    # Act and Assert that ValueError is raised
    # test with wrong data type
    with pytest.raises(ValueError):
        test_processor._sanity_check_data("wrong data type")

@pytest.fixture()
def test_time_series():
    # with datetime index
    data = [0, 3, 3, 3, 4, 0, 1, 2, 3, 2]
    return pd.Series(
        data,
        index=pd.date_range(
            start='1/1/2020', 
            periods=len(data), 
            freq='s'
        )
    )

# parametrize test
@pytest.mark.parametrize(
    "n_neighbors, threshold, expected",
    [
        (3, 2, [4, 3]),
        (5, 2, [4]),
        (3, 3, [4, 3]),
        (5, 4, [4]),
        (3, None, [4, 3]), # will use average of data, which is 2.1
    ]
)
def test_get_local_maxima(test_time_series, n_neighbors, threshold, expected):
    result = ActivityProcessor.get_local_maxima_per_column(test_time_series, n_neighbors, threshold)
    assert expected == result.tolist()

def test_initialize_summary_df(test_processor):
    # Arrange
    mock_cell_population_activity = create_autospec(CellPopulationActivity)
    mock_cell_population_activity.data = pd.DataFrame({
        'column1': [1, 2, 3],
        'column2': [4, 5, 6]
    }, index=pd.date_range(start='1/1/2022', periods=3))

    # Act
    result = test_processor._initialize_summary_df(mock_cell_population_activity)

    # Assert
    assert result.index.tolist() == ['column1', 'column2']

@pytest.mark.parametrize(
    "n_neighbors, threshold, expected",
    [
        (3, 4, [1, True, 4, 4, 4, 4]),
        (5, 3, [1, True, 4, 4, 4, 4]),
        (3, 5, [0, False, None, None, None, None]), 
    ]

)
def test_process_cell_activity(test_time_series, n_neighbors, threshold, expected):
    # Arrange
    test_processor = ActivityProcessor(
        threshold=threshold,
        n_neighbors=n_neighbors
    )

    # Act
    result = test_processor.process_cell_activity(test_time_series)

    # Assert
    assert isinstance(result, pd.DataFrame)
    assert result['nr_peaks'][0] == expected[0]
    assert result['is_active'][0] == expected[1]
    if expected[2] is None:
        assert pd.isna(result['time_to_first_peak'][0])
    else:
        assert result['time_to_first_peak'][0] == expected[2]
    if expected[3] is None:
        assert pd.isna(result['value_at_first_peak'][0])
    else:
        assert result['value_at_first_peak'][0] == expected[3]
    if expected[4] is None:
        assert pd.isna(result['time_to_max_peak'][0])
    else:
        assert result['time_to_max_peak'][0] == expected[4]
    if expected[5] is None:
        assert pd.isna(result['value_at_max_peak'][0])
    else:
        assert result['value_at_max_peak'][0] == expected[5]

def test_run(test_processor):
    # Arrange
    mock_cell_population_activity = create_autospec(CellPopulationActivity)
    mock_cell_population_activity.data = pd.DataFrame({
        'column1': [1, 2, 3],
        'column2': [4, 5, 6]
    }, index=pd.date_range(start='1/1/2022', periods=3))

    # Act
    result = test_processor.run(mock_cell_population_activity)

    # Assert
    assert result.index.tolist() == ['column1', 'column2']
    # sort list of string

    expected_columns = ['nr_peaks', 'is_active', 'time_to_first_peak', 'value_at_first_peak', 'time_to_max_peak', 'value_at_max_peak']
    for col in expected_columns:
        assert col in result.columns
    # Assert that the values are as expected
    assert result['nr_peaks'].tolist() == [0, 0]
    assert result['is_active'].tolist() == [False, False]
    assert pd.isna(result['time_to_first_peak']).all()
    assert pd.isna(result['value_at_first_peak']).all()
    assert pd.isna(result['time_to_max_peak']).all()
    assert pd.isna(result['value_at_max_peak']).all()
    
def test_summary_population():
    cell_population_activity_features = pd.DataFrame({
        'numeric1': [1, 2, 3],
        'numeric2': [4, 5, 6],
        'boolean1': [True, False, True],
        'boolean2': [False, True, True],
    })
    summary = ActivityProcessor.summary_of_population(cell_population_activity_features)

    # assert summary.index.tolist() == [
    #     'mean numeric1', 'mean numeric2', 'nr_true boolean1', 'nr_true boolean2', 'percentage_true boolean1', 'percentage_true boolean2'
    # ]

    assert summary["mean numeric1"] == 2
    assert summary["mean numeric2"] == 5
    assert summary["nr_true boolean1"] == 2
    assert summary["nr_true boolean2"] == 2
    assert summary["percentage_true boolean1"] == pytest.approx(2/3*100)
    assert summary["percentage_true boolean2"] == pytest.approx(2/3*100)
