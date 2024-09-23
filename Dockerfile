# Use the official Python base image
FROM python:3.12.1

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
RUN mkdir /app
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

# Upgrade pip and install the project dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files to the container
COPY . /app/
