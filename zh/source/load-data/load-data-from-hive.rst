从 Hive 数仓加载数据
====================

Hive 数据仓库建立在 Hadoop 集群的 HDFS 上，因此 Hive 数据仓库中的数据也保存在 HDFS 上。HashData Lightning 支持使用扩展 Hive Connector 和 :ref:`datalake_fdw <load-data/load-data-from-oss-and-hdfs:从对象存储和 hdfs 加载数据>`\ ，将 Hive 集群中的表加载到 HashData Lightning 中。

Hive Connector 将 Hive 集群中的表加载为 HashData Lightning 的外表，该外表保存了 Hive 表中数据在 HDFS 上的路径。datalake_fdw 读取外表数据，由此将 Hive 上的数据加载到 HashData Lightning。

本文档介绍如何使用 Hive Connector 和 ``datalake_fdw`` 将 Hive 集群中的表加载到 HashData Lightning。

支持的 Hive 文件格式
--------------------

你可以将 TEXT、CSV、ORC、PARQUET、Iceberg、Hudi 格式的文件从 Hive 数仓加载到 HashData Lightning。

使用限制 
--------

-  不支持同步 Hive External Table。
-  不支持同步 Hive Table 统计信息。
-  HashData Lightning 可以读取 HDFS 上的数据，也可以往 HDFS 写数据，但是写入的数据无法被 Hive 读取。

.. note:: 

   问：HDFS 上的写更新是如何同步到 HashData Lightning 的？是否有限制？

   答：数据实际上还在 HDFS 上，而 Foreign Data Wrapper 只是读取 HDFS
   上的数据。

操作步骤
--------

使用 Hive Connector 的大致操作步骤如下：

1. 在 HashData Lightning 节点上创建配置文件，在配置文件中指定目标 Hive 集群和 HDFS 的信息。参见在 HashData Lightning 上创建配置文件。
2. 创建 Foreign Data Wrapper 和 Hive Connector 插件。
3. 创建 Server 和 User Mapping。
4. 将 Hive 对象加载到 HashData Lightning。可以选择加载 Hive 上单张表，也可以加载 Hive 上的数据库。

第 1 步：在 HashData Lightning 上创建配置文件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在 HashData Lightning 相关节点上创建配置文件，在配置文件中指定目标 Hive 集群和 HDFS 的信息。

配置 Hive 集群信息
^^^^^^^^^^^^^^^^^^

Hive Connector 支持 Hive 2.x 和 3.x 版本。你需要在 HashData Lightning 数据仓库的 Coordinator 节点和 Standby 节点创建名为 ``gphive.conf`` 的配置文件。

配置项
''''''

.. list-table::
   :header-rows: 1
   :align: left
   :widths: 8 20 8

   * - 配置项名
     - 描述
     - 默认值
   * - uris
     - Hive Metastore Service 监听地址（HMS 的主机名）
     - /
   * - auth_method
     - Hive Metastore Service 认证方法：simple 或 kerberos
     - simple
   * - krb_service_principal
     - Hive Metastore Service 的 Kerberos 认证需要的 service principal。使用 HMS HA 功能时需要将 principal 内的 instance 写成 ``_HOST``，例如 ``hive/_HOST@HASHDATA``。
     - /
   * - krb_client_principal
     - Hive Metastore Service 的 Kerberos 认证需要的 client principal。
     - /
   * - krb_client_keytab
     - Hive Metastore Service 的 Kerberos 认证需要的 client principal 对应的 keytab 文件。
     - /
   * - debug
     - Hive Connector debug flag：true 或 false
     - false

配置示例
''''''''

使用以下内容在 HashData Lightning 数据仓库 Coordinator 节点和 Standby 节点创建 ``gphive.conf`` 配置文件，将 ``expample.net:8083`` 替换成对应的 Hive Metastore Service 地址。

.. code:: yaml

   hive-cluster-1: #connector name
       uris: thrift://example.net:8083
       auth_method: simple

配置多个 Hive 集群
''''''''''''''''''

在 ``gphive.conf`` 内新增配置项即可，以下内容表示新增了一个名为 ``hive-cluster-2`` 的需要 Kerberos 验证的 Hive 集群，以及一个名为 ``hive-cluster-3`` 的需要 Kerberos 验证的 Hive HA 集群。

