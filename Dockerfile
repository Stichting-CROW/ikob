FROM python:3.13-slim

# The ikobconfig and ikobrunner GUI require tk.
RUN apt-get update -y
RUN apt-get install tk -y

WORKDIR /app
COPY . /app

# Install ikob.
RUN pip install --upgrade pip
RUN pip install -e .[dev,deploy]

# By default, start the ikob runner. 
# If desired, ikobconfig may be supplied as alternative entrypoint
ENTRYPOINT [ "/app/src/ikob/ikobrunner.py" ]
