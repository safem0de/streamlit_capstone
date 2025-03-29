FROM python:3.10-slim

# -----------------------------
# Add app user
# -----------------------------
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 -ms /bin/bash appuser

# -----------------------------
# Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    curl \
    ca-certificates \
    tk \
    tcl \
    libtk8.6 \
    && rm -rf /var/lib/apt/lists/*


# -----------------------------
# Set environment variables
# -----------------------------
ENV VIRTUAL_ENV=/home/appuser/venv
ENV APP_HOME=/home/appuser/app

# -----------------------------
# Install Python tools
# -----------------------------
RUN pip install --no-cache-dir --upgrade pip virtualenv

# -----------------------------
# Create working directory
# -----------------------------
RUN mkdir -p ${APP_HOME}
WORKDIR ${APP_HOME}

# -----------------------------
# Copy everything
# -----------------------------
COPY . ${APP_HOME}
COPY run.sh /opt/run.sh

# -----------------------------
# Set permissions
# -----------------------------
RUN chmod +x /opt/run.sh && \
    chown -R 1000:1000 ${APP_HOME} /opt/run.sh

# -----------------------------
# Use non-root user
# -----------------------------
USER appuser

# -----------------------------
# Install Python dependencies
# -----------------------------
RUN bash -c "set -e; \
    echo '🚀 [1] Activating virtualenv' && \
    virtualenv ${VIRTUAL_ENV} && \
    . ${VIRTUAL_ENV}/bin/activate && \
    echo '🧠 [2] upgrade for compatible packages...' && \
    pip install --upgrade --force-reinstall pip setuptools wheel && \
    echo '📦 [3] Installing requirements...' && \
    pip install --no-cache-dir --force-reinstall -r ${APP_HOME}/requirements.txt && \
    echo '✅ [4] Requirements installed successfully' \
    "

# -----------------------------
# Expose port and define ENTRYPOINT
# -----------------------------
EXPOSE 8501
ENTRYPOINT ["/opt/run.sh"]