.. code:: yaml

   hive-cluster-1: #simple auth
       uris: thrift://example1.net:9083
       auth_method: simple

   hive-cluster-2: #kerberos auth
       uris: thrift://example2.net:9083
       auth_method: kerberos
       krb_service_principal: hive/hashdata@HASHDATA.CN
       krb_client_principal: user/hashdata@HASHDATA.CN
       krb_client_keytab: /home/gpadmin/user.keytab
       
   hive-cluster-3: #kerberos auth(HMS HA)
       uris: thrift://hms-primary.example2.net:9083,thrift://hms-standby.example2.net:9083
       auth_method: kerberos
       krb_service_principal: hive/_HOST@HASHDATA.CN
       krb_client_principal: user/hashdata@HASHDATA.CN
       krb_client_keytab: /home/gpadmin/user.keytab

配置 HDFS 集群信息
^^^^^^^^^^^^^^^^^^

Hive connector 需要 Hive 集群所在的 HDFS 集群的信息，从而创建外表，并用 ``datalake_fdw`` 插件对其读取。所以，需要在 HashData Lightning 的 Coordinator 节点和 Standby 节点提供名为 ``gphdfs.conf`` 的配置文件。

.. _配置项-1:

配置项
''''''

.. list-table::
   :header-rows: 1
   :align: left
   :widths: 8 20 8

   * - 配置项名
     - 描述
     - 默认值
   * - hdfs_namenode_host
     - 配置 HDFS 的 host 信息。如 ``"hdfs://mycluster"``，其中 ``hdfs://`` 可以省略。
     - /
   * - hdfs_namenode_port
     - 配置 HDFS 的端口信息。如果没配置，默认使用 9000。
     - ``9000``
   * - hdfs_auth_method
     - 配置 HDFS 身份验证模式。普通的 HDFS 使用 ``simple``。带有 Kerberos 的使用 ``kerberos``。
     - /
   * - krb_principal
     - Kerberos principal。当 ``hdfs_auth_method`` 设置 Kerberos 时设置。
     - /
   * - krb_principal_keytab
     - 用户生成的 keytab 放置的位置。
     - /
   * - hadoop_rpc_protection
     - 与 HDFS 集群配置文件 ``hdfs-site.xml`` 中的配置一致。
     - /
   * - data_transfer_protocol
     - HDFS 集群配置 Kerberos 时，有两种不同方式: 1. privileged resources 2. SASL RPC data transfer protection and SSL for HTTP。如果是第二种"SASL"的方式，这里需要设置 ``data_transfer_protocol`` 为 ``true``。
     - /
   * - is_ha_supported
     - 用户设置是否使用 ``hdfs-ha``。如果使用设置成 ``true``。不使用设置为 ``false``。默认为 ``false``。
     - ``false``


**hdfs-ha 配置说明**

``is_ha_supported`` 设置为 ``true`` 时程序才会读取 HA 的配置信息。用户将 ``hdfs-ha`` 的配置信息以 key-value 形式放在配置文件中，程序会依次读取所有 HA 的配置信息，所有的 HA 配置都需要与 hdfs 集群中对应的配置一致，并且，配置项的值必须为小写，如为大写，则必须转换为小写再配置。配置如下表所示：

.. list-table:: 配置选项
   :header-rows: 1
   :align: left
   :widths: 8 20 5

   * - 配置项名
     - 描述
     - 默认值
   * - ``dfs.nameservices``
     - HDFS 集群 NameServices 名字，以下配置中用 ``${service}`` 代替。
     - /
   * - ``dfs.ha.namenodes.${service}``
     - HDFS 中 NameService 为 ``${service}`` 的集群中的 NameNode 列表，多个 NameNode 用逗号隔开，以下配置中一个 NameNode 用 ``${node}`` 代替。
     - /
   * - ``dfs.namenode.rpc-address.${service}.${node}``
     - ``${service}`` 集群中名为 ``${node}`` 的 NameNode 的 rpc 地址。
     - /
   * - ``dfs.namenode.http-address.${service}.${node}``
     - ``${service}`` 集群中名为 ``${node}`` 的 NameNode 的 http 地址。
     - /
   * - ``dfs.client.failover.proxy.provider.${service}``
     - 用于与 ``${service}`` 集群中 Active NameNode 通信的 java class。
     - /


.. _配置示例-2:

配置示例
''''''''

