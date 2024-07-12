从对象存储和 HDFS 加载数据
==========================

你可以通过数据库扩展 ``datalake_fdw``\ ，来将对象存储（例如 Amazon S3、青云、阿里云、华为云、腾讯云等）、HDFS 存储上的数据、Hive 上的 ORC 表，作为外部数据加载到 HashData Lightning 中，以进行数据查询/访问。

目前，支持加载的数据格式为 CSV、TEXT、ORC、PARQUET。

.. note:: ``datalake_fdw`` 不支持并行加载数据。

本文介绍如下内容：

-  安装 ``datalake_fdw`` 扩展到数据库。
-  加载对象存储上的数据到 HashData Lightning。
-  加载 HDFS 上的数据到 HashData Lightning。

有关如何将 Hive 上的表加载到 HashData Lightning，参见\ :ref:`从 Hive 数仓加载数据 <load-data/load-data-from-hive:从 hive 加载数据>`\ 。

安装扩展
--------

要安装 ``datalake_fdw`` 扩展到数据库，执行 SQL 语句 ``CREATE EXTENSION data_fdw;``\ 。

.. code:: sql

   CREATE EXTENSION datalake_fdw;

使用说明
--------

本节具体说明如何使用 ``datalake_fdw`` 将对象存储以及 HDFS 上的数据加载到 HashData Lightning。

使用 ``datalake_fdw`` 加载数据，需要先创建外部数据封装器（Foreign Data Wrapper，或 FDW），其中需要创建 FDW 服务器以及用户映射等内容。

加载对象存储上的数据
~~~~~~~~~~~~~~~~~~~~

你可以将 Amazon S3、青云、阿里云、腾讯云等对象存储上的数据加载到 HashData Lightning。步骤如下：

1. 创建外部表封装器 ``FOREIGN DATA WRAPPER``\ 。注意，以下 SQL 语句中暂时没有可选项，你需要准确执行该语句。

   .. code:: sql

      CREATE FOREIGN DATA WRAPPER datalake_fdw
      HANDLER datalake_fdw_handler
      VALIDATOR datalake_fdw_validator 
      OPTIONS ( mpp_execute 'all segments' );

2. 创建外部服务器 ``foreign_server``\ 。

   .. code:: sql

      CREATE SERVER foreign_server        
      FOREIGN DATA WRAPPER datalake_fdw        
      OPTIONS (host 'xxx', protocol 's3b', isvirtual 'false',ishttps 'false');

   以上 SQL 语句中的选项说明如下：

   .. raw:: latex

       \begingroup
       \renewcommand{\arraystretch}{1.5} % 调整表格行间距
       \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
       \setlength{\itemindent}{-20pt} % 调整列表缩进

   .. list-table:: 配置选项 1
      :header-rows: 1
      :widths: 6 12 6 16 5 15

      * - 选项名
        - 描述
        - 是否可选
        - 配置项
        - 默认值
        - 说明
      * - ``host``
        - 设置访问对象存储的主机 host 信息。
        - 必须设置
        - /
        - /
        - 示例：
           * 公有云青云的 ``host：pek3b.qingstor.com``
           * 私有云的 host：\ ``192.168.1.1:9000``
      * - ``protocol``
        - 指定对象存储对应的云平台。
        - 必须设置
        - - ``s3b``：即 Amazon Cloud（使用 v2 签名）
          - ``s3``：即 Amazon Cloud（使用 v4 签名）
          - ``ali``：即阿里云对象存储
          - ``qs``：即青云对象存储
          - ``cos``：即腾讯对象存储
          - ``huawei``：即华为对象存储
          - ``ks3``：即 Kingstor 对象存储
        - /
        - /
      * - ``isvirtual``
        - 按照 **virtual-host-style** 还是 **path-host-style** 的方式来解析对象存储的主机。
        - 可选
        - - ``true``，即按照 **virtual-host-style**
          - ``false``，即按照 **path-host-style**
        - ``false``
        - /
      * - ``ishttps``
        - 访问对象存储是否使用 HTTPS。
        - 可选
        - - ``true``，即使用 HTTPS
          - ``false``，即不使用 HTTPS
        - ``false``
        - /

   .. raw:: latex

       \endgroup

