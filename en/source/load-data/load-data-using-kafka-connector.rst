Load Data from Kafka Using Kafka Connector
============================================

HashData Kafka Connector is a plugin based on the `Apache Kafka Connect <https://kafka.apache.org/documentation/#connect>`__ framework. It consumes data from Kafka topics and loads it into HashData tables, enabling scenarios such as data loading and real-time data warehousing.

Data Formats
-------------

The Kafka message data format supports the following three formats:

-  **Delimited Plain Text**

   .. code:: bash

      678,mike,abc
      456,jack,zzz

-  **JSON Format**

   .. code:: json

      {"id":"100","name":"zhangsan","address":"beijing"}
      {"id":"200","name":"lisi","address":"shanghai"}

-  **JSON Format for Change Data Capture (CDC)**

   Supports both DML (Data Manipulation Language) and DDL (Data Definition Language) operations, such as those in `debezium <https://debezium.io/>`__ format.

   .. code:: json

      // insert
      {
         "payload": {
            "before": null,
            "after": {
                  "c1": 10,
                  "c2": "abcd"
            },
            "source": {
                  "version": "2.1.1.Final",
                  "connector": "postgresql",
                  "name": "debezium",
                  "ts_ms": 1697280773034,
                  "snapshot": "false",
                  "db": "postgres",
                  "sequence": [
                     "23413560",
                     "23413848"
                  ],
                  "schema": "s2",
                  "table": "t2",
                  "txId": 771,
                  "lsn": 23413848,
                  "xmin": null
            },
            "op": "c",
            "ts_ms": 1697280773249,
            "transaction": null
         }
      }

      // delete
      {
         "payload": {
            "before": {
                  "c1": 11,
                  "c2": null
            },
            "after": null,
            "source": {
                  "version": "2.1.1.Final",
                  "connector": "postgresql",
                  "name": "debezium",
                  "ts_ms": 1697280877563,
                  "snapshot": "false",
                  "db": "postgres",
                  "sequence": [
                     "23415392",
                     "23415448"
                  ],
                  "schema": "s2",
                  "table": "t2",
                  "txId": 774,
                  "lsn": 23415448,
                  "xmin": null
            },
            "op": "d",
            "ts_ms": 1697280878032,
            "transaction": null
         }
      }

   When the Kafka message is in JSON CDC format, it supports DML (insert/update/delete) and DDL operations. For DML operations (insert/update/delete), the connector performs the following merge actions:

   -  Converts an update operation into a delete+insert operation.
   -  Operations on the same row (with the same primary key) will be merged. For example, if a row with the same primary key is updated 10,000 times, only the final value will be sent.
   -  During data loading, HashData uses its unique ``gpfdist`` external table method to load the merged result data to the target with maximum throughput:

      -  For inserts, it loads the data directly into the user table via ``gpfdist`` external tables.
      -  For deletes, it creates a temporary table, loads the delete data into this table via ``gpfdist``, and then performs a join delete operation (i.e., ``DELETE FROM user_table WHERE user_table.pk = temp_table.pk``) to update the user table.

   -  **HashData Installation Directory**: HashData Kafka Connector utilizes HashData’s unique gpfdist external table method to load data with maximum throughput. Therefore, the machine must have the HashData installation directory.

Installation
------------

Preparation
~~~~~~~~~~~

Before using HashData Kafka Connector, make sure to prepare the following components:

-  **Java JDK:** HashData Kafka Connector is released as a Java JAR file. Since Java is a cross-platform product, you only need to have the appropriate JDK installed on your system to run the connector. [`Download JDK here <https://www.oracle.com/technetwork/java/javase/downloads/index.html>`__].

-  **Kafka:** HashData Kafka Connector is based on the Kafka Connector framework, so it must run within the Kafka installation directory. [`Download Kafka here <https://kafka.apache.org/downloads>`__].

-  **HashData Kafka Connector JAR File:** Check the available versions to download the appropriate JAR file from HashData.

