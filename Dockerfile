# Set base image (host OS)
FROM python:3.10.9

# By default, listen on port 5000
EXPOSE 3000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
RUN pip --default-timeout=5000 install tensorflow
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY app.py .
COPY lofi_generator/ ./lofi_generator


# Specify the command to run on container start
CMD [ "python", "./app.py" ]
