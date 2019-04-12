FROM opv-hugin

RUN apt-get update && apt-get install -y libpq-dev python3-dev imagemagick && rm -rf /var/lib/apt/lists/*

ENV OPV_TASKS_DBREST_ADDRESS dbrest
ENV OPV_TASKS_DBREST_PORT 5000
ENV OPV_TASKS_DIRMANAGER_ADDRESS directorymanager
ENV OPV_TASKS_DIRMANAGER_PORT 5015

COPY . /source/OPV_Tasks

WORKDIR /source/OPV_Tasks

RUN pip3 install -r requirements.txt && \
python3 setup.py install

WORKDIR /

CMD ["/bin/bash"]

RUN rm -rf /source/OPV_Tasks

