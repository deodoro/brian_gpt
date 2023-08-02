# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app

RUN mkdir /app
COPY ./requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Add the current directory contents into the container at /app
COPY ./env /app/.env
COPY ./*.py /app/
COPY ./dist/* /var/www/

# Make port available to the world outside this container
ENV PORT 8080
EXPOSE 8080

WORKDIR /app
# Run the application
CMD ["python", "./server.py"]