-  **Configuration File:**

   .. code:: python

      # entry class
      connector.class=cn.hashdata.kafka.connector.HashdataSinkConnector

      # task max number
      tasks.max=2

      # connector name
      name=z1connector

      # kafa topic name
      topics=delimited1topic

      # kafka topic message format
      hashdata.topic.format=delimited_file
      hashdata.format.delimiter=|

      # target table
      hashdata.topic.table=public.test1table

      # database connection info
      hashdata.url.name=jdbc:postgresql://192.168.176.110:5432/db1

      hashdata.user.name=gpadmin
      hashdata.user.password=gpadmin
      hashdata.database.name=db1

      # directory to put gpfdist data and kafka offset
      hashdata.data.dir=/xxx/hashdata_kafka_connector/data

      # data flush condition, e.g. here flush after consume 10k records or 5M bytes or 1 second
      buffer.count.records=10000
      buffer.size.bytes=5000000
      buffer.flush.time=1

      # converter
      key.converter=org.apache.kafka.connect.storage.StringConverter
      value.converter=org.apache.kafka.connect.storage.StringConverter

Installation Steps
~~~~~~~~~~~~~~~~~~

1. **Extract Kafka**.

   .. code:: bash

      tar xvfz kafka_2.13-3.1.0.tgz

2. **Edit the configuration file** ``kafka_2.13-3.1.0/config/connect-standalone.properties``.

   .. code:: bash

      # Modify the following two settings

      # 1.Kafka server address
      bootstrap.servers=localhost:9092

      # 2.Location of the HashData Kafka Connector JAR file
      plugin.path=/xxx/hashdata_kafka_connector/hashdata-kafka-connector-0.0.12.jar

3. **Edit** ``hashdata-kafka-connector-standalone.properties``. For example:

   .. code:: bash

      # Custom connector name
      name=zyzxconnector

      # Kafka topic to consume
      topics=zyzx1topic

      # Data format in the Kafka topic
      hashdata.topic.format=delimited_file
      hashdata.format.delimiter=|

      # HashData database connection details
      hashdata.url.name=jdbc:postgresql://192.168.176.110:5432/db1

      hashdata.user.name=gpadmin
      hashdata.user.password=gpadmin
      hashdata.database.name=db1

      # Directory for intermediate data: create this directory in advance with mkdir -p /xxx/hashdata_kafka_connector/data
      hashdata.data.dir=/xxx/hashdata_kafka_connector/data

   .. tip:: 

      Explanation of hashdata.data.dir

      This directory will store a metadata file that tracks the Kafka message offset that has been replicated. You can manually edit this file to skip unwanted data before restarting the connector.

4. **Set the HashData environment variables**.

   .. code:: bash

      source /<HashData installation directory>/greenplum_path.sh

5. **Start HashData Kafka Connector**.

   .. code:: bash

      kafka_2.13-3.1.0/bin/connect-standalone.sh -daemon kafka_2.13-3.1.0/config/connect-standalone.properties hashdata-kafka-connector-standalone.properties

Parameter Descriptions
----------------------

The following section explains the parameters in the ``hashdata-kafka-connector-standalone.properties`` file.

-  Kafka Connect Framework Parameters

   .. raw:: latex

       \begingroup
       \renewcommand{\arraystretch}{1.5} % 调整表格行间距
       \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
       \setlength{\itemindent}{-20pt} % 调整列表缩进

   .. list-table::
      :header-rows: 1
      :align: left

      * - **Parameter**
        - **Description**
        - **Example**
      * - **name**
        - Connector name
        - name=zyzxconnector
      * - **topics**
        - Kafka topic name
        - topics=zyzx1topic
      * - **tasks.max**
        - Number of tasks to run in the Kafka Connect framework, generally not exceeding the number of partitions in the topic.
        - tasks.max=2
      * - **connector.class**
        - Fixed value
        - connector.class=cn.hashdata.kafka.connector.HashdataSinkConnector
      * - **key.converter**
        - Fixed value
        - org.apache.kafka.connect.storage.StringConverter
      * - **value.converter**
        - Fixed value
        - org.apache.kafka.connect.storage.StringConverter

   .. raw:: latex

       \endgroup

