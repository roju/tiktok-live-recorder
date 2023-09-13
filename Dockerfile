######################################################
# Stage 1: Build image with Python and required tools
######################################################
FROM ubuntu:20.04 AS builder-image

# Avoid getting stuck on user prompts
ARG DEBIAN_FRONTEND=noninteractive

# Install Python and other build tools
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    python3.9 python3.9-dev python3.9-venv python3-pip python3-wheel build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and activate Python virtual environment
RUN python3.9 -m venv /home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"

# Install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir wheel && \
    pip3 install --no-cache-dir -r requirements.txt

######################################################
# Stage 2: Runner image with only runtime essentials
######################################################
FROM ubuntu:20.04 AS runner-image

# Install ffmpeg and Python runtime
RUN apt-get update && \
    apt-get install --no-install-recommends -y ffmpeg python3.9 python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a user and set permissions
RUN useradd --create-home myuser
USER myuser

# Copy virtual environment from builder image
COPY --from=builder-image /home/myuser/venv /home/myuser/venv

# Set work directory and copy code
WORKDIR /home/myuser/code
RUN mkdir /home/myuser/mp4s
COPY *.py .

# Environment settings
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"

# Set the CMD to execute your app
CMD ["python", "ttlr.py", "-user", "_ENTER_YOUR_USER_HERE_", "-mode", "auto", "-ffmpeg", "-out_dir", "/home/myuser/mp4s"]