3. 创建用户映射。

   .. code:: sql

      CREATE USER MAPPING FOR gpadmin SERVER foreign_server 
      OPTIONS (user 'gpadmin', accesskey 'xxx', secretkey 'xxx');

   以上 SQL 语句中的选项说明如下：

   .. raw:: latex

       \begingroup
       \renewcommand{\arraystretch}{1.5} % 调整表格行间距
       \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
       \setlength{\itemindent}{-20pt} % 调整列表缩进

   .. list-table:: 配置选项 2
      :header-rows: 1
      :align: left
      :widths: auto

      * - 选项名
        - 描述
        - 是否可选
      * - ``user``
        - 创建 ``foreign_server`` 所指定的具体用户。
        - 必须设置
      * - ``accesskey``
        - 访问对象存储所需的密钥。
        - 必须设置
      * - ``secretkey``
        - 访问对象存储所需的密钥。
        - 必须设置

   .. raw:: latex

       \endgroup

4. 创建外表 ``example``\ 。创建完后，对象存储上的数据已经加载到 HashData Lightning，你可以对该表进行查询。

   .. code:: sql

      CREATE FOREIGN TABLE example(
      a text,
      b text
      )
      SERVER foreign_server 
      OPTIONS (filePath '/test/parquet/', compression 'none' , enableCache 'false', format 'parquet');

   以上 SQL 语句中的选项说明如下：

   .. raw:: latex

       \begingroup
       \renewcommand{\arraystretch}{1.5} % 调整表格行间距
       \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
       \setlength{\itemindent}{-20pt} % 调整列表缩进

   .. list-table:: 配置选项 3
      :header-rows: 1
      :widths: 8 9 5 20 9 15

      * - 选项名
        - 描述
        - 是否可选
        - 配置项
        - 默认值
        - 说明
      * - ``filePath``
        - 设置目标外表的具体路径。
        - 必须设置
        - 路径规则为 ``/bucket/prefix``。
  
          示例，假设用户访问的 bucket 名为 ``test-bucket``，访问的路径为 ``bucket/test/orc_file_folder/``，假设该路径下有多个文件 ``0000_0``、\ ``0001_1``、\ ``0002_2``。

          那么访问 ``0000_0`` 文件的 ``filePath`` 可设置为 ``filePath '/test-bucket/test/orc_file_folder/0000_0'``。

          如果要访问 ``test/orc_file_folder/`` 下的全部文件，\ ``filePath`` 可设置为 ``filePath '/test-bucket/test/orc_file_folder/'``。
        - /
        - 注意，``filePath`` 是按照 ``/bucket/prefix/`` 格式解析的，错误的格式可能导致错误，例如以下错误格式：

          - ``filePath 'test-bucket/test/orc_file_folder/'``
          - ``filePath '/test-bucket/test/orc_file_folder/0000_0'``
      * - ``compression``
        - 设置写的压缩格式。目前支持 snappy, gzip, zstd, lz4 格式。
        - 可选
        - - ``none``，支持 CSV, ORC, TEXT, PARQUET 格式。
          - ``snappy``，支持 CSV, TEXT, PARQUET 格式。
          - ``gzip``，支持 CSV, TEXT, PARQUET 格式。
          - ``zstd``，支持 PARQUET 格式。
          - ``lz4``，支持 PARQUET 格式。
        - ``none``，表示未压缩。不设置该值同样表示未压缩。
        - /
      * - ``enableCache``
        - 指定是否使用 Gopher 的缓存功能。
        - 可选
        - - ``true``，即打开 Gopher 缓存。
          - ``false``，即关闭 Gopher 缓存。
        - ``false``
        - 删除外表并不会自动清理该表的缓存。要清理该外表的缓存，需要手动执行特定的 SQL 函数，例如： ``select`` 
  
          ``gp_toolkit._gopher_cache_``
          
          ``free_relation_name``
          
          ``(text);``。

      * - ``format``
        - FDW 当前支持的文件格式。
        - 必须设置
        - - ``csv``：可读、可写
          - ``text``：可读、可写
          - ``orc``：可读、可写
          - ``parquet``：可读、可写
        - /
        - /

   .. raw:: latex

       \endgroup

