FROM hysds/pge-base

MAINTAINER aria-ops "aria-ops@list.jpl.nasa.gov"
LABEL description="GRFN PGE container"

USER ops

# copy ariamh code ensure proper permissions, and move dependencies to final locations
COPY . /home/ops/sentinel1-opds
RUN set -ex \
 && source /home/ops/verdi/bin/activate \
 && sudo chown -R ops:ops /home/ops/sentinel1-opds \
 && mv /home/ops/sentinel1-opds/ariamh /home/ops/  \
 && mv /home/ops/sentinel1-opds/qquery /home/ops/qquery \
 && mv /home/ops/sentinel1-opds/scihub /home/ops/scihub \
 && mv /home/ops/sentinel1-opds/unavco /home/ops/unavco \
 && mv /home/ops/sentinel1-opds/asf /home/ops/asf \
 && mv /home/ops/sentinel1-opds/apihub /home/ops/apihub \
 && cd /home/ops/qquery
 && pip install -e . \
 && cd /home/ops/scihub \
 && pip install -e . \
 && cd /home/ops/unavco \
 && pip install -e . \
 && cd /home/ops/asf \
 && pip install -e . \
 && cd /home/ops/apihub \
 && pip install -e .

# for sling_extract.py to be referenced by sling_extract_opds.py
ENV PYTHONPATH "${PYTHONPATH}:/home/ops/ariamh/frameMetadata"

# set entrypoint
WORKDIR /home/ops
CMD ["/bin/bash", "--login"]
