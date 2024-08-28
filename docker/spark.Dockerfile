ARG SPARK_VERSION ES_VERSION

FROM curlimages/curl:8.9.1

ENV SPARK_VERSION=${SPARK_VERSION:-7.17.23} ES_VERSION=${ES_VERSION:-7.17.23}

USER root

RUN curl "https://repo1.maven.org/maven2/org/elasticsearch/elasticsearch-spark-30_2.12/7.17.23/elasticsearch-spark-30_2.12-$ES_VERSION.jar" -o /mnt/elasticsearch-spark.jar \
    && curl "https://github.com/vesoft-inc/nebula-exchange/releases/download/v3.8.0/nebula-exchange_spark_3.0-3.8.0.jar" -o /mnt/nebula-exchange_spark.jar \
    && curl "https://repo1.maven.org/maven2/com/vesoft/nebula-spark-connector_3.0/3.8.1/nebula-spark-connector_3.0-3.8.1.jar" -o /mnt/nebula-spark-connector.jar

FROM bitnami/spark:${SPARK_VERSION:-3.3.4}

WORKDIR /opt/bitnami/spark

COPY --from=0 /mnt/*.jar /opt/bitnami/spark/jars/

ENV PATH=/opt/bitnami/python/bin:/opt/bitnami/java/bin:/opt/bitnami/spark/bin:/opt/bitnami/spark/sbin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin HOME=/ OS_ARCH=amd64 OS_FLAVOUR=debian-12 OS_NAME=linux APP_VERSION=3.3.4 BITNAMI_APP_NAME=spark JAVA_HOME=/opt/bitnami/java LD_LIBRARY_PATH=/opt/bitnami/python/lib:/opt/bitnami/spark/venv/lib/python3.8/site-packages/numpy.libs: LIBNSS_WRAPPER_PATH=/opt/bitnami/common/lib/libnss_wrapper.so NSS_WRAPPER_GROUP=/opt/bitnami/spark/tmp/nss_group NSS_WRAPPER_PASSWD=/opt/bitnami/spark/tmp/nss_passwd PYTHONPATH=/opt/bitnami/spark/python/: SPARK_HOME=/opt/bitnami/spark SPARK_USER=spark

SHELL [ "/bin/bash", "-o", "errexit", "-o", "nounset", "-o", "pipefail", "-c" ]

ENTRYPOINT [ "/opt/bitnami/scripts/spark/entrypoint.sh" ]

CMD [ "/opt/bitnami/scripts/spark/run.sh" ]
