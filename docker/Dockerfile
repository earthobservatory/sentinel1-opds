FROM hysds/pge-base

MAINTAINER aria-ops "aria-ops@list.jpl.nasa.gov"
LABEL description="GRFN PGE container"

USER ops

# copy ariamh code ensure proper permissions, and move dependencies to final locations
COPY . /home/ops/sentinel1-opds
RUN set -ex \
 && sudo chown -R ops:ops /home/ops/sentinel1-opds \
 && mv /home/ops/sentinel1-opds/ariamh /home/ops/  \
 && mv /home/ops/verdi/ops/sentinel1-opds/qquery /home/ops/verdi/ops/qquery \
 && mv /home/ops/verdi/ops/sentinel1-opds/scihub /home/ops/verdi/ops/scihub \
 && mv /home/ops/verdi/ops/sentinel1-opds/unavco /home/ops/verdi/ops/unavco \
 && mv /home/ops/verdi/ops/sentinel1-opds/asf /home/ops/verdi/ops/asf \
 && mv /home/ops/verdi/ops/sentinel1-opds/apihub /home/ops/verdi/ops/apihub \
 && cd /home/ops/verdi/ops/qquery \
 && pip install -e . \
 && cd /home/ops/verdi/ops/scihub \
 && pip install -e . \
 && cd /home/ops/verdi/ops/unavco \
 && pip install -e . \
 && cd /home/ops/verdi/ops/asf \
 && pip install -e . \
 && cd /home/ops/verdi/ops/apihub \
 && pip install -e .

ENV PYTHONPATH "${PYTHONPATH}:/home/ops/ariamh/frameMetadata"

# set entrypoint
WORKDIR /home/ops
CMD ["/bin/bash", "--login"]