以下配置文件中包含了三个 HDFS 集群的配置，分别为 ``paa_cluster``\ 、\ ``pab_cluster``\ 、\ ``pac_cluster``\ 。其中，\ ``paa_cluster`` 未使用 Kerberos 认证，未使用 ``hdfs-ha``\ 。\ ``pab_cluster`` 使用 Kerberos 认证，未使用 ``hdfs-ha``\ 。\ ``pac_cluster`` 使用 Kerberos 认证，使用两节点的 ``hdfs-ha`` 集群。

::

   paa_cluster:    
   # namenode host    
   hdfs_namenode_host: paa_cluster_master    
   # name port    
   hdfs_namenode_port: 9000    
   # authentication method    
   hdfs_auth_method: simple 
   # rpc protection    
   hadoop_rpc_protection: privacy
   data_transfer_protocol: true


   pab_cluster:    
   hdfs_namenode_host: pab_cluster_master    
   hdfs_namenode_port: 9000    
   hdfs_auth_method: kerberos    
   krb_principal: gpadmin/hdw-68212b9b-master0@GPADMINCLUSTER2.COM    
   krb_principal_keytab: /home/gpadmin/hadoop.keytab    
   hadoop_rpc_protection: privacy    
   data_transfer_protocol: true


   pac_cluster:    
   hdfs_namenode_host: pac_cluster_master    
   hdfs_namenode_port: 9000    
   hdfs_auth_method: kerberos    
   krb_principal: gpadmin/hdw-68212b9b-master0@GPADMINCLUSTER2.COM    
   krb_principal_keytab: /home/gpadmin/hadoop.keytab    
   hadoop_rpc_protection: privacy    
   is_ha_supported: true    
   dfs.nameservices: mycluster    
   dfs.ha.namenodes.mycluster: nn1,nn2    
   dfs.namenode.rpc-address.mycluster.nn1: 192.168.111.70:8020    
   dfs.namenode.rpc-address.mycluster.nn2: 192.168.111.71:8020    
   dfs.namenode.http-address.mycluster.nn1: 192.168.111.70:50070    
   dfs.namenode.http-address.mycluster.nn2: 192.168.111.71:50070    
   dfs.client.failover.proxy.provider.mycluster: org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailover..

第 2 步：创建 Foreign Data Wrapper 和 Hive Connector 插件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在同步前，先加载用于读 HDFS 的插件 datalake_fdw，创建读取外表的 Foreign Data Wrapper。

1. 创建 Foreign Data Wrapper。

   .. code:: sql

      CREATE EXTENSION datalake_fdw;

      CREATE FOREIGN DATA WRAPPER datalake_fdw
      HANDLER datalake_fdw_handler
      VALIDATOR datalake_fdw_validator
      OPTIONS (mpp_execute 'all segments');

2. 调用函数前需要创建 Hive Connector 插件。

   .. code:: sql

      CREATE EXTENSION hive_connector;

第 3 步：创建 Server 和 User Mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

创建 Foreign Data Wrapper 和 Hive Connector 后，需要创建 Server 和 User Mapping，示例如下：

.. code:: sql

   SELECT public.create_foreign_server('sync_server', 'gpadmin', 'datalake_fdw', 'hdfs-cluster-1');

以上示例中，\ ``create_foreign_server`` 函数的形式如下：

.. code:: sql

   create_foreign_server(serverName, 
                        userMapName, 
                        dataWrapName, 
                        hdfsClusterName);

此函数创建一个指向 HDFS 集群的 server 以及 user mapping，可以供 Hive Connector 创建 foreign table 时使用，datalake_fdw 读取外表时会根据 server 的配置从对应 HDFS 集群中读取数据。

函数中的参数解释如下：

-  ``serverName``\ ：要创建的 server 的名字。
-  ``userMapName`` ：要在 server 上创建的 user 的名字。
-  ``dataWrapName``\ ：用于读取 HDFS 数据的 data wrapper 的名字。
-  ``hdfsClusterName``\ ：Hive 集群所在的 HDFS 集群在配置文件中的名字。

执行此函数相当于执行：

.. code:: sql

   CREATE SERVER serverName FOREIGN DATA WRAPPER dataWrapName OPTIONS (......);
   CREATE USER MAPPING FOR userMapName SERVER serverName OPTIONS (user 'userMapName');

其中，\ ``OPTIONS (......)`` 内容会从配置文件中名为 ``hdfsClusterName`` 的配置中读取。

第 4 步：将 Hive 上的对象同步到 HashData Lightning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

同步一张 Hive 表
^^^^^^^^^^^^^^^^

