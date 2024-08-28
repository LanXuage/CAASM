ARG ES_VERSION

FROM docker.elastic.co/elasticsearch/elasticsearch:${ES_VERSION:-7.17.23}

ENV ES_VERSION=${ES_VERSION:-7.17.23}

RUN curl https://release.infinilabs.com/analysis-ik/stable/elasticsearch-analysis-ik-${ES_VERSION}.zip -o /tmp/elasticsearch-analysis-ik.zip \
    && mkdir -p /usr/share/elasticsearch/plugins/ik \
    && unzip -d /usr/share/elasticsearch/plugins/ik /tmp/elasticsearch-analysis-ik.zip \
    && rm -rf /tmp/elasticsearch-analysis-ik.zip

WORKDIR /usr/share/elasticsearch

ENV ELASTIC_CONTAINER=true PATH=/usr/share/elasticsearch/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

EXPOSE 9200 9300

ENTRYPOINT [ "/bin/tini", "--", "/usr/local/bin/docker-entrypoint.sh" ]

CMD [ "eswrapper" ]