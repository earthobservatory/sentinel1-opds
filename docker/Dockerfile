FROM hysds/pge-base

MAINTAINER aria-ops "aria-ops@list.jpl.nasa.gov"
LABEL description="GRFN PGE container"

USER ops

# copy ariamh code ensure proper permissions, and move dependencies to final locations
COPY . /home/ops/sentinel1-opds
RUN set -ex \
 && sudo chown -R ops:ops /home/ops/sentinel1-opds \
 && mv /home/ops/sentinel1-opds/ariamh /home/ops/ \

ENV PYTHONPATH "${PYTHONPATH}:/home/ops/ariamh/frameMetadata"

# set entrypoint
WORKDIR /home/ops
CMD ["/bin/bash", "--login"]
