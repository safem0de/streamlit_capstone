#!/bin/bash

set -e  # ถ้ามี error ใด ๆ ให้หยุดทันที

echo "✅ ENTRYPOINT STARTING"

APP_PID=

stopRunningProcess() {
    if test ! "${APP_PID}" = '' && ps -p ${APP_PID} > /dev/null ; then
        echo "🛑 Stopping Streamlit app with PID ${APP_PID}" > /proc/1/fd/1
        kill -TERM ${APP_PID}
        wait ${APP_PID}
        echo "✅ App shutdown cleanly" > /proc/1/fd/1
    else
        echo "⚠️ App was not running or already stopped" > /proc/1/fd/1
    fi
}

trap stopRunningProcess EXIT TERM

echo "🔍 Activating virtualenv..."
source ${VIRTUAL_ENV}/bin/activate

APP_FILE="${APP_HOME}/app.py"

if [ ! -f "${APP_FILE}" ]; then
  echo "❌ ERROR: ${APP_FILE} not found!"
  exit 1
fi

echo "🚀 Starting Streamlit..."
streamlit run ${APP_HOME}/app.py \
  --server.port 8501 \
  --server.enableCORS false \
  --server.enableXsrfProtection false &
APP_PID=$!

wait ${APP_PID}
