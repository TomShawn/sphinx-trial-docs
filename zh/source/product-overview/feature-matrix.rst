产品版本功能矩阵
================

.. note:: 

    -  ✅：已支持的功能。
    -  ❌：不支持该功能。

高效查询
--------

.. list-table:: 功能支持版本
   :header-rows: 1
   :align: left

   * - 功能名/版本号
     - 1.6.0
     - 1.5.4
     - 1.5.3
     - 1.5.2
     - 1.5.0
     - 1.4.0
     - 1.3.0
     - 1.2.0
     - 1.1.0
     - 1.0.0
   * - :ref:`optimize-performance/push-down-agg-operators:下推聚集运算`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - :ref:`optimize-performance/optimize-hashjoin-query-performance:优化 hashjoin 查询性能`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - :ref:`optimize-performance/use-index-scan-on-ao-tables:在 ao 表上使用索引扫描`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - :ref:`optimize-performance/create-index-in-parallel:并发创建索引`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - :ref:`optimize-performance/execute-queries-in-parallel:并行执行查询`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`operate-with-data/advanced-data-analytics/vectorization-queries:Vectorization 向量化查询计算`
     - ✅
     - ✅
     - ✅ [1]_
     - ✅
     - ✅ [2]_
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`optimize-performance/create-ao-aoco-tables-in-parallel-and-refresh-mtv:并行创建 AO/AOCO 表与刷新物化视图`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`optimize-performance/use-auto-mtv-for-query-optimization:使用自动物化视图进行查询优化`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`optimize-performance/use-incremental-mtv:使用增量物化视图`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`optimize-performance/use-unique-index-on-ao-tables:在 AO 表上使用唯一索引`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌

存储引擎
--------

.. list-table::
   :header-rows: 1
   :align: left

   * - 功能名/版本号
     - 1.6.0
     - 1.5.4
     - 1.5.3
     - 1.5.2
     - 1.5.0
     - 1.4.0
     - 1.3.0
     - 1.2.0
     - 1.1.0
     - 1.0.0
   * - Heap 和 AO 存储格式
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
   * - :ref:`operate-with-data/operate-with-database-objects/choose-table-storage-models/unionstore-table-format:UnionStore 存储格式`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`operate-with-data/operate-with-database-objects/choose-table-storage-models/pax-table-format:PAX 存储格式`
     - ✅ [7]_
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌

数据安全
--------

.. list-table:: 功能支持版本
   :header-rows: 1
   :align: left

   * - 功能名/版本号
     - 1.6.0
     - 1.5.4
     - 1.5.3
     - 1.5.2
     - 1.5.0
     - 1.4.0
     - 1.3.0
     - 1.2.0
     - 1.1.0
     - 1.0.0
   * - :ref:`manage-system/set-security-and-permission/use-pgcrypto:使用 pgcrypto 加密数据`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - :ref:`manage-system/set-security-and-permission/check-password-security:检查密码安全性`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - :ref:`manage-system/set-security-and-permission/use-anon:使用 Anon 脱敏数据`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - :ref:`manage-system/set-security-and-permission/use-tde-to-encrypt-data:透明数据加密`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`manage-system/set-security-and-permission/set-password-policy:配置密码策略`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`manage-system/set-security-and-permission/use-pgaudit:日志审计 pgaudit`
     - ✅
     - ✅ 
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌

容灾、备份和高可用
------------------

.. list-table::
   :header-rows: 1
   :align: left

   * - 功能名/版本号
     - 1.6.0
     - 1.5.4
     - 1.5.3
     - 1.5.2
     - 1.5.0
     - 1.4.0
     - 1.3.0
     - 1.2.0
     - 1.1.0
     - 1.0.0
   * - 高可用 FTS 说明
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - gpbackup 和 gprestore
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅

部署、运维、可视化和工具
------------------------