-  Hashdata Kafka Conector Parameters

   -  Kafka Data Format Parameters

      .. raw:: latex

         \begingroup
         \renewcommand{\arraystretch}{1.5} % 调整表格行间距
         \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
         \setlength{\itemindent}{-20pt} % 调整列表缩进

      .. list-table::
         :header-rows: 1
         :align: left

         * - **Parameter**
           - **Description**
           - **Example**
         * - **hashdata.topic.format**
           - Format of the content in Kafka topics.
           - hashdata.topic.format=delimited_file
         * - **hashdata.format.delimiter**
           - Delimiter for plain text data in Kafka (non-JSON).
           - hashdata.format.delimiter=
         * - **hashdata.topic.table**
           - Target table name
           - hashdata.topic.table=schema1.table1

      .. raw:: latex

         \endgroup

   -  Database Connection Parameters

      .. raw:: latex

         \begingroup
         \renewcommand{\arraystretch}{1.5} % 调整表格行间距
         \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
         \setlength{\itemindent}{-20pt} % 调整列表缩进

      .. list-table::
         :header-rows: 1
         :align: left

         * - **Parameter**
           - **Description**
           - **Example**
         * - **hashdata.url.name**
           - Database JDBC connection string
           - hashdata.url.name=jdbc:postgresql://192.168.176.110:5432/db1
         * - **hashdata.user.name**
           - Database username
           - hashdata.user.name=gpadmin
         * - **hashdata.user.password**
           - Database user password
           - hashdata.user.password=gpadmin
         * - **hashdata.database.name**
           - Database name
           - hashdata.database.name=db1

      .. raw:: latex

         \endgroup

   -  Data Loading Real-time Parameters

      .. raw:: latex

         \begingroup
         \renewcommand{\arraystretch}{1.5} % 调整表格行间距
         \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
         \setlength{\itemindent}{-20pt} % 调整列表缩进

      .. list-table::
         :header-rows: 1
         :align: left

         * - **Parameter**
           - **Description**
           - **Example**
         * - **buffer.count.records**
           - Number of records to consume from Kafka before loading data into the database.
           - buffer.count.records=10000
         * - **buffer.size.bytes**
           - Size of consumed records from Kafka before loading data into the database.
           - buffer.size.bytes=5000000
         * - **buffer.flush.time**
           - Time to wait before loading data into the database.
           - buffer.flush.time=1

      .. raw:: latex

         \endgroup

   -  Working Directory Configuration

      .. raw:: latex

         \begingroup
         \renewcommand{\arraystretch}{1.5} % 调整表格行间距
         \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
         \setlength{\itemindent}{-20pt} % 调整列表缩进

      .. list-table:: 
         :header-rows: 1
         :align: left

         * - **Parameter**
           - **Description**
           - **Example**
         * - **hashdata.dir**
           - Working directory used during operation. This directory will store:
              - Kafka topic offsets (important, do not delete).
              - Other temporary files (will be deleted after operation).
           - hashdata.data.dir=/xxx/hashdata_kafka_connector/data
         * - **hashdata.ext.table.log.errors**
           - Whether to include a ``LOG ERRORS`` clause when creating the ``gpfdist`` external table. Useful for skipping invalid data during import into HashData.
           - hashdata.ext.table.log.errors=LOG ERRORS SEGMENT REJECT LIMIT 5
         * - **hashdata.table.upsert**
           - Specify if the ``INSERT ... SELECT ... FROM <gpfdist external table>`` statement should include an upsert clause. If present, it updates existing rows; otherwise, it performs a direct insert.
           - Example without upsert: ``insert into public.t1 select * from public_t1_0_ins_ext``.

             Example with upsert: ``insert into public.t1 select * from public_t1_0_ins_ext ON CONFLICT (c1) DO UPDATE SET c2 = EXCLUDED.c2, c3 = EXCLUDED.c3``.

      .. raw:: latex

         \endgroup

**Parameter Descriptions for** ``hashdata.topic.format``

The ``hashdata.topic.format`` parameter defines the format of data in the Kafka topic. The valid values and their descriptions are:

-  **delimited_file**: Data with delimiters.

   -  **Delimiter Example**: When ``hashdata.format.delimiter=|``, the Kafka topic messages appear as:

      ::

         678|mike|abc
         456|jack|zzz

   -  **Alternate Delimiter**: When ``hashdata.format.delimiter=@``, the Kafka topic messages appear as:

      ::

         678@mike@abc
         456@jack@zzz

