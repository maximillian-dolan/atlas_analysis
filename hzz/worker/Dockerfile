# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install needed packages
RUN pip install awkward
RUN pip install uproot
RUN pip install vector
RUN pip install argparse
RUN pip install aiohttp
RUN pip install requests

# Run hzz_collector.py when the container launches
CMD ["python", "hzz_script.py"]