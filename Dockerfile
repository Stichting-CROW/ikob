FROM python:3.12-slim

# The ikobconfig and ikobrunner GUI require tk.
RUN apt-get update -y
RUN apt-get install tk -y

WORKDIR /app
COPY . /app

# Install ikob.
RUN pip install --upgrade pip
RUN pip install -e .[dev]
