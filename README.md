# template-python-project
This is intended to be a repository to serve as a template to my own, and others projects using Python. 

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
