#!/bin/bash

APP_PID=

stopRunningProcess() {
    if test ! "${APP_PID}" = '' && ps -p ${APP_PID} > /dev/null ; then
        echo "Stopping Streamlit app with process ID ${APP_PID}" > /proc/1/fd/1
        kill -TERM ${APP_PID}
        wait ${APP_PID}
        echo "All processes have stopped running" > /proc/1/fd/1
    else
        echo "App was not running or already stopped" > /proc/1/fd/1
    fi
}

trap stopRunningProcess EXIT TERM

source ${VIRTUAL_ENV}/bin/activate

streamlit run /home/appuser/app/app.py --server.port 8501 --server.enableCORS false &
APP_PID=$!

wait ${APP_PID}
