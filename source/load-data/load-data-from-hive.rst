从对象存储和 HDFS 加载数据
==========================

你可以通过数据库扩展 ``datalake_fdw``\ ，来将对象存储（例如 Amazon S3、青云、阿里云、华为云、腾讯云等）、HDFS 存储上的数据、Hive 上的 ORC 表，作为外部数据加载到 HashData Lightning 中，以进行数据查询/访问。

目前，支持加载的数据格式为 CSV、TEXT、ORC、PARQUET。

   注意，\ ``datalake_fdw`` 不支持并行加载数据。

本文介绍如下内容：

-  安装 ``datalake_fdw`` 扩展到数据库。
-  加载对象存储上的数据到 HashData Lightning。
-  加载 HDFS 上的数据到 HashData Lightning。

有关如何将 Hive 上的表加载到 HashData Lightning，参见\ `从 Hive 数仓加载数据 <https://hashdata.feishu.cn/wiki/CEU6wnMx8imXLskgULxcazcsn6f>`__\ 。

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

   .. list-table:: 配置选项
      :header-rows: 1
      :widths: auto

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
           * 公有云青云的 host：pek3b.qingstor.com
           * 私有云的 host：192.168.1.1:9000
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
        - 按照 virtual-host-style 还是 path-host-style 的方式来解析对象存储的主机。
        - 可选
        - - ``true``，即按照 virtual-host-style
          - ``false``，即按照 path-host-style
        - ``false``
        - /
      * - ``ishttps``
        - 访问对象存储是否使用 HTTPS。
        - 可选
        - - ``true``，即使用 HTTPS
          - ``false``，即不使用 HTTPS
        - ``false``
        - /

3. 创建用户映射。

   .. code:: sql

      CREATE USER MAPPING FOR gpadmin SERVER foreign_server 
      OPTIONS (user 'gpadmin', accesskey 'xxx', secretkey 'xxx');

   以上 SQL 语句中的选项说明如下：

   .. list-table::
      :header-rows: 1

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

