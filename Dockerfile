FROM python:3.10-slim

# Add appuser
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 -ms /bin/bash appuser

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up virtualenv
RUN pip install --no-cache-dir --upgrade pip virtualenv

ENV VIRTUAL_ENV=/home/appuser/venv
RUN virtualenv ${VIRTUAL_ENV}

# Copy code to /home/appuser/app
COPY . /home/appuser/app
COPY run.sh /opt/run.sh
RUN chmod +x /opt/run.sh && chown -R 1000:1000 /home/appuser /opt

USER appuser
WORKDIR /home/appuser/app

# Install Python packages
RUN . ${VIRTUAL_ENV}/bin/activate && pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["/opt/run.sh"]