# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install needed packages
RUN pip install awkward
RUN pip install uproot
RUN pip install vector
RUN pip install time
RUN pip install math
RUN pip install argparse
RUN pip install pickle

# Run hzz_collector.py when the container launches
CMD ["python", "hzz_counter.py"]