FROM python:3.11.11-slim-bookworm

#Install container dependencies
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential python3-dev libxml2-dev libffi-dev
RUN apt-get update && apt-get install -y gcc g++ libxml2 libxslt-dev libusb-dev libpcsclite-dev i2c-tools
RUN apt-get install --upgrade python3-setuptools -y
RUN apt-get install --fix-broken

# Set the working directory in the container
WORKDIR /app

COPY libnfc-1.8.0.tar.bz2 /app
RUN tar -xf libnfc-1.8.0.tar.bz2
RUN ./libnfc-1.8.0/configure --prefix=/usr --sysconfdir=/etc
RUN make
RUN make install
COPY libnfc.conf /etc/nfc/

# Copy the current directory contents into the container at /app
COPY requirements.txt /app

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ADD . /app

RUN chmod a+x run.sh

#Setup NFS share for /audio files so Sonos can see them
# Install necessary NFS server packages
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     nfs-kernel-server rpcbind portmap

# # Set appropriate permissions (adjust as needed)
# RUN chown nobody:nogroup ./audio
# RUN chmod 777 ./audio # Be cautious with 777 in production

# # Configure NFS exports
# RUN echo "/audio *(rw,sync,no_subtree_check,no_root_squash)" > /etc/exports

# Run app.py when the container launches
CMD ["./run.sh"]