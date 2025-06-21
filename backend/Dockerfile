FROM python:3.13.5-slim-bullseye


RUN apt-get update && apt-get install -y curl
# create python virtual environment
# isolated environment for python packages

RUN python -m venv /opt/venv
# Set the PATH environment variable to use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /tmp/requirements.txt

# Install the required Python packages
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./src .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]