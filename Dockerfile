FROM praekeltfoundation/python-base:3.6

# Install marathon-acme
COPY docker-requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Set up the entrypoint
COPY docker-entrypoint.sh /scripts/marathon-acme-entrypoint.sh
ENTRYPOINT ["marathon-acme-entrypoint.sh"]

# Set up some defaults
EXPOSE 8000
VOLUME /var/lib/marathon-acme
WORKDIR /var/lib/marathon-acme
CMD ["/var/lib/marathon-acme"]
