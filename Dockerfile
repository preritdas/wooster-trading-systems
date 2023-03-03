FROM ubuntu:latest

# Install Python 3.10 and pip
RUN apt update && apt upgrade -y && apt autoremove -y && \
    apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get install -y sudo curl git python3.10 python3.10-dev && \
    curl https://bootstrap.pypa.io/get-pip.py | python3.10

# Install TA-Lib
RUN curl https://gist.githubusercontent.com/preritdas/7b1a4fcd6b3835e80cea4c27295464d4/raw/40b4e10bf81f5715ce5a2ea3ab4b0b339915ca57/install-talib-ubuntu.sh | bash

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . .

# Install the dependencies
RUN python3.10 -m pip install -U pip wheel && \
    python3.10 -m pip install --no-cache-dir -r requirements.txt

# Create wooster executable
RUN echo '#!/bin/bash\npython3.10 /app/main.py "$@"' > /usr/bin/wooster && \
    chmod +x /usr/bin/wooster

# Run bash
CMD ["wooster"]
