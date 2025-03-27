FROM python:3.10-slim

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -ms /bin/bash appuser

RUN pip3 install --no-cache-dir --upgrade \
    pip \
    virtualenv

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git

USER appuser
WORKDIR /home/appuser

# RUN git clone https://github.com/streamlit/streamlit-example.git app
RUN git clone https://github.com/safem0de/streamlit_capstone app

ENV VIRTUAL_ENV=/home/appuser/venv
RUN virtualenv ${VIRTUAL_ENV}
RUN . ${VIRTUAL_ENV}/bin/activate && pip install -r app/requirements.txt

EXPOSE 8501

COPY run.sh /home/appuser
RUN chmod +x /home/appuser/run.sh

ENTRYPOINT ["./run.sh"]