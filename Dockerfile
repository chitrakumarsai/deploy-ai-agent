# FROM python:3.13.5-slim-bullseye

# WORKDIR /app

# #RUN mkdir -p /app/static_folder

# # local path to the static folder
# # same as ./static_folder /static_folder under app directory if you do not specify WORKDIR then use RUN command
# COPY ./static_folder .

# CMD ["python3", "-m", "http.server", "8000"]