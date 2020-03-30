FROM alpine:3.12

LABEL maintainer ""

# Add project source
COPY ubi_serial_hack.py /usr/bin/ubi_serial_hack

# Install dependencies
RUN apk update \
&& apk add --no-cache \
  python3 \
  py3-paramiko \
  py3-scp

ENTRYPOINT ["ubi_serial_hack"]