将 Hive 上的一张表同步至 HashData Lightning，示例如下：

.. code:: sql

   -- 在 psql 内同步 Hive 表

   gpadmin=# select public.sync_hive_table('hive-cluster-1', 'mytestdb', 'weblogs', 'hdfs-cluster-1', 'mytestdb.weblogs', 'sync_server');
    sync_hive_table
   -----------------
    t
   (1 row)

以上示使用了 ``sync_hive_table`` 函数进行同步，该函数的一般形式如下：

.. code:: sql

   sync_hive_table(hiveClusterName, 
                  hiveDatabaseName,
                  hiveTableName,
                  hdfsClusterName, 
                  destTableName, 
                  serverName);

   sync_hive_table(hiveClusterName, 
                  hiveDatabaseName, 
                  hiveTableName, 
                  hdfsClusterName, 
                  destTableName, 
                  serverName, 
                  forceSync);

该函数同步一张表到 HashData Lightning，分为非强制与强制两种加载。在 forceSync 为 ``true`` 时强制同步，即在同步表时如果在 HashData Lightning 中已有重名表，则将现有重名表 DROP，再同步。没有 forceSync 参数或 forceSync 为 ``false`` 时视为非强制同步，遇到同名表会报错。

参数解释如下：

-  ``hiveClusterName`` 表示待同步表所在的 Hive 集群在配置文件中的名字。
-  ``hiveDatabaseName`` 表示待同步的表在 Hive 中所属的数据库名。
-  ``hiveTableName`` 表示待同步的表名。
-  ``hdfsClusterName`` 表示 Hive 集群所在的 HDFS 集群在配置文件中的名字。
-  ``destTableName`` 表示同步到 HashData Lightning 中的表名。
-  ``serverName`` 表示 ``datalake_fdw`` 插件创建 foreign table 时要使用的 server 的名字。
-  ``forceSync`` 表示在是否强制同步，强制则为 ``true``\ ，反之为 ``false``\ 。

同步一个 Hive 数据库
^^^^^^^^^^^^^^^^^^^^

以下示例将 Hive 上的一个数据库同步到 HashData Lightning：

.. code:: sql

   gpadmin=# select public.sync_hive_database('hive-cluster-1', 'default', 'hdfs-cluster-1', 'mytestdb', 'sync_server');
    sync_hive_database
   **--------------------
   ** t
   (1 row)

以上示例使用了 ``sync_hive_database`` 函数将进行同步。该函数的一般形式如下：

.. code:: sql

   sync_hive_database(hiveClusterName, 
                     hiveDatabaseName, 
                     hdfsClusterName, 
                     destSchemaName, 
                     serverName);
    
   sync_hive_database(hiveClusterName, 
                     hiveDatabaseName, 
                     hdfsClusterName, 
                     destSchemaName, 
                     serverName,
                     forceSync);

该函数同步一个 Hive 数据库到 HashData Lightning 的一个 schema 中，和同步一张表时相同，分为非强制与强制两种加载。在 forceSync 为 ``true`` 时强制同步，即在同步表时如果在 HashData Lightning 中已有重名表，则将现有重名表 DROP，再同步。没有 forceSync 参数或 forceSync 为 ``false`` 时视为非强制同步，遇到同名表会报错。

参数解释如下：

-  ``hiveClusterName`` 表示 Hive 集群在配置文件中的名字。

-  ``hiveDatabaseName`` 表示待同步的数据库名。

-  ``hdfsClusterName`` 表示 Hive 集群所在的 hdfs 集群在配置文件中的名字。

-  ``destSchemaName`` 表示同步到 HashData Lightning 中的 schema 名。

-  ``serverName`` 表示 datalake_fdw 插件创建 foreign table 时要使用的 server 的名字。

      **注意**

      以上函数所使用的接口说明如下：

      -  ``sync_hive_table`` 调用 HMS 的 ``thrift getTable`` 接口。
      -  ``sync_hive_database`` 调用 HMS 的 ``thrift getTables`` 和
         ``getTable`` 接口。

同步表格示例
------------

以下示例仅展示在 Hive 上建表和同步至 HashData Lightning 的命令，即仅展示上文中\ :ref:`第 4 步：将 Hive 上的对象同步至 HashData Lightning <load-data/load-data-from-hive:第 4 步：将 hive 上的对象同步到 hashdata lightning>`\ 。完整的操作还应包括该步骤之前的步骤。