4. 创建外表 ``example``\ 。创建完后，对象存储上的数据已经加载到 HashData Lightning，你可以对该表进行查询。

   .. code:: sql

      CREATE FOREIGN TABLE example(
      a text,
      b text
      )
      SERVER foreign_server 
      OPTIONS (filePath '/test/parquet/', compression 'none' , enableCache 'false', format 'parquet');

   以上 SQL 语句中的选项说明如下：

   .. list-table:: 配置选项
      :header-rows: 1
      :widths: auto

      * - 选项名
        - 描述
        - 是否可选
        - 配置项
        - 默认值
        - 说明
      * - ``filePath``
        - 设置目标外表的具体路径。
        - 必须设置
        - 路径规则为 `/bucket/prefix`。
          示例，假设用户访问的 bucket 名为 test-bucket，访问的路径为 bucket/test/orc_file_folder/，假设该路径下有多个文件 `0000_0`、`0001_1`、`0002_2`。
          那么访问 `0000_0` 文件的 `filePath` 可设置为 `filePath '/test-bucket/test/orc_file_folder/0000_0'`。
          如果要访问 `test/orc_file_folder/` 下的全部文件，`filePath` 可设置为 `filePath '/test-bucket/test/orc_file_folder/'`。
        - /
        - 注意，`filePath` 是按照 `/bucket/prefix/` 格式解析的，错误的格式可能导致错误，例如以下错误格式：
          * `filePath 'test-bucket/test/orc_file_folder/'`
          * `filePath '/test-bucket/test/orc_file_folder/0000_0'`
      * - ``compression``
        - 设置写的压缩格式。目前支持 snappy, gzip, zstd, lz4 格式。
        - 可选
        - - `none`，支持 CSV, ORC, TEXT, PARQUET 格式。
          - `snappy`，支持 CSV, TEXT, PARQUET 格式。
          - `gzip`，支持 CSV, TEXT, PARQUET 格式。
          - `zstd`，支持 PARQUET 格式。
          - `lz4`，支持 PARQUET 格式。
        - `none`，表示未压缩。不设置该值同样表示未压缩。
        - /
      * - ``enableCache``
        - 指定是否使用 Gopher 的缓存功能。
        - 可选
        - - `true`，即打开 Gopher 缓存。
          - `false`，即关闭 Gopher 缓存。
        - `false`
        - 删除外表并不会自动清理该表的缓存。要清理该外表的缓存，需要手动执行特定的 SQL 函数，例如：`select gp_toolkit.__gopher_cache_free_relation_name(text);`。
      * - ``format``
        - FDW 当前支持的文件格式。
        - 必须设置
        - - `csv`：可读、可写
          - `text`：可读、可写
          - `orc`：可读、可写
          - `parquet`：可读、可写
        - /
        - /

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

      .. list-table:: 配置选项
         :header-rows: 1

         * - 选项名
           - 描述
           - 是否可选
           - 配置项
           - 默认值
           - 说明
         * - ``protocol``
           - 指定 Hadoop 平台。
           - 必须设置
           - 固定为 `hdfs`，即 Hadoop 平台，不可修改。
           - `hdfs`
           - /
         * - ``hdfs_namenodes``
           - 指定访问 HDFS 的 namenode 主机。
           - 必须设置
           - /
           - /
           - 例如 `hdfs_namenodes '192.168.178.95:9000'`
         * - ``hdfs_auth_method``
           - 指定访问 HDFS 的认证模式。
           - 必须设置
           - - `simple`，即使用 Simple 认证（即无认证）模式访问 HDFS。
             - `kerberos`，即使用 Kerberos 认证模式访问 HDFS。
           - /
           - 如果要以 Simple 模式访问，请将选项值设为 `simple`，即 `hdfs_auth_method 'simple'`。
         * - ``hadoop_rpc_protection``
           - 用于配置建立 SASL 连接时的认证机制。此参数设置必须与 HDFS 配置文件 `core-site.xml` 中的 `hadoop.rpc.protection` 项值保持一致。
           - 必须设置
           - 有三个可选值，`authentication`、`integrity` 和 `privacy`。详细解释见 Hadoop [关于 `core-site.xml` 的说明文档](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/core-site.xml)。
           - /
           - /

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

      .. list-table:: 配置选项
         :header-rows: 1

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
           - 当 `is_ha_supported` 为 `true` 时，访问 HDFS HA 服务的名称。
           - 如果为 HDFS HA 集群，则必须设置。
           - 与 HDFS 配置文件 `hdfs-site.xml` 中的 `dfs.ha.namenodes.mycluster` 项保持一致即可。
           - /
           - 例如，如果 `dfs.ha.namenodes.mycluster` 为 `cluster`，则将本参数配置为 `dfs_nameservices 'mycluster'`。
         * - ``dfs_ha_namenodes``
           - 当 `is_ha_supported` 为 `true` 时，指定 HDFS HA 可访问的节点。
           - 如果为 HDFS HA 集群，则必须设置。
           - 与 HDFS 配置文件 `hdfs-site.xml` 中的 `dfs.ha.namenodes.mycluster` 项值保持一致即可。
           - /
           - 例如，`dfs_ha_namenodes 'nn1,nn2,nn3'`
         * - ``dfs_namenode_rpc_address``
           - 当 `is_ha_supported` 为 `true` 时，指定 HDFS HA 具体的高可用节点 IP 地址。
           - 如果为 HDFS HA 集群，则必须设置。
           - 参考 HDFS 的 `hdfs-site.xml` 中的 `dfs.ha_namenodes` 配置，节点地址即为配置文件中的 namenode 地址。
           - /
           - 例如，在 `dfs.ha.namenodes.mycluster` 中配置了三个 namenode 分别为 `nn1`、`nn2`、`nn3`，可根据 HDFS 配置文件找到 `dfs.namenode.rpc-address.mycluster.nn1`、`dfs.namenode.rpc-address.mycluster.nn2`、`dfs.namenode.rpc-address.mycluster.nn3` 配置的地址，再填入到字段中。例如：
             
             ```
             dfs_namenode_rpc_address '192.168.178.95:9000,192.168.178.160:9000,192.168.178.186:9000'
             ```
         * - ``dfs_client_failover_proxy_provider``
           - 指定 HDFS HA 是否开启故障转移。
           - 如果为 HDFS HA 集群，则必须设置。
           - 设置为默认值即可，即 `dfs_client_failover_proxy_provider 'org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider'`。
           - /
           - /


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

   +----------+----------+----------+----------+----------+----------+
   | 选项名   | 描述     | 是否可选 | 配置项   | 默认值   | 说明     |
   +==========+==========+==========+==========+==========+==========+
   | ``fi     | 设置目标 | 必须设置 | 路       |          | 注意     |
   | lePath`` | 外表的具 |          | 径规则为 |          | ，\ ``fi |
   |          | 体路径。 |          | ``       |          | lePath`` |
   |          |          |          | /bucket/ |          | 是按照   |
   |          |          |          | prefix`` |          | :lit     |
   |          |          |          | \ 。示例 |          | eral:`/` |
   |          |          |          | ，假设用 |          | `bucket/ |
   |          |          |          | 户访问的 |          | prefix/` |
   |          |          |          | bucket   |          | 格式解析 |
   |          |          |          | 名为     |          | 的，\ ** |
   |          |          |          | ``test-  |          | 错误的格 |
   |          |          |          | bucket`` |          | 式可能导 |
   |          |          |          | \ ，访问 |          | 致报错** |
   |          |          |          | 的路径为 |          | \ ，例如 |
   |          |          |          | ``t      |          | 以下错误 |
   |          |          |          | est/orc_ |          | 格式：-  |
   |          |          |          | file_fol |          | `        |
   |          |          |          | der/``\  |          | `filePat |
   |          |          |          | 。假设该 |          | h 'test- |
   |          |          |          | 路径下有 |          | bucket/t |
   |          |          |          | 多个文件 |          | est/orc_ |
   |          |          |          | ``0000   |          | file_fol |
   |          |          |          | _0``\ 、 |          | der/'``- |
   |          |          |          | \ ``0001 |          | `        |
   |          |          |          | _1``\ 、 |          | `filePat |
   |          |          |          | \ ``0002 |          | h '/test |
   |          |          |          | _2``\ 。 |          | -bucket/ |
   |          |          |          | 那么访问 |          | test/orc |
   |          |          |          | ``       |          | _file_fo |
   |          |          |          | 0000_0`` |          | lder/'`` |
   |          |          |          | 文件的   |          |          |
   |          |          |          | ``fi     |          |          |
   |          |          |          | lePath`` |          |          |
   |          |          |          | 可设置为 |          |          |
   |          |          |          | ``fil    |          |          |
   |          |          |          | ePath '/ |          |          |
   |          |          |          | test-buc |          |          |
   |          |          |          | ket/test |          |          |
   |          |          |          | /orc_fil |          |          |
   |          |          |          | e_folder |          |          |
   |          |          |          | /0000_0' |          |          |
   |          |          |          | ``\ 。如 |          |          |
   |          |          |          | 果要访问 |          |          |
   |          |          |          | `        |          |          |
   |          |          |          | `test/or |          |          |
   |          |          |          | c_file_f |          |          |
   |          |          |          | older/`` |          |          |
   |          |          |          | 下的     |          |          |
   |          |          |          | 全部文件 |          |          |
   |          |          |          | ，\ ``fi |          |          |
   |          |          |          | lePath`` |          |          |
   |          |          |          | 可设置为 |          |          |
   |          |          |          | ``fil    |          |          |
   |          |          |          | ePath '/ |          |          |
   |          |          |          | test-buc |          |          |
   |          |          |          | ket/test |          |          |
   |          |          |          | /orc_fil |          |          |
   |          |          |          | e_folder |          |          |
   |          |          |          | /'``\ 。 |          |          |
   +----------+----------+----------+----------+----------+----------+
   | ``compr  | 设       | 可选     | -        | ``       |          |
   | ession`` | 置写的压 |          | ``none`` | none``\  |          |
   |          | 缩格式。 |          | \ ，支持 | ，表示未 |          |
   |          | 目前支持 |          | CSV、ORC | 压缩。不 |          |
   |          | snappy、 |          | 、TEXT、 | 设置该值 |          |
   |          | gzip、z  |          | PARQUET  | 同样表示 |          |
   |          | std、lz4 |          | 格式。-  | 未压缩。 |          |
   |          | 格式。   |          | ``       |          |          |
   |          |          |          | snappy`` |          |          |
   |          |          |          | \ ，支持 |          |          |
   |          |          |          | CSV      |          |          |
   |          |          |          | 、TEXT、 |          |          |
   |          |          |          | PARQUET  |          |          |
   |          |          |          | 格式。-  |          |          |
   |          |          |          | ``gzip`` |          |          |
   |          |          |          | \ ，支持 |          |          |
   |          |          |          | CSV      |          |          |
   |          |          |          | 、TEXT、 |          |          |
   |          |          |          | PARQUET  |          |          |
   |          |          |          | 格式。-  |          |          |
   |          |          |          | ``zs     |          |          |
   |          |          |          | td``\ ， |          |          |
   |          |          |          | 支持     |          |          |
   |          |          |          | PARQUET  |          |          |
   |          |          |          | 格式。-  |          |          |
   |          |          |          | ``l      |          |          |
   |          |          |          | z4``\ ， |          |          |
   |          |          |          | 支持     |          |          |
   |          |          |          | PARQUET  |          |          |
   |          |          |          | 格式。   |          |          |
   +----------+----------+----------+----------+----------+----------+
   | ``enabl  | 指定     | 可选     | -        | `        | 删除外表 |
   | eCache`` | 是否使用 |          | ``       | `false`` | 并不会自 |
   |          | Gopher   |          | true``\  |          | 动清理该 |
   |          | 的缓     |          | ，即打开 |          | 表的缓存 |
   |          | 存功能。 |          | Gopher   |          | 。要清理 |
   |          |          |          | 缓存。-  |          | 该外表的 |
   |          |          |          | ``f      |          | 缓存，需 |
   |          |          |          | alse``\  |          | 要手动执 |
   |          |          |          | ，即关闭 |          | 行特定的 |
   |          |          |          | Gopher   |          | SQL      |
   |          |          |          | 缓存。   |          | 函数，例 |
   |          |          |          |          |          | 如：\ `` |
   |          |          |          |          |          | select g |
   |          |          |          |          |          | p_toolki |
   |          |          |          |          |          | t.__goph |
   |          |          |          |          |          | er_cache |
   |          |          |          |          |          | _free_re |
   |          |          |          |          |          | lation_n |
   |          |          |          |          |          | ame(text |
   |          |          |          |          |          | );``\ 。 |
   +----------+----------+----------+----------+----------+----------+
   | ``       | FDW      | 必须设置 | -        |          |          |
   | format`` | 当前     |          | ``csv``  |          |          |
   |          | 支持的文 |          | \ ：可读 |          |          |
   |          | 件格式。 |          | ，可写-  |          |          |
   |          |          |          | ``text`` |          |          |
   |          |          |          | \ ：可读 |          |          |
   |          |          |          | ，可写-  |          |          |
   |          |          |          | ``orc``  |          |          |
   |          |          |          | \ ：可读 |          |          |
   |          |          |          | ，可写-  |          |          |
   |          |          |          | `        |          |          |
   |          |          |          | `parquet |          |          |
   |          |          |          | ``\ ：可 |          |          |
   |          |          |          | 读，可写 |          |          |
   +----------+----------+----------+----------+----------+----------+

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

      +----------+----------+----------+----------+----------+----------+
      | 选项名   | 描述     | 是否可选 | 配置项   | 默认值   | 说明     |
      +==========+==========+==========+==========+==========+==========+
      | ``       | 指定访问 | 必须设置 |          | /        | 例如     |
      | hdfs_nam | HDFS 的  |          |          |          | ``hdfs_n |
      | enodes`` | namenode |          |          |          | amenodes |
      |          | 主机。   |          |          |          |  '192.16 |
      |          |          |          |          |          | 8.178.95 |
      |          |          |          |          |          | :9000'`` |
      +----------+----------+----------+----------+----------+----------+
      | ``pr     | 指定     | 必须设置 | 固定为   | ``hdfs`` |          |
      | otocol`` | Hadoop   |          | ``hdfs   |          |          |
      |          | 平台。   |          | ``\ ，即 |          |          |
      |          |          |          | Hadoop   |          |          |
      |          |          |          | 平台。不 |          |          |
      |          |          |          | 可修改。 |          |          |
      +----------+----------+----------+----------+----------+----------+
      | ``auth_  | 指定访问 | 必须设置 | -        | /        |          |
      | method`` | HDFS     |          | ``ke     |          |          |
      |          | 的认证   |          | rberos`` |          |          |
      |          | 模式，即 |          | \ ，使用 |          |          |
      |          | Kerberos |          | Kerberos |          |          |
      |          | 认       |          | 认证     |          |          |
      |          | 证模式。 |          | 模式访问 |          |          |
      |          |          |          | HDFS。   |          |          |
      +----------+----------+----------+----------+----------+----------+
      | `        | 指定     | 必须设置 | 与       | /        |          |
      | `krb_pri | HDFS     |          | keytab   |          |          |
      | ncipal`` | keytab   |          | 中       |          |          |
      |          | 中设置的 |          | 具体的用 |          |          |
      |          | p        |          | 户信息保 |          |          |
      |          | rincipal |          | 持一致。 |          |          |
      |          | 用户。   |          | 你需要查 |          |          |
      |          |          |          | 看相关用 |          |          |
      |          |          |          | 户信息， |          |          |
      |          |          |          | 并设置该 |          |          |
      |          |          |          | 选项值。 |          |          |
      +----------+----------+----------+----------+----------+----------+
      | ``krb_pr | 指定     | 必须设置 | 选项     | /        |          |
      | incipal_ | HDFS     |          | 值需要与 |          |          |
      | keytab`` | keytab   |          | HDFS 中  |          |          |
      |          | 的具     |          | keytab   |          |          |
      |          | 体路径。 |          | 的实     |          |          |
      |          |          |          | 际路径保 |          |          |
      |          |          |          | 持一致。 |          |          |
      +----------+----------+----------+----------+----------+----------+
      | `        | 用于     | 必须设置 | 有三个   | /        |          |
      | `hadoop_ | 配置建立 |          | 可选值， |          |          |
      | rpc_prot | SASL     |          | \ ``auth |          |          |
      | ection`` | 连       |          | enticati |          |          |
      |          | 接时的认 |          | on``\ 、 |          |          |
      |          | 证机制。 |          | \ ``int  |          |          |
      |          | 此参数设 |          | egrity`` |          |          |
      |          | 置必须与 |          | 和       |          |          |
      |          | HDFS     |          | `        |          |          |
      |          | 配置文件 |          | `privacy |          |          |
      |          | `        |          | ``\ 。详 |          |          |
      |          | `core-si |          | 细解释见 |          |          |
      |          | te.xml`` |          | Hadoop   |          |          |
      |          | 中的     |          | `关于 <h |          |          |
      |          | `        |          | ttps://h |          |          |
      |          | `hadoop. |          | adoop.ap |          |          |
      |          | rpc.prot |          | ache.org |          |          |
      |          | ection`` |          | /docs/cu |          |          |
      |          | 项保     |          | rrent/ha |          |          |
      |          | 持一致。 |          | doop-pro |          |          |
      |          |          |          | ject-dis |          |          |
      |          |          |          | t/hadoop |          |          |
      |          |          |          | -common/ |          |          |
      |          |          |          | core-def |          |          |
      |          |          |          | ault.xml |          |          |
      |          |          |          | >`__\ `` |          |          |
      |          |          |          | core-sit |          |          |
      |          |          |          | e.xml``\ |          |          |
      |          |          |          |  `的说明 |          |          |
      |          |          |          | 文档 <h  |          |          |
      |          |          |          | ttps://h |          |          |
      |          |          |          | adoop.ap |          |          |
      |          |          |          | ache.org |          |          |
      |          |          |          | /docs/cu |          |          |
      |          |          |          | rrent/ha |          |          |
      |          |          |          | doop-pro |          |          |
      |          |          |          | ject-dis |          |          |
      |          |          |          | t/hadoop |          |          |
      |          |          |          | -common/ |          |          |
      |          |          |          | core-def |          |          |
      |          |          |          | ault.xml |          |          |
      |          |          |          | >`__\ 。 |          |          |
      +----------+----------+----------+----------+----------+----------+