加载 HDFS 上的数据
~~~~~~~~~~~~~~~~~~

你可以将 HDFS 上的数据加载到 HashData Lightning 中。下文分别介绍如何加载无认证机制的 HDFS 集群数据，以及如何加载带 Kerberos 认证机制的 HDFS 数据。同时，HashData Lightning 还支持加载 HDFS HA 高可用集群的数据，也在下文中介绍。

加载无认证机制的 HDFS 数据
^^^^^^^^^^^^^^^^^^^^^^^^^^

以 Simple 模式加载 HDFS 上的数据，即基础的 HDFS 模式，不使用复杂的安全认证机制。详情参见 Hadoop 文档 `Hadoop in Secure Mode <https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/SecureMode.html>`__\ 。步骤如下：

1. 创建外部表封装器 ``FOREIGN DATA WRAPPER``\ 。注意，以下 SQL 语句中暂时没有可选项，你需要准确执行该语句。

   .. code:: sql

      CREATE FOREIGN DATA WRAPPER datalake_fdw
      HANDLER datalake_fdw_handler
      VALIDATOR datalake_fdw_validator 
      OPTIONS ( mpp_execute 'all segments' );

2. 创建外部服务器。在这一步，你可以选择为单节点 HDFS，以及为 HA 高可用的 HDFS 创建外部服务器。

   -  为单节点 HDFS 创建外部服务器 ``foreign_server``\ ：

      .. code:: sql

         CREATE SERVER foreign_server FOREIGN DATA WRAPPER datalake_fdw
         OPTIONS (
             protocol 'hdfs',
             hdfs_namenodes '[192.168.178.95](http://192.168.178.95)',
             hdfs_port '9000',
             hdfs_auth_method 'simple', 
             hadoop_rpc_protection 'authentication');

      以上 SQL 语句中的选项说明如下：

      .. raw:: latex

          \begingroup
          \renewcommand{\arraystretch}{1.5} % 调整表格行间距
          \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
          \setlength{\itemindent}{-20pt} % 调整列表缩进

      .. list-table:: 配置选项 4
         :header-rows: 1
         :widths: 14 10 7 12 6 12

         * - 选项名
           - 描述
           - 是否可选
           - 配置项
           - 默认值
           - 说明
         * - ``protocol``
           - 指定 Hadoop 平台。
           - 必须设置
           - 固定为 ``hdfs``，即 Hadoop 平台，不可修改。
           - ``hdfs``
           - /
         * - ``hdfs_namenodes``
           - 指定访问 HDFS 的 namenode 主机。
           - 必须设置
           - /
           - /
           - 例如 ``hdfs_namenodes '192.168.178.95:9000'``
         * - ``hdfs_auth_method``
           - 指定访问 HDFS 的认证模式。
           - 必须设置
           - - ``simple``，即使用 Simple 认证（即无认证）模式访问 HDFS。
             - ``kerberos``，即使用 Kerberos 认证模式访问 HDFS。
           - /
           - 如果要以 Simple 模式访问，请将选项值设为 ``simple``，即 ``hdfs_auth_method 'simple'``。
         * - ``hadoop_rpc_protection``
           - 用于配置建立 SASL 连接时的认证机制。此参数设置必须与 HDFS 配置文件 ``core-site.xml`` 中的 ``hadoop.rpc.protection`` 项值保持一致。
           - 必须设置
           - 有三个可选值，\ ``authentication``\ 、\ ``integrity`` 和 ``privacy``。详细解释见 Hadoop `关于 core-site.xml 的说明文档 <https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/core-site.xml>`__\ 。
           - /
           - /

      .. raw:: latex

          \endgroup

   -  为多节点 HA 集群创建外部服务器。HA 集群支持故障节点切换。有关 HDFS 高可用集群的说明，参见 Hadoop 文档 `HDFS High Availability Using the Quorum Journal Manager <https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html>`__\ 。

      要加载 HDFS HA 集群，你可以使用如下模板创建外部服务器：

      .. code:: sql

         CREATE SERVER foreign_server
                 FOREIGN DATA WRAPPER datalake_fdw
                 OPTIONS (
                 protocol 'hdfs',
                 hdfs_namenodes 'mycluster',
                 hdfs_auth_method 'simple',
                 hadoop_rpc_protection 'authentication',
                 is_ha_supported 'true',
                 dfs_nameservices 'mycluster',
                 dfs_ha_namenodes 'nn1,nn2,nn3',
                 dfs_namenode_rpc_address '192.168.178.95:9000,192.168.178.160:9000,192.168.178.186:9000',
                 dfs_client_failover_proxy_provider 'org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider');

      在以上 SQL 语句中，\ ``protocol``\ 、\ ``hdfs_namenodes``\ 、\ ``hdfs_auth_method``\ 、\ ``hadoop_rpc_protection`` 的解释同上表单节点。HA 特定的选项解释如下：

      .. raw:: latex

          \begingroup
          \renewcommand{\arraystretch}{1.5} % 调整表格行间距
          \fontsize{6pt}{7pt}\selectfont % 设置表格字体大小
          \setlength{\itemindent}{-20pt} % 调整列表缩进

      .. list-table:: 配置选项 5
         :header-rows: 1
         :widths: 18 15 10 10 5 18

         * - 选项名
           - 描述
           - 是否可选
           - 配置项
           - 默认值
           - 说明
         * - ``is_ha_supported``
           - 指定是否要访问 HDFS HA 服务，即高可用服务。如果打开则会加载 HA 的配置参数，即本表中下列的参数。
           - 必须设置
           - 设为 `true` 即可。
           - /
           - /
         * - ``dfs_nameservices``
           - 当 ``is_ha_supported`` 为 `true` 时，访问 HDFS HA 服务的名称。
           - 如果为 HDFS HA 集群，则必须设置。
           - 与 HDFS 配置文件 ``hdfs-site.xml`` 中的 ``dfs.ha.namenodes.mycluster`` 项保持一致即可。
           - /
           - 例如，如果 ``dfs.ha.namenodes.mycluster`` 为 `cluster`，则将本参数配置为 ``dfs_nameservices 'mycluster'``。
         * - ``dfs_ha_namenodes``
           - 当 ``is_ha_supported`` 为 ``true`` 时，指定 HDFS HA 可访问的节点。
           - 如果为 HDFS HA 集群，则必须设置。
           - 与 HDFS 配置文件 ``hdfs-site.xml`` 中的 ``dfs.ha.namenodes.mycluster`` 项值保持一致即可。
           - /
           - 例如，\ ``dfs_ha_namenodes 'nn1,nn2,nn3'``
         * - ``dfs_namenode_rpc_address``
           - 当 ``is_ha_supported`` 为 ``true`` 时，指定 HDFS HA 具体的高可用节点 IP 地址。
           - 如果为 HDFS HA 集群，则必须设置。
           - 参考 HDFS 的 ``hdfs-site.xml`` 中的 ``dfs.ha_namenodes`` 配置，节点地址即为配置文件中的 ``namenode`` 地址。
           - /
           - 例如，在 ``dfs.ha.namenodes.mycluster`` 中配置了三个 namenode 分别为 ``nn1``\ 、\ ``nn2``\ 、\ ``nn3``\ ，可根据 HDFS 配置文件找到 ``dfs.namenode.rpc-address.mycluster.nn1``、\ ``dfs.namenode.rpc-address.mycluster.nn2``\ 、\ ``dfs.namenode.rpc-address.mycluster.nn3`` 配置的地址，再填入到字段中。例如：
             
             .. code:: 

                dfs_namenode_rpc_address '192.168.178.95:9000,192.168.178.160:9000,192.168.178.186:9000'

         * - ``dfs_client_failover_proxy``
            
              ``provider``
           - 指定 HDFS HA 是否开启故障转移。
           - 如果为 HDFS HA 集群，则必须设置。
           - 设置为默认值即可，即 ``dfs_client_failover_proxy_provider 'org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider'``。
           - /
           - /

      .. raw:: latex

          \endgroup

