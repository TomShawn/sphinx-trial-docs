数据加载概览
============

HashData Lightning 主要通过加载工具将外部数据转换为外部表来加载数据。然后从这些外部表中读取数据，或将数据写入外部表中，以此实现外部数据加载。

数据加载流程
------------

加载数据进入 HashData Lightning 的一般流程如下：

1. 评估数据加载场景（例如数据源位置、数据类型和数据量），并选择合适的加载工具。
2. 配置和启用加载工具。
3. 创建外部表，指定 ``CREATE EXTERNAL TABLE`` 语句中的加载工具协议、数据源地址和数据格式。
4. 创建外部表后，可以直接使用 ``SELECT`` 语句查询外部表中的数据，或者使用 ``INSERT INTO SELECT`` 语句从外部表中导入数据。

加载工具和场景
--------------

HashData Lightning
提供了多种数据加载解决方案，你可以根据不同的数据源选择不同的数据加载方法。

.. list-table::
   :header-rows: 1
   :align: left
   :widths: 15 15 18 8

   * - 加载方法/工具
     - 数据源
     - 数据格式
     - 是否并行
   * - :ref:`COPY <load-data/load-data-from-local-files/load-data-using-copy:使用 copy 加载数据>`
     - 本地文件系统- Coordinator 节点主机（对于单文件）- Segment 节点主机（对于多文件）
     - - TXT
       - CSV
       - 二进制
     - 否
   * - :ref:`file:// <load-data/load-data-from-local-files/load-data-using-file-protocal:使用 file:// 协议加载数据>`
     - 本地文件系统（本地 Segment 主机，仅超级用户可访问）
     - - TXT
       - CSV
     - 是
   * - :ref:`gpfdist <load-data/load-data-from-local-files/load-data-using-gpfdist:使用 gpfdist 加载数据>`
     - 本地主机文件或者通过内网可访问的文件
     - - TXT
       - CSV
       - ``FORMAT`` 子句支持的任意分隔文本格式
       - XML 和 JSON（需要通过 YAML 配置文件转换为文本格式）
     - 是
   * - 使用 :ref:`gpload <load-data/load-data-from-local-files/load-data-using-gpload:使用 gpload 加载数据>` 批量加载（使用 ``gpfdist`` 为底层工作组件）
     - 本地主机文件或者可通过内网访问的文件
     - - TXT
       - CSV
       - ``FORMAT`` 子句支持的任意分隔文本格式
       - XML 和 JSON（需要通过 YAML 配置文件转换为文本格式）
     - 是
   * - :ref:`创建外部 Web 表 <load-data/load-data-from-web-services:从 web 服务加载数据>`
     - 从网络服务或可通过命令行访问的任意来源提取的数据
     - - TXT
       - CSV
     - 是
   * - :ref:`Kafka FDW <load-data/load-data-from-kafka:从 kafka 服务加载数据>`
     - Kafka
     - - CSV
       - JSON
     - 是
   * - :ref:`Data Lake Connector <load-data/load-data-from-oss-and-hdfs:从对象存储和 hdfs 加载数据>`
     - - 公有云对象存储（例如 Amazon S3、青云、阿里云、华为云、腾讯云等）
       - Hadoop 存储
     - - CSV
       - TEXT
       - ORC
       - PARQUET
     - 是
   * - :ref:`Hive Connector <load-data/load-data-from-hive:从 hive 数仓加载数据>` 搭配 ``data lake_fdw``
     - Hive 数据仓库
     - - CSV
       - TEXT
       - ORC
       - PARQUET
       - Iceberg（自 v1.5.2 支持）
       - Hudi（自 v1.5.2 支持）
     - 是