-  为多节点 HA 集群创建外部服务器。HA 集群支持故障节点切换。有关 HDFS 高可用集群的说明，参见 Hadoop 文档 `HDFS High Availability Using the Quorum Journal Manager <https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html>`__\ 。

   要加载 HDFS HA 集群，你可以使用如下模板创建外部服务器：

   .. code:: sql

      CREATE SERVER foreign_server
              FOREIGN DATA WRAPPER datalake_fdw
              OPTIONS (hdfs_namenodes 'mycluster'， 
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

   +----------+----------+----------+----------+--------+----------+
   | 选项名   | 描述     | 是否可选 | 配置项   | 默认值 | 说明     |
   +==========+==========+==========+==========+========+==========+
   | ``i      | 指定是   | 必须设置 | 设为     | /      |          |
   | s_ha_sup | 否要访问 |          | ``true`` |        |          |
   | ported`` | HDFS HA  |          | 即可。   |        |          |
   |          | 服务     |          |          |        |          |
   |          | ，即高可 |          |          |        |          |
   |          | 用服务。 |          |          |        |          |
   |          | 如果打开 |          |          |        |          |
   |          | 则会加载 |          |          |        |          |
   |          | HA       |          |          |        |          |
   |          | 的       |          |          |        |          |
   |          | 配置参数 |          |          |        |          |
   |          | ，即本表 |          |          |        |          |
   |          | 中下面行 |          |          |        |          |
   |          | 的参数。 |          |          |        |          |
   +----------+----------+----------+----------+--------+----------+
   | ``df     | 当       | 如果为   | 与 HDFS  | /      | 例       |
   | s_namese | ``i      | HDFS HA  | 配置文件 |        | 如，如果 |
   | rvices`` | s_ha_sup | 集       | `        |        | ``dfs.   |
   |          | ported`` | 群，则必 | `hdfs-si |        | ha.namen |
   |          | 为       | 须设置。 | te.xml`` |        | odes.myc |
   |          | ``true`` |          | 中的     |        | luster`` |
   |          | 时，访问 |          | ``dfs.   |        | 为       |
   |          | HDFS HA  |          | ha.namen |        | ``clust  |
   |          | 服务     |          | odes.myc |        | er``\ ， |
   |          | 的名称。 |          | luster`` |        | 则将本参 |
   |          |          |          | 项保持一 |        | 数配置为 |
   |          |          |          | 致即可。 |        | ``df     |
   |          |          |          |          |        | s_namese |
   |          |          |          |          |        | rvices ' |
   |          |          |          |          |        | mycluste |
   |          |          |          |          |        | r'``\ 。 |
   +----------+----------+----------+----------+--------+----------+
   | ``df     | 当       | 如果为   | 与 HDFS  | /      | 例       |
   | s_ha_nam | ``i      | HDFS HA  | 配置文件 |        | 如，\ `` |
   | enodes`` | s_ha_sup | 集       | `        |        | dfs_ha_n |
   |          | ported`` | 群，则必 | `hdfs-si |        | amenodes |
   |          | 为       | 须设置。 | te.xml`` |        |  'nn1,nn |
   |          | ``true`` |          | 中的     |        | 2,nn3'`` |
   |          | 时，指定 |          | ``dfs.   |        |          |
   |          | HDFS HA  |          | ha.namen |        |          |
   |          | 可访问   |          | odes.myc |        |          |
   |          | 的节点。 |          | luster`` |        |          |
   |          |          |          | 项       |        |          |
   |          |          |          | 值保持一 |        |          |
   |          |          |          | 致即可。 |        |          |
   +----------+----------+----------+----------+--------+----------+
   | ``df     | 当       | 如果为   | 参考     | /      | 例如，在 |
   | s_nameno | ``i      | HDFS HA  | HDFS 的  |        | ``dfs.   |
   | de_rpc_a | s_ha_sup | 集       | `        |        | ha.namen |
   | ddress`` | ported`` | 群，则必 | `hdfs-si |        | odes.myc |
   |          | 为       | 须设置。 | te.xml`` |        | luster`` |
   |          | ``true`` |          | 中的     |        | 中配     |
   |          | 时，指定 |          | ``df     |        | 置了三个 |
   |          | HDFS HA  |          | s_ha_nam |        | namenode |
   |          | 具体的高 |          | enodes`` |        | 分别为   |
   |          | 可用节点 |          | 配置，   |        | ``n      |
   |          | IP       |          | 节点地址 |        | n1``\ 、 |
   |          | 地址。   |          | 即为配置 |        | \ ``nn2` |
   |          |          |          | 文件中的 |        | `\ 、\ ` |
   |          |          |          | namenode |        | `nn3``\  |
   |          |          |          | 地址。   |        | ，可根据 |
   |          |          |          |          |        | HDFS     |
   |          |          |          |          |        | 配置     |
   |          |          |          |          |        | 文件找到 |
   |          |          |          |          |        | ``dfs.   |
   |          |          |          |          |        | namenode |
   |          |          |          |          |        | .rpc-add |
   |          |          |          |          |        | ress.myc |
   |          |          |          |          |        | luster.n |
   |          |          |          |          |        | n1``\ 、 |
   |          |          |          |          |        | ``dfs.   |
   |          |          |          |          |        | namenode |
   |          |          |          |          |        | .rpc-add |
   |          |          |          |          |        | ress.myc |
   |          |          |          |          |        | luster.n |
   |          |          |          |          |        | n2``\ 、 |
   |          |          |          |          |        | ``       |
   |          |          |          |          |        | dfs.name |
   |          |          |          |          |        | node.rpc |
   |          |          |          |          |        | -address |
   |          |          |          |          |        | .myclust |
   |          |          |          |          |        | er.nn3`` |
   |          |          |          |          |        | 配置     |
   |          |          |          |          |        | 的地址， |
   |          |          |          |          |        | 再填入到 |
   |          |          |          |          |        | 字段中。 |
   |          |          |          |          |        | 例如：\  |
   |          |          |          |          |        |  ``sqldf |
   |          |          |          |          |        | s_nameno |
   |          |          |          |          |        | de_rpc_a |
   |          |          |          |          |        | ddress ' |
   |          |          |          |          |        | 192.168. |
   |          |          |          |          |        | 178.95:9 |
   |          |          |          |          |        | 000,192. |
   |          |          |          |          |        | 168.178. |
   |          |          |          |          |        | 160:9000 |
   |          |          |          |          |        | ,192.168 |
   |          |          |          |          |        | .178.186 |
   |          |          |          |          |        | :9000'`` |
   +----------+----------+----------+----------+--------+----------+
   | ``dfs_   | 指定     | 如果为   | 设置     |        |          |
   | client_f | HDFS HA  | HDFS HA  | 为默认值 |        |          |
   | ailover_ | 是       | 集       | 即可，即 |        |          |
   | proxy_pr | 否开启故 | 群，则必 | ``dfs_   |        |          |
   | ovider`` | 障转移。 | 须设置。 | client_f |        |          |
   |          |          |          | ailover_ |        |          |
   |          |          |          | proxy_pr |        |          |
   |          |          |          | ovider ' |        |          |
   |          |          |          | org.apac |        |          |
   |          |          |          | he.hadoo |        |          |
   |          |          |          | p.hdfs.s |        |          |
   |          |          |          | erver.na |        |          |
   |          |          |          | menode.h |        |          |
   |          |          |          | a.Config |        |          |
   |          |          |          | uredFail |        |          |
   |          |          |          | overProx |        |          |
   |          |          |          | yProvide |        |          |
   |          |          |          | r'``\ 。 |        |          |
   +----------+----------+----------+----------+--------+----------+

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

   +----------+----------+----------+----------+----------+----------+
   | 选项名   | 描述     | 是否可选 | 配置项   | 默认值   | 说明     |
   +==========+==========+==========+==========+==========+==========+
   | ``fi     | 设置目标 | 必须设置 | 路       |          | 注意     |
   | lePath`` | 外表的具 |          | 径规则为 |          | ，\ ``fi |
   |          | 体路径。 |          | ``       |          | lePath`` |
   |          |          |          | /bucket/ |          | 是按照   |
   |          |          |          | prefix`` |          | :lit     |
   |          |          |          | \ 。示例 |          | eral:`/` |
   |          |          |          | ，假设用 |          | `bucket/ |
   |          |          |          | 户访问的 |          | prefix/` |
   |          |          |          | bucket   |          | 格式解析 |
   |          |          |          | 名为     |          | 的，\ ** |
   |          |          |          | ``test-  |          | 错误的格 |
   |          |          |          | bucket`` |          | 式可能导 |
   |          |          |          | \ ，访问 |          | 致报错** |
   |          |          |          | 的路径为 |          | \ ，例如 |
   |          |          |          | ``t      |          | 以下错误 |
   |          |          |          | est/orc_ |          | 格式：-  |
   |          |          |          | file_fol |          | `        |
   |          |          |          | der/``\  |          | `filePat |
   |          |          |          | 。假设该 |          | h 'test- |
   |          |          |          | 路径下有 |          | bucket/t |
   |          |          |          | 多个文件 |          | est/orc_ |
   |          |          |          | ``0000   |          | file_fol |
   |          |          |          | _0``\ 、 |          | der/'``- |
   |          |          |          | \ ``0001 |          | `        |
   |          |          |          | _1``\ 、 |          | `filePat |
   |          |          |          | \ ``0002 |          | h '/test |
   |          |          |          | _2``\ 。 |          | -bucket/ |
   |          |          |          | 那么访问 |          | test/orc |
   |          |          |          | ``       |          | _file_fo |
   |          |          |          | 0000_0`` |          | lder/'`` |
   |          |          |          | 文件的   |          |          |
   |          |          |          | ``fi     |          |          |
   |          |          |          | lePath`` |          |          |
   |          |          |          | 可设置为 |          |          |
   |          |          |          | ``fil    |          |          |
   |          |          |          | ePath '/ |          |          |
   |          |          |          | test-buc |          |          |
   |          |          |          | ket/test |          |          |
   |          |          |          | /orc_fil |          |          |
   |          |          |          | e_folder |          |          |
   |          |          |          | /0000_0' |          |          |
   |          |          |          | ``\ 。如 |          |          |
   |          |          |          | 果要访问 |          |          |
   |          |          |          | `        |          |          |
   |          |          |          | `test/or |          |          |
   |          |          |          | c_file_f |          |          |
   |          |          |          | older/`` |          |          |
   |          |          |          | 下的     |          |          |
   |          |          |          | 全部文件 |          |          |
   |          |          |          | ，\ ``fi |          |          |
   |          |          |          | lePath`` |          |          |
   |          |          |          | 可设置为 |          |          |
   |          |          |          | ``fil    |          |          |
   |          |          |          | ePath '/ |          |          |
   |          |          |          | test-buc |          |          |
   |          |          |          | ket/test |          |          |
   |          |          |          | /orc_fil |          |          |
   |          |          |          | e_folder |          |          |
   |          |          |          | /'``\ 。 |          |          |
   +----------+----------+----------+----------+----------+----------+
   | ``compr  | 设       | 可选     | -        | ``       |          |
   | ession`` | 置写的压 |          | ``none`` | none``\  |          |
   |          | 缩格式。 |          | \ ，支持 | ，表示未 |          |
   |          | 目前支持 |          | CSV、ORC | 压缩。不 |          |
   |          | snappy、 |          | 、TEXT、 | 设置该值 |          |
   |          | gzip、z  |          | PARQUET  | 同样表示 |          |
   |          | std、lz4 |          | 格式。-  | 未压缩。 |          |
   |          | 格式。   |          | ``       |          |          |
   |          |          |          | snappy`` |          |          |
   |          |          |          | \ ，支持 |          |          |
   |          |          |          | CSV      |          |          |
   |          |          |          | 、TEXT、 |          |          |
   |          |          |          | PARQUET  |          |          |
   |          |          |          | 格式。-  |          |          |
   |          |          |          | ``gzip`` |          |          |
   |          |          |          | \ ，支持 |          |          |
   |          |          |          | CSV      |          |          |
   |          |          |          | 、TEXT、 |          |          |
   |          |          |          | PARQUET  |          |          |
   |          |          |          | 格式。-  |          |          |
   |          |          |          | ``zs     |          |          |
   |          |          |          | td``\ ， |          |          |
   |          |          |          | 支持     |          |          |
   |          |          |          | PARQUET  |          |          |
   |          |          |          | 格式。-  |          |          |
   |          |          |          | ``l      |          |          |
   |          |          |          | z4``\ ， |          |          |
   |          |          |          | 支持     |          |          |
   |          |          |          | PARQUET  |          |          |
   |          |          |          | 格式。   |          |          |
   +----------+----------+----------+----------+----------+----------+
   | ``enabl  | 指定     | 可选     | -        | `        | 删除外表 |
   | eCache`` | 是否使用 |          | ``       | `false`` | 并不会自 |
   |          | Gopher   |          | true``\  |          | 动清理该 |
   |          | 的缓     |          | ，即打开 |          | 表的缓存 |
   |          | 存功能。 |          | Gopher   |          | 。要清理 |
   |          |          |          | 缓存。-  |          | 该外表的 |
   |          |          |          | ``f      |          | 缓存，需 |
   |          |          |          | alse``\  |          | 要手动执 |
   |          |          |          | ，即关闭 |          | 行特定的 |
   |          |          |          | Gopher   |          | SQL      |
   |          |          |          | 缓存。   |          | 函数，例 |
   |          |          |          |          |          | 如：\ `` |
   |          |          |          |          |          | select g |
   |          |          |          |          |          | p_toolki |
   |          |          |          |          |          | t.__goph |
   |          |          |          |          |          | er_cache |
   |          |          |          |          |          | _free_re |
   |          |          |          |          |          | lation_n |
   |          |          |          |          |          | ame(text |
   |          |          |          |          |          | );``\ 。 |
   +----------+----------+----------+----------+----------+----------+
   | ``       | FDW      | 必须设置 | -        |          |          |
   | format`` | 当前     |          | ``csv``  |          |          |
   |          | 支持的文 |          | \ ：可读 |          |          |
   |          | 件格式。 |          | ，可写-  |          |          |
   |          |          |          | ``text`` |          |          |
   |          |          |          | \ ：可读 |          |          |
   |          |          |          | ，可写-  |          |          |
   |          |          |          | ``orc``  |          |          |
   |          |          |          | \ ：可读 |          |          |
   |          |          |          | ，可写-  |          |          |
   |          |          |          | `        |          |          |
   |          |          |          | `parquet |          |          |
   |          |          |          | ``\ ：可 |          |          |
   |          |          |          | 读，可写 |          |          |
   +----------+----------+----------+----------+----------+----------+