3. 创建用户映射。

   .. code:: sql

      CREATE USER MAPPING FOR gpadmin SERVER foreign_server 
      OPTIONS (user 'gpadmin');

   以上语句中，选项 ``user`` 表示创建 ``foreign_server`` 所指定的具体用户，为必须设置的参数。

4. 创建外表 ``example``\ 。创建完后，对象存储上的数据已经加载到 HashData Lightning，你可以对该表进行查询。

   .. code:: sql

      CREATE FOREIGN TABLE example(
      a text,
      b text
      )
      SERVER foreign_server 
      OPTIONS (filePath '/test/parquet/', compression 'none' , enableCache 'false', format 'parquet');

   以上 SQL 语句中的选项说明如下：

   .. raw:: latex

       \begingroup
       \renewcommand{\arraystretch}{1.5} % 调整表格行间距
       \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
       \setlength{\itemindent}{-20pt} % 调整列表缩进

   .. list-table:: 配置选项 6
      :header-rows: 1
      :widths: 8 9 5 20 9 15

      * - 选项名
        - 描述
        - 是否可选
        - 配置项
        - 默认值
        - 说明
      * - ``filePath``
        - 设置目标外表的具体路径。
        - 必须设置
        - 路径规则为 ``/bucket/prefix``。
  
          示例，假设用户访问的 bucket 名为 ``test-bucket``，访问的路径为 ``bucket/test/orc_file_folder/``，假设该路径下有多个文件 ``0000_0``、\ ``0001_1``、\ ``0002_2``。

          那么访问 ``0000_0`` 文件的 ``filePath`` 可设置为 ``filePath '/test-bucket/test/orc_file_folder/0000_0'``。

          如果要访问 ``test/orc_file_folder/`` 下的全部文件，\ ``filePath`` 可设置为 ``filePath '/test-bucket/test/orc_file_folder/'``。

        - /
        - 注意，\ ``filePath`` 是按照 ``/bucket/prefix/`` 格式解析的，错误的格式可能导致错误，例如以下错误格式：
  
           -  ``filePath 'test-bucket/test/orc_file_folder/'``
           -  ``filePath '/test-bucket/test/orc_file_folder/0000_0'``
      * - ``compression``
        - 设置写的压缩格式。目前支持 snappy, gzip, zstd, lz4 格式。
        - 可选
        - - ``none``，支持 CSV, ORC, TEXT, PARQUET 格式。
          - ``snappy``，支持 CSV, TEXT, PARQUET 格式。
          - ``gzip``，支持 CSV, TEXT, PARQUET 格式。
          - ``zstd``，支持 PARQUET 格式。
          - ``lz4``，支持 PARQUET 格式。
        - ``none``，表示未压缩。不设置该值同样表示未压缩。
        - /
      * - ``enableCache``
        - 指定是否使用 Gopher 的缓存功能。
        - 可选
        - - ``true``\ ，即打开 Gopher 缓存。
          - ``false``，即关闭 Gopher 缓存。
        - ``false``
        - 删除外表并不会自动清理该表的缓存。要清理该外表的缓存，需要手动执行特定的 SQL 函数，例如：\ ``select``                 
         
          ``gp_toolkit._gopher_cache_``
          
          ``free_relation_name``
          
          ``(text);``。

      * - ``format``
        - FDW 当前支持的文件格式。
        - 必须设置
        - - ``csv``：可读、可写
          - ``text``：可读、可写
          - ``orc``：可读、可写
          - ``parquet``：可读、可写
        - /
        - /

   .. raw:: latex

       \endgroup