.. list-table::
   :header-rows: 1
   :align: left

   * - 功能名/版本号
     - 1.6.0
     - 1.5.4
     - 1.5.3
     - 1.5.2
     - 1.5.0
     - 1.4.0
     - 1.3.0
     - 1.2.0
     - 1.1.0
     - 1.0.0
   * - :ref:`deploy-guides/deploy-in-k8s:在 kubernetes 上部署`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - :ref:`deploy-guides/physical-deploy/visualized-deploy:可视化部署`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`operate-with-data/auto-execute-sql-commands:自动化执行 sql 语句`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`operate-with-data/view-and-operate-db-objects-using-web-platform:在网页编辑器中执行 sql 语句`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`deploy-guides/physical-deploy/manual-deploy/deploy-single-node:部署单计算节点`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - 使用 ``gpdemo`` 快速部署集群
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`manage-system/expand-and-shrink-cluster:扩缩容集群`
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - 在外部对象存储上创建表空间
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`manage-system/web-platform-monitoring/web-platform-monitoring-index:使用 web platform 查看集群监控数据`
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌

数据分析和计算
--------------

.. list-table::
   :header-rows: 1
   :align: left

   * - 功能名/版本号
     - 1.6.0
     - 1.5.4
     - 1.5.3
     - 1.5.2
     - 1.5.0
     - 1.4.0
     - 1.3.0
     - 1.2.0
     - 1.1.0
     - 1.0.0
   * - :ref:`components/zombodb:使用 zombodb 集成 elastic search`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅ [3]_
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - :ref:`operate-with-data/advanced-data-analytics/vectorization-queries:vectorization 向量化查询计算`
     - ✅
     - ✅
     - ✅ [4]_
     - ✅
     - ✅ [5]_
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`operate-with-data/advanced-data-analytics/pgvector-search:pgvector 向量相似搜索`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅ [6]_
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`operate-with-data/advanced-data-analytics/directory-tables:使用目录表纳管非结构化文件`
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`operate-with-data/advanced-data-analytics/roaringbitmap:使用 roaringbitmap 位图运算`
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`operate-with-data/advanced-data-analytics/postgis-analyses:使用 postgis 进行地理空间数据分析`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`operate-with-data/advanced-data-analytics/madlib-machine-learning:使用 madlib 进行机器学习和深度学习`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - PL/R
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - PL/Java
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌

数据加载/湖仓一体
-----------------

.. list-table::
   :header-rows: 1
   :align: left

   * - 功能名/版本号
     - 1.6.0
     - 1.5.4
     - 1.5.3
     - 1.5.2
     - 1.5.0
     - 1.4.0
     - 1.3.0
     - 1.2.0
     - 1.1.0
     - 1.0.0
   * - :ref:`load-data/load-data-from-local-files/load-data-using-gpfdist:使用 gpfdist 加载数据`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
   * - :ref:`load-data/load-data-from-local-files/load-data-using-copy:使用 copy 加载数据`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
   * - :ref:`load-data/load-data-from-local-files/load-data-using-file-protocal:使用 file:// 协议加载数据`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
   * - :ref:`load-data/load-data-from-local-files/load-data-using-gpload:使用 gpload 加载数据`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
   * - :ref:`load-data/load-data-from-kafka:从 kafka 加载数据`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`load-data/load-data-from-oss-and-hdfs:从对象存储和 hdfs 加载数据`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`load-data/load-data-from-hive:从 hive 数仓加载数据`
     - ✅
     - ✅
     - ✅
     - 新增支持加载 Iceberg 和 Hudi 表
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - 从 Spark 加载数据
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌
   * - :ref:`load-data/customize-multi-char-delimiters:读写外部表时自定义多字符分隔符`
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
     - ❌
     - ❌

.. [1] 新增支持 Numeric 数据类型。

.. [2] 新增若干算子。

.. [3] 新增支持 SSL。

.. [4] 新增支持 Numeric 数据类型。

.. [5] 新增若干算子。

.. [6] 新增支持索引运算。

.. [7] 新增对 ``TOAST`` 数据类型的支持。