同步一张 Hive Text 表
~~~~~~~~~~~~~~~~~~~~~

1. 在 Hive 上创建以下 Text 表。

   .. code:: sql

      -- 在 Beeline 内创建 Hive 表

      CREATE TABLE weblogs
      (
          client_ip           STRING,
          full_request_date   STRING,
          day                 STRING,
          month               STRING,
          month_num           INT,
          year                STRING,
          referrer            STRING,
          user_agent          STRING
      ) STORED AS TEXTFILE;

2. 将 Text 表同步至 HashData Lightning。

   .. code:: sql

      -- 在 psql 内同步 Hive 表

      gpadmin=# select public.sync_hive_table('hive-cluster-1', 'mytestdb', 'weblogs', 'hdfs-cluster-1', 'mytestdb.weblogs', 'sync_server');
      sync_hive_table
      -----------------
      t
      (1 row)

同步一张 Hive ORC 表
~~~~~~~~~~~~~~~~~~~~

1. 在 Hive 上创建一个 ORC 表。

   .. code:: sql

      -- 在 Beeline 内创建 Hive 表
      CREATE TABLE test_all_type
      (
          column_a tinyint,
          column_b smallint,
          column_c int,
          column_d bigint,
          column_e float,
          column_f double,
          column_g string,
          column_h timestamp,
          column_i date,
          column_j char(20),
          column_k varchar(20),
          column_l decimal(20, 10)
      ) STORED AS ORC;

2. 将 ORC 表同步至 HashData Lightning：

   .. code:: sql

      -- 在 psql 内同步表

      gpadmin=# select public.sync_hive_table('hive-cluster-1', 'mytestdb', 'test_all_type', 'hdfs-cluster-1', 'mytestdb.test_all_type', 'sync_server');
      sync_hive_table
      -----------------
      t
      (1 row)

同步一张 Hive ORC 分区表
~~~~~~~~~~~~~~~~~~~~~~~~

1. 在 Hive 上创建一个 ORC 分区表。

   .. code:: sql

      -- 在 Beeline 内创建 Hive 表

      CREATE TABLE test_partition_1_int
      (
          a tinyint,
          b smallint,
          c int,
          d bigint,
          e float,
          f double,
          g string,
          h timestamp,
          i date,
          j char(20),
          k varchar(20),
          l decimal(20, 10)
      )
      PARTITIONED BY
      (
          m int
      )
      STORED AS ORC;
      INSERT INTO test_partition_1_int VALUES (1, 1, 1, 1, 1, 1, '1', '2020-01-01 01:01:01', '2020-01-01', '1', '1', 10.01, 1);
      INSERT INTO test_partition_1_int VALUES (2, 2, 2, 2, 2, 2, '2', '2020-02-02 02:02:02', '2020-02-01', '2', '2', 11.01, 2);
      INSERT INTO test_partition_1_int VALUES (3, 3, 3, 3, 3, 3, '3', '2020-03-03 03:03:03', '2020-03-01', '3', '3', 12.01, 3);
      INSERT INTO test_partition_1_int VALUES (4, 4, 4, 4, 4, 4, '4', '2020-04-04 04:04:04', '2020-04-01', '4', '4', 13.01, 4);
      INSERT INTO test_partition_1_int VALUES (5, 5, 5, 5, 5, 5, '5', '2020-05-05 05:05:05', '2020-05-01', '5', '5', 14.01, 5);

2. 将 ORC 分区表同步至 HashData Lightning。

   .. code:: sql

      -- psql 将 Hive 分区表同步为一个 foreign table

      gpadmin=# select public.sync_hive_table('hive-cluster-1', 'mytestdb', 'test_partition_1_int', 'hdfs-cluster-1', 'mytestdb.test_partition_1_int', 'sync_server');
      sync_hive_table
      -----------------
      t
      (1 row)