-  **debeziumjson**: Data in `debezium <https://debezium.io/>`__ format.

   .. code:: json

      // insert
      {
         "payload": {
            "before": null,
            "after": {
                  "c1": 10,
                  "c2": "abcd"
            },
            "source": {
                  "version": "2.1.1.Final",
                  "connector": "postgresql",
                  "name": "debezium",
                  "ts_ms": 1697280773034,
                  "snapshot": "false",
                  "db": "postgres",
                  "sequence": [
                     "23413560",
                     "23413848"
                  ],
                  "schema": "s2",
                  "table": "t2",
                  "txId": 771,
                  "lsn": 23413848,
                  "xmin": null
            },
            "op": "c",
            "ts_ms": 1697280773249,
            "transaction": null
         }
      }

      // delete
      {
         "payload": {
            "before": {
                  "c1": 11,
                  "c2": null
            },
            "after": null,
            "source": {
                  "version": "2.1.1.Final",
                  "connector": "postgresql",
                  "name": "debezium",
                  "ts_ms": 1697280877563,
                  "snapshot": "false",
                  "db": "postgres",
                  "sequence": [
                     "23415392",
                     "23415448"
                  ],
                  "schema": "s2",
                  "table": "t2",
                  "txId": 774,
                  "lsn": 23415448,
                  "xmin": null
            },
            "op": "d",
            "ts_ms": 1697280878032,
            "transaction": null
         }
      }

      // update
      {
         "payload": {
            "before": {
                  "c1": 10,
                  "c2": "abcd"
            },
            "after": {
                  "c1": 10,
                  "c2": "upd-c2-kkk"
            },
            "source": {
                  "version": "2.1.1.Final",
                  "connector": "postgresql",
                  "name": "debezium",
                  "ts_ms": 1697285262028,
                  "snapshot": "false",
                  "db": "postgres",
                  "sequence": [
                     "23508840",
                     "23508896"
                  ],
                  "schema": "s2",
                  "table": "t3",
                  "txId": 784,
                  "lsn": 23508896,
                  "xmin": null
            },
            "op": "u",
            "ts_ms": 1697285262211,
            "transaction": null
         }
      }

   Note: When using ``debeziumjson``, the following parameters are
   ignored:

   -  ``hashdata.format.delimiter``
   -  ``hashdata.topic.table``

-  **zyzxjson/csgjson/ttjson**: Custom JSON data formats for specific clients.

   .. code:: json

      // DML

      {
         "_source_schema": "PUBLIC",
         "_source_table": "PERSON",
         "_committime": "2023-03-14 14:57:35.863",
         "_optype": "INSERT",
         "_seqno": "2261",
         "record": {
            "PKID": "825",
            "ID": "20211128",
            "NAME": "陈丽",
            "LOADING_DATE": "2023-03-14 00:00:00.0",
            "DELETE_FLAG": "1",
            "MOD_USER": "annoy",
            "MOD_USER_ID": "75589"
         }
      }

      {
         "_source_schema": "PUBLIC",
         "_source_table": "PERSON",
         "_committime": "2023-03-14 18:13:43.622",
         "_optype": "UPDATE",
         "_seqno": "2264",
         "record": {
            "PKID": "279",
            "ID": "20210582",
            "NAME": "赵欣",
            "LOADING_DATE": "2023-03-14 00:00:00.0",
            "DELETE_FLAG": "1",
            "MOD_USER": "admin",
            "MOD_USER_ID": "94950"
         },
         "key": {
            "PKID": "279"
         }
      }

      {
         "_source_schema": "PUBLIC",
         "_source_table": "PERSON",
         "_committime": "2023-03-17 15:02:05.19",
         "_optype": "DELETE",
         "_seqno": "2267",
         "record": {
            "PKID": "5"
         },
         "key": {
            "PKID": "5"
         }
      }

      // DDL

      {
         "_source_schema": "PUBLIC",
         "_committime": "2023-03-17 15:06:05.249",
         "_optype": "DDL",
         "_seqno": "2268",
         "record": "alter table PUBLIC.PERSON add add_column integer"
      }

Troubleshooting
---------------

HashData Kafka Connector’s log files are located in the ``kafka_2.13-3.1.0/logs`` directory. Check these files to troubleshoot issues.

To print more detailed information, you can adjust the logging level by editing the ``kafka_2.13-3.1.0/config/connect-log4j.properties`` file. Change the log level for the Kafka Connector from ``INFO`` to ``DEBUG`` by modifying the following line:

::

   log4j.logger.cn.hashdata=DEBUG

This will enable more detailed logging for troubleshooting.

References
----------

-  `APACHE KAFKA QUICKSTART <https://kafka.apache.org/quickstart>`__
-  `Kafka Connect <https://kafka.apache.org/documentation/#connect>`__
