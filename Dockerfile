FROM praekeltfoundation/python3-base:alpine
MAINTAINER Praekelt.org <sre@praekelt.org>

# Install marathon-acme
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Set up the entrypoint
COPY entrypoint.sh /scripts/marathon-acme-entrypoint.sh
ENTRYPOINT ["marathon-acme-entrypoint.sh"]

# Set up some defaults
EXPOSE 8000
VOLUME /var/lib/marathon-acme
WORKDIR /var/lib/marathon-acme
CMD ["/var/lib/marathon-acme"]
