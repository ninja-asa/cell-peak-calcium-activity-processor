import os

from app.file.tables import read_from_file

# get directory of this file
dir_path = os.path.dirname(os.path.realpath(__file__))
samples_path = os.path.join(dir_path, "..", ".." , "samples")

def test_read_df_from_csv():
    # Arrange
    file_path = os.path.join(samples_path, "sample.csv")

    # Act
    result = read_from_file(file_path)

    # Assert
    assert result.shape == (21, 6)
    assert result.columns.tolist() == ['FRAMES', 'Time (sec)', 'cell 1', 'cell 2', 'cell 3', 'cell 4']

def test_read_df_from_excel():
    # Arrange
    file_path = os.path.join(samples_path, "sample.xlsx")

    # Act
    result = read_from_file(file_path)

    # Assert
    assert result.shape == (21, 4)
    assert result.columns.tolist() == ['FRAMES', 'Time (sec)', 'cell 1', 'cell 2']