加载带 Kerberos 认证机制的 HDFS 数据
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

如果目标 HDFS 使用了 Kerberos 作为认证方式，你可以参照以下步骤加载 HDFS 上的数据到 HashData Lightning。

1. 创建外部表封装器 ``FOREIGN DATA WRAPPER``\ 。注意，以下 SQL 语句中暂时没有可选项，你需要准确执行该语句。

   .. code:: sql

      CREATE FOREIGN DATA WRAPPER datalake_fdw
      HANDLER datalake_fdw_handler
      VALIDATOR datalake_fdw_validator 
      OPTIONS ( mpp_execute 'all segments' );

2. 创建外部服务器。在这一步，你可以选择为单节点 HDFS，以及为 HA 高可用的 HDFS 创建外部服务器。

   -  为单节点 HDFS 创建外部服务器 ``foreign_server``\ ：

      .. code:: sql

         DROP SERVER foreign_server;

         CREATE SERVER foreign_server
                 FOREIGN DATA WRAPPER datalake_fdw
                 OPTIONS (hdfs_namenodes '192.168.3.32',
                 hdfs_port '9000',
                 protocol 'hdfs',
                 auth_method 'kerberos', 
                 krb_principal 'gpadmin/hdw-68212a9a-master0@GPADMINCLUSTER2.COM',
                 krb_principal_keytab '/home/gpadmin/hadoop.keytab',
                 hadoop_rpc_protection 'privacy'
                 );

      以上 SQL 语句中的选项解释如下：

      .. raw:: latex

          \begingroup
          \renewcommand{\arraystretch}{1.5} % 调整表格行间距
          \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
          \setlength{\itemindent}{-20pt} % 调整列表缩进

      .. list-table:: 配置选项 7
         :header-rows: 1
         :widths: 14 10 7 12 6 12

         * - 选项名
           - 描述
           - 是否可选
           - 配置项
           - 默认值
           - 说明
         * - ``hdfs_namenodes``
           - 指定访问 HDFS 的 namenode 主机。
           - 必须设置
           - /
           - /
           - 例如 ``hdfs_namenodes '192.168.178.95:9000'``
         * - ``protocol``
           - 指定 Hadoop 平台。
           - 必须设置
           - 固定为 ``hdfs``，即 Hadoop 平台，不可修改。
           - ``hdfs``
           - /
         * - ``auth_method``
           - 指定访问 HDFS 的认证模式，即 Kerberos 认证模式。
           - 必须设置
           - - ``kerberos``，使用 Kerberos 认证模式访问 HDFS。
           - /
           - /
         * - ``krb_principal``
           - 指定 HDFS keytab 中设置的 principal 用户。
           - 必须设置
           - 与 keytab 中具体的用户信息保持一致。你需要查看相关用户信息，并设置该选项值。
           - /
           - /
         * - ``krb_principal_keytab``
           - 指定 HDFS keytab 的具体路径。
           - 必须设置
           - 选项值需要与 HDFS 中 keytab 的实际路径保持一致。
           - /
           - /
         * - ``hadoop_rpc_protection``
           - 用于配置建立 SASL 连接时的认证机制。此参数设置必须与 HDFS 配置文件 ``core-site.xml`` 中的 ``hadoop.rpc.protection`` 项保持一致。
           - 必须设置
           - 有三个可选值，\ ``authentication``、\ ``integrity`` 和 ``privacy``。详细解释见 Hadoop `关于 core-site.xml 的说明文档 <https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/core-site.xml>`__\ 。
           - /
           - /

      .. raw:: latex

          \endgroup

