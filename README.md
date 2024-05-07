# cell-peak-calcium-activity-process

The goal with this repository is to support a scientific workflow to:
1. read time series for a variable number of cells with their respective peak calcium activity
2. process each time series to
    1. detect the peaks that are above a certain threshold
    2. record the amplitude of the greatest peak 
    3. record the time of the greatest peak
    4. record the amplitude of the first peak
    5. record the time of the first peak
    4. count number of peaks
    5. if any peak is detected, consider cell as active
3. obtain general statistics for the population of cells
    1. total number of cell
    2. number of active cells
    3. % of active cells
    4. average number of peaks per cell
    3. average amplitude of peaks
    4. ... (More to be defined)
4. plot the time series for each cell as a heatmap (x-axis: time, y-axis: cell number, color: amplitude)
5. Allow user to set the threshold for peak detection
6. Allow user to exclude first `n` samples or `t` time units from the time series
5. allow processing of multiple files
6. export (cell) results per excel file
7. export (population) results in a summary excel file (single file for all processed files)
8. allow user to edit column names in the excel files
9. be a web application

## Getting Started
- Clone the repository
- Open the repository in VSCode
- Setup intended Python version in the `Dockerfile.dev`
- Press `F1` and type `Remote-Containers: Reopen in Container`
- Start developing

## Features
### Docker-based development
This is tuned for VSCode and to support container based development.

You will find the `.vscode` directory with the files needed to make it work. However, before starting to develop, check the `python` version in the `Dockerfile.dev` - ensure you are using a version that suits your needs.

## Useful links:
- support status of `python` in the [Python Developer's Guide](https://devguide.python.org/versions/#versions).
- vulnerabilities in the [Mailing List by Python Software Foundation CVE Numbering Authority and Python Security Response Team](https://mail.python.org/archives/list/security-announce@python.org/latest).
- vulnerabilities in the

## Common Issues
### Dev Container Cannot Start - Issue with communicating with Docker Enginer
Repro steps:
- Ensure docker enginer is running
- Have the required base docker image stored cached 
- Attempt to `Open in Container` or `Rebuild and Open in Container` in repository

Issue:
- Visual Studio Code gets stuck
- Dev Containers extension Logs we can see an issue of Visual Studio Code server communicating with docker engine: whenever a docker command is called, an error with the API is reported

Attempts:
- Restart Visual Studio Code
- Restarted Docker
- Restart computer
  
Solution:
- Updated Docker

### Dev Container Cannot Start - Network issue
Repro steps:
- Ensure docker enginer is running
- Attempt to `Open in Container` or `Rebuild and Open in Container` in repository

Issue:
- Dev container cannot start building
 
Solution:
- Have no internet connectivity to get docker image from remote registry