3. 查看同步结果。

   .. code:: sql

      gpadmin=# \d mytestdb.test_partition_1_int;
                          Foreign table "mytestdb.test_partition_1_int"
      Column |            Type             | Collation | Nullable | Default | FDW options
      --------+-----------------------------+-----------+----------+---------+-------------
      a      | smallint                    |           |          |         |
      b      | smallint                    |           |          |         |
      c      | integer                     |           |          |         |
      d      | bigint                      |           |          |         |
      e      | double precision            |           |          |         |
      f      | double precision            |           |          |         |
      g      | text                        |           |          |         |
      h      | timestamp without time zone |           |          |         |
      i      | date                        |           |          |         |
      j      | character(20)               |           |          |         |
      k      | character varying(20)       |           |          |         |
      l      | numeric(20,10)              |           |          |         |
      m      | integer                     |           |          |         |
      Server: sync_server
      FDW options: (filepath '/opt/hadoop/apache-hive-3.1.0-bin/user/hive/warehouse/mytestdb.db/test_partition_1_int', hive_cluster_name 'hive-cluster-1', datasource 'mytestdb.test_partition_1_int', hdfs_cluster_name 'hdfs-cluster-1', enablecache 'true', transactional 'false', partitionkeys 'm', format 'orc')

.. _同步一个-hive-数据库-1:

同步一个 Hive 数据库
~~~~~~~~~~~~~~~~~~~~

1. 将 Hive 数据库同步至 HashData Lightning。

   .. code:: sql

      gpadmin=# select public.sync_hive_database('hive-cluster-1', 'default', 'hdfs-cluster-1', 'mytestdb', 'sync_server');
      sync_hive_database
      **--------------------
      ** t
      (1 row)

2. 查看结果。

   .. code:: sql

      gpadmin=# \d mytestdb.*
                                      List of relations
      Schema  |             Name              |       Type        |  Owner  | Storage
      ----------+-------------------------------+-------------------+---------+---------
      mytestdb | test_all_type                 | foreign table     | gpadmin |
      mytestdb | weblogs                       | foreign table     | gpadmin |
      mytestdb | test_csv_default_option       | foreign table     | gpadmin |
      mytestdb | test_partition_1_int          | foreign table     | gpadmin |
      (4 rows)

同步 Iceberg 和 Hudi 格式的表
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Apache Iceberg（下称 Iceberg）是一个开源的表格式，旨在改进大数据的存储、访问和处理。它为大规模数据仓库场景设计，提供了高效的数据存储和查询优化。Apache Hudi（下称 Hudi）是一个为数据湖提供高效存储管理的库，其目标是简化增量数据处理和流数据处理。

Hive 最初设计时并没有考虑到现代数据湖的一些需求，如实时数据处理和更细粒度的更新控制，但 Iceberg 和 Hudi 提供了与 Hive 兼容的接口。Iceberg 和 Hudi 为现代大数据平台提供了高效、灵活的数据管理能力，与传统的 Hive 数仓相比，它们在处理大规模数据集时可以提供更高的性能和更先进的数据管理特性。通过与 Hive 的集成，它们能够提供一条平滑的升级路径，帮助用户从传统的数据仓库架构过渡到更现代、更高效的数据平台解决方案。

Hive Connector 和 datalake_fdw 支持将 Iceberg 和 Hudi 格式的表加载到 HashData Lightning 中。

加载 Iceberg 表
^^^^^^^^^^^^^^^

1. 在 Hive 上创建 Iceberg 格式的表（以 Hive 2.3.2 为例）。

   .. code:: sql

      CREATE DATABASE icebergdb;
      USE icebergdb;

      CREATE TABLE iceberg_table1 (
          id int,
          name string,
          age int,
          address string
      ) STORED BY 'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler';

2. 在 HashData Lightning 中创建对应的外部表，并进行导入。

   .. code:: sql

      CREATE FOREIGN TABLE iceberg_table1 (
          id int,
          name text,
          age int,
          address text
      )
      server sync_server
      OPTIONS (filePath 'icebergdb.iceberg_table1', catalog_type 'hive', server_name 'hive-cluster-1', hdfs_cluster_name 'hdfs-cluster-1', table_identifier 'icebergdb.iceberg_table1', format 'iceberg');

   建表参数如下：

   -  ``catalog_type``\ ：填写 ``hive`` 或者 ``hadoop``\ 。
   -  ``filePath``
  
      -  如果 ``catalog_type`` 是 ``hive``\ ，则填写 ``<数据库名>.<表名>``\ 。
      -  如果 ``catalog_type`` 是 ``hadoop``\ ，则填写表在 HDFS 中的路径，例如 ``/user/hadoop/hudidata/``\ 。
  
   -  ``table_identifier``\ ：填写 ``<数据库名>.<表名>``\ 。
   -  ``format``\ ：填写 ``iceberg``\ 。

加载 Hudi 表
^^^^^^^^^^^^