-  为多节点 HA 集群创建外部服务器。HA 集群支持故障节点切换。有关 HDFS 高可用集群的说明，参见 Hadoop 文档 `HDFS High Availability Using the Quorum Journal Manager <https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html>`__\ 。

   要加载 HDFS HA 集群，你可以使用如下模板创建外部服务器：

   .. code:: sql

      CREATE SERVER foreign_server
              FOREIGN DATA WRAPPER datalake_fdw
              OPTIONS (hdfs_namenodes 'mycluster',
              protocol 'hdfs', 
              auth_method 'kerberos', 
              krb_principal 'gpadmin/hdw-68212a9a-master0@GPADMINCLUSTER2.COM',
              krb_principal_keytab '/home/gpadmin/hadoop.keytab', 
              hadoop_rpc_protection 'privacy',
              is_ha_supported 'true',
              dfs_nameservices 'mycluster',
              dfs_ha_namenodes 'nn1,nn2,nn3',
              dfs_namenode_rpc_address '192.168.178.95:9000,192.168.178.160:9000,192.168.178.186:9000',
              dfs_client_failover_proxy_provider 'org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider'
              );

   在以上 SQL 语句中，\ ``hdfs_namenodes``\ 、\ ``protocol``\ 、\ ``auth_method``\ 、\ ``krb_principal``\ 、\ ``krb_principal_keytab``\ 、\ ``hadoop_rpc_protection`` 的解释同上表单节点。HA 特定的选项解释如下：

   .. raw:: latex

       \begingroup
       \renewcommand{\arraystretch}{1.5} % 调整表格行间距
       \fontsize{6pt}{7pt}\selectfont % 设置表格字体大小
       \setlength{\itemindent}{-20pt} % 调整列表缩进

   .. list-table:: 配置选项 8
      :header-rows: 1
      :widths: 18 15 10 10 5 18

      * - 选项名
        - 描述
        - 是否可选
        - 配置项
        - 默认值
        - 说明
      * - ``is_ha_supported``
        - 指定是否要访问 HDFS HA 服务，即高可用服务。如果打开则会加载 HA 的配置参数，即本表中下列的参数。
        - 必须设置
        - 设为 ``true`` 即可。
        - /
        - /
      * - ``dfs_nameservices``
        - 当 ``is_ha_supported`` 为 ``true`` 时，访问 HDFS HA 服务的名称。
        - 如果为 HDFS HA 集群，则必须设置。
        - 与 HDFS 配置文件 ``hdfs-site.xml`` 中的 ``dfs.ha.namenodes.mycluster`` 项保持一致即可。
        - /
        - 例如，如果 ``dfs.ha.namenodes.mycluster`` 为 ``cluster``，则将本参数配置为 ``dfs_nameservices 'mycluster'``。
      * - ``dfs_ha_namenodes``
        - 当 ``is_ha_supported`` 为 ``true`` 时，指定 HDFS HA 可访问的节点。
        - 如果为 HDFS HA 集群，则必须设置。
        - 与 HDFS 配置文件 ``hdfs-site.xml`` 中的 ``dfs.ha.namenodes.mycluster`` 项值保持一致即可。
        - /
        - 例如，\ ``dfs_ha_namenodes 'nn1,nn2,nn3'``
      * - ``dfs_namenode_rpc_address``
        - 当 ``is_ha_supported`` 为 ``true`` 时，指定 HDFS HA 具体的高可用节点 IP 地址。
        - 如果为 HDFS HA 集群，则必须设置。
        - 参考 HDFS 的 ``hdfs-site.xml`` 中的 ``dfs.ha_namenodes`` 配置，节点地址即为配置文件中的 namenode 地址。
        - /
        - 例如，在 ``dfs.ha.namenodes.mycluster`` 中配置了三个 namenode 分别为 ``nn1``、\ ``nn2``、\ ``nn3``，可根据 HDFS 配置文件找到 ``dfs.namenode.rpc-address.mycluster.nn1``、\ ``dfs.namenode.rpc-address.mycluster.nn2``、 ``dfs.namenode.rpc-address.mycluster.nn3`` 配置的地址，再填入到字段中。例如：

          .. code:: 

             dfs_namenode_rpc_address '192.168.178.95:9000,192.168.178.160:9000,192.168.178.186:9000'

      * - ``dfs_client_failover_proxy_provider``
        - 指定 HDFS HA 是否开启故障转移。
        - 如果为 HDFS HA 集群，则必须设置。
        - 设置为默认值即可，即 ``dfs_client_failover_proxy_provider 'org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider'``。
        - /
        - /

   .. raw:: latex

       \endgroup

