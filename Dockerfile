# Specifying the base image
FROM python:3.12-bookworm

# Install system dependencies and pip
RUN apt-get update -y && apt-get install --no-install-recommends -y \
    python3-pip

RUN apt install nano -y

# install poetry
RUN pip install poetry

# Installing the requirements
RUN poetry install

# Run streamlit app using SERVER_PORT environment variable
CMD ["streamlit", "run", "app.py", "--server.port=$SERVER_PORT"] 