1. 在 Spark 上创建 Hudi 格式的表，以 Spark 2.4.4 为例。

   .. code:: sql

      CREATE DATABASE hudidb;
      USE hudidb;

      _------ hudi_table1 ------_
      CREATE TABLE hudi_table1 (
          id int,
          name string,
          age int,
          address string
      ) using hudi;

2. 在 HashData Lightning 中创建对应的外部表。

   .. code:: sql

      CREATE FOREIGN TABLE hudi_table1 (
          id int,
          name text,
          age int,
          address text
      )
      server sync_server
      OPTIONS (filePath 'hudidb.hudi_table1', catalog_type 'hive', server_name 'hive-cluster-1', hdfs_cluster_name 'hdfs-cluster-1', table_identifier 'hudidb.hudi_table1', format 'hudi');

数据类型对照
------------

以下为 Hive 集群上表数据类型，与 HashData Lightning
表数据类型的一一对应关系。

.. table:: 
   :align: left

   ========= ==================
   Hive      HashData Lightning
   ========= ==================
   binary    bytea
   tinyint   smallint
   smallint  smallint
   int       int
   bigint    bigint
   float     float4
   double    double precision
   string    text
   timestamp timestamp
   date      date
   char      char
   varchar   varchar
   decimal   decimal
   ========= ==================

已知问题
--------

HashData Lightning Coordinator 和 Standby
节点在一台机器上时，由于使用的是一套配置，会出现端口占用的情况，导致
``dlagent`` 进程不断重启，CPU 占用率高。

解决方案
~~~~~~~~

1. 在 Standby 节点工作目录
   (``/home/gpadmin/workspace/cbdb_dev/gpAux/gpdemo/datadirs/standby/``)
   下创建 ``config`` 文件夹。

2. 在 ``config`` 目录下创建配置文件
   ``application.properties``\ ，修改端口 ``server.port``\ ，修改日志名
   ``logging.file.name``\ ，修改日志路径 ``logging.file.path``\ 。

   ``application.properties`` 文件如下：

   ::

      # Expose health, info, shutdown, metrics, and prometheus endpoints by default
      # 1. health: returns the status of the application {"status":"UP"}
      # 2. info: returns information about the build {"build":{"version":"X.X.X","artifact":"dlagent","name":"dlagent","group":"hashdata.cn","time":"timestamp"}}
      # 3. shutdown: allows shutting down the application
      # 4. metrics: shows ‘metrics’ information for the application
      # 5. prometheus: exposes metrics in a format that can be scraped by a Prometheus server
      management.endpoints.web.exposure.include=health,info,shutdown,metrics,prometheus
      management.endpoint.shutdown.enabled=true
      management.endpoint.health.probes.enabled=true
      # common tags applied to all metrics
      management.metrics.tags.application=dlagent
      # dlagent-specific metrics
      dlagent.metrics.partition.enabled=true
      dlagent.metrics.report-frequency=1000
      spring.profiles.active=default
      server.port=5888
      # Whitelabel error options
      server.error.include-message=always
      server.error.include-stacktrace=on_param
      server.error.include-exception=false
      server.server-header=DlAgent Server
      server.max-http-header-size=1048576
      # tomcat specific
      server.tomcat.threads.max=200
      server.tomcat.accept-count=100
      server.tomcat.connection-timeout=5m
      server.tomcat.mbeanregistry.enabled=true
      dlagent.tomcat.max-header-count=30000
      dlagent.tomcat.disable-upload-timeout=false
      dlagent.tomcat.connection-upload-timeout=5m
      # timeout (ms) for the request - 1 day
      spring.mvc.async.request-timeout=86400000
      dlagent.task.thread-name-prefix=dlagent-response-
      dlagent.task.pool.allow-core-thread-timeout=false
      dlagent.task.pool.core-size=8
      dlagent.task.pool.max-size=200
      dlagent.task.pool.queue-capacity=0
      # logging
      dlagent.log.level=info
      logging.config=classpath:log4j2-dlagent.xml
      logging.file.name=${MASTER_DATA_DIRECTORY:/home/gpadmin/workspace/cbdb_dev/gpAux/gpdemo/datadirs/standby/demoDataDir-1}/pg_log/dlagent.log
      logging.file.path=${MASTER_DATA_DIRECTORY:/home/gpadmin/workspace/cbdb_dev/gpAux/gpdemo/datadirs/standby/demoDataDir-1}/pg_log