3. 创建用户映射。

   .. code:: sql

      CREATE USER MAPPING FOR gpadmin SERVER foreign_server 
      OPTIONS (user 'gpadmin');

   以上语句中，选项 ``user`` 表示创建 ``foreign_server`` 所指定的具体用户，为必须设置的参数。

4. 创建外表 ``example``\ 。创建完后，对象存储上的数据已经加载到 HashData Lightning，你可以对该表进行查询。

   .. code:: sql

      CREATE FOREIGN TABLE example(
      a text,
      b text
      )
      SERVER foreign_server 
      OPTIONS (filePath '/test/parquet/', compression 'none' , enableCache 'false', format 'parquet');

   以上 SQL 语句中的选项说明如下：

   .. raw:: latex

       \begingroup
       \renewcommand{\arraystretch}{1.5} % 调整表格行间距
       \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
       \setlength{\itemindent}{-20pt} % 调整列表缩进

   .. list-table:: 配置选项 9
      :header-rows: 1
      :widths: 8 9 5 20 9 15

      * - 选项名
        - 描述
        - 是否可选
        - 配置项
        - 默认值
        - 说明
      * - ``filePath``
        - 设置目标外表的具体路径。
        - 必须设置
        - 路径规则为 ``/bucket/prefix``。
  
          示例，假设用户访问的 bucket 名为 ``test-bucket``，访问的路径为 ``bucket/test/orc_file_folder/``，假设该路径下有多个文件 ``0000_0``、\ ``0001_1``、\ ``0002_2``。

          那么访问 ``0000_0`` 文件的 ``filePath`` 可设置为 ``filePath '/test-bucket/test/orc_file_folder/0000_0'``。

          如果要访问 ``test/orc_file_folder/`` 下的全部文件，\ ``filePath`` 可设置为 ``filePath '/test-bucket/test/orc_file_folder/'``。
        - /
        - 注意，\ ``filePath`` 是按照 ``/bucket/prefix/`` 格式解析的，错误的格式可能导致错误，例如以下错误格式：
  
          -  ``filePath 'test-bucket/test/orc_file_folder/'``
          - ``filePath '/test-bucket/test/orc_file_folder/0000_0'``
      * - ``compression``
        - 设置写的压缩格式。目前支持 snappy, gzip, zstd, lz4 格式。
        - 可选
        - - ``none``，支持 CSV, ORC, TEXT, PARQUET 格式。
          - ``snappy``，支持 CSV, TEXT, PARQUET 格式。
          - ``gzip``，支持 CSV, TEXT, PARQUET 格式。
          - ``zstd``，支持 PARQUET 格式。
          - ``lz4``，支持 PARQUET 格式。
        - ``none``，表示未压缩。不设置该值同样表示未压缩。
        - /
      * - ``enableCache``
        - 指定是否使用 Gopher 的缓存功能。
        - 可选
        - - ``true``，即打开 Gopher 缓存。
          - ``false``，即关闭 Gopher 缓存。
        - ``false``
        - 删除外表并不会自动清理该表的缓存。要清理该外表的缓存，需要手动执行特定的 SQL 函数，例如：\ ``select``

          ``gp_toolkit.__gopher_cache_``
           
          ``free_relation_name``

          ``(text);``。
      * - ``format``
        - FDW 当前支持的文件格式。
        - 必须设置
        - - ``csv``：可读、可写
          - ``text``：可读、可写
          - ``orc``：可读、可写
          - ``parquet``：可读、可写
        - /
        - /

   .. raw:: latex

       \endgroup