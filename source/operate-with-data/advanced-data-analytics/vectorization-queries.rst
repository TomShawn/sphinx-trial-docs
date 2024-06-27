Vectorization 向量化查询计算
============================

当需要处理大规模数据集时，向量化 (vectorization) 执行引擎可以显著提高计算效率。通过将数据向量化，可以同时处理多个数据元素，利用并行计算和 SIMD 指令集加速计算过程。HashData Lightning Vectorization（简称 Vectorization）是基于 HashData Lightning 内核的一个向量化插件，用于优化查询语句的性能。

安装与卸载
----------

安装步骤
~~~~~~~~

1. 在安装 HashData Lightning Vectorization 之前，需要先\ `安装部署 HashData Lightning <https://hashdata.feishu.cn/wiki/OCDVwwBAjiattUkXVQKcoeHqnBh>`__\ ，确保版本在 v1.4.0 或以上。

2. 加载 Vectorization。使用 ``gpconfig`` 启用 HashData Lightning 的 ``vectorization.so``\ 。

   .. code:: bash

      # 下面的路径为 vectorization.so 所在路径
      gpconfig -c session_preload_libraries -v '/usr/local/cloudberry-db/lib/postgresql/vectorization.so'

3. 连接到目标数据库。将 ``your_database_name`` 替换为实际的数据库名。

   .. code:: shell

      $ psql your_database_name;

4. 在数据库中安装 Vectorization。

   .. code:: sql

      your_database_name=# CREATE extension vectorization;

.. attention:: Vectorization 安装后向量化开关即已打开，退出数据库重新连接不需要重新安装。

卸载步骤
~~~~~~~~

在数据库上卸载 Vectorization 后，Vectorization 将会被禁用，重新连接数据库时，Vectorization 是关闭状态。

.. code:: sql

   your_database_name=# DROP EXTENSION vectorization;

使用说明
--------

Vectorization 向用户提供两个参数：\ ``vector.enable_vectorization`` 和 ``vector.max_batch_size``\ 。

.. list-table::
   :header-rows: 1
   :align: left
   :widths: 12 15

   * - **参数名称**
     - **说明**
   * - ``vector.enable_vectorization``
     - 用于控制是否开启向量化查询。默认为开启状态。
   * - ``vector.max_batch_size``
     - 向量化 batch 大小，用于控制执行器单次循环处理数据的行数，范围为 [0, 600000]，默认值 16384。


开启或关闭向量化查询
~~~~~~~~~~~~~~~~~~~~

可以通过设置 ``vector.enable_vectorization`` 变量在连接中暂时关闭和打开 Vectorization 功能，设置对单次连接有效，退出连接后设置会恢复为默认值。

卸载 Vectorization 后设置 ``vector.enable_vectorization`` 的变量不会生效，重新安装后会恢复 ``vector.enable_vectorizatio`` 为默认值 ``on``\ 。

.. code:: sql

   SET vector.enable_vectorization TO [on|off];

设置向量化 batch 大小
~~~~~~~~~~~~~~~~~~~~~

Vectorization 的 batch 大小会显著影响性能，过小的值会导致查询变慢，过大的值会导致内存占用过高却可能无法提升性能。

.. code:: sql

   SET vector.max_batch_size TO <batch_number>;

验证查询是否为向量化
~~~~~~~~~~~~~~~~~~~~

可以通过 ``explain`` 来验证查询是否为 Vectorization 查询。

-  如果 QUERY PLAN 首行有 Vec 标记，表明使用了 Vectorization 查询。

   .. code:: sql

      gpadmin=# EXPLAIN SELECT * FROM int8_tbl;
                                          QUERY PLAN                                     
      -----------------------------------------------------------------------------------
      Vec Gather Motion 3:1  (slice1; segments: 3)  (cost=0.00..431.00 rows=1 width=16)
      ->  Vec Seq Scan on int8_tbl  (cost=0.00..431.00 rows=1 width=16)
      Optimizer: Pivotal Optimizer (GPORCA)
      (3 rows)

-  如果 QUERY PLAN 首行没有 Vec 标记，表明未使用 Vectorization 查询。

   .. code:: sql

      gpadmin=# EXPLAIN SELECT * FROM int8_tbl;
                                      QUERY PLAN                                   
      -------------------------------------------------------------------------------
      Gather Motion 3:1  (slice1; segments: 3)  (cost=0.00..431.00 rows=1 width=16)
      ->  Seq Scan on int8_tbl  (cost=0.00..431.00 rows=1 width=16)
      Optimizer: Pivotal Optimizer (GPORCA)
      (3 rows)

Vectorization 支持的特性
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: 特性支持情况
   :header-rows: 1
   :align: left
   :widths: 9 7 18

   * - 特性
     - 是否支持
     - 描述
   * - **存储格式**
     - 支持
     - AOCS
   * - **存储格式**
     - 不支持
     - HEAP
   * - **数据类型**
     - 支持
     - int2、int4、int8、float8、bool、char、tid、date、time、timestamp、timestamptz、varchar、text、numeric（v1.5.3 新增）
   * - **数据类型**
     - 不支持
     - custom type
   * - **Scan 算子**
     - 支持
     - AOCS 表的扫描、复杂过滤条件
   * - **Scan 算子**
     - 不支持
     - 非 AOCS 表
   * - **Agg 算子**
     - 支持
     - 聚合函数：min，max，count，sum，avg
       聚合策略：PlanAggregate 朴素聚集，GroupAggregate 排序聚合，HashAggregate 哈希聚合
   * - **Agg 算子**
     - 不支持
     - 聚合函数：sum(int8)，sum(float8)，stddev 标准差，variance 方差
       聚合策略：MixedAggregate 混合聚合
   * - **Limit 算子**
     - 支持
     - 全部
   * - **ForeignScan 算子**
     - 支持
     - 全部
   * - **Result 算子**
     - 支持
     - 全部
   * - **Append 算子**
     - 支持
     - 全部
   * - **Subquery 算子**
     - 支持
     - 全部
   * - **Sequence 算子**
     - 支持
     - 全部
   * - **NestedLoopJoin 算子**
     - 支持
     - 连接类型：inner join，left join，semi join，anti join
   * - **NestedLoopJoin 算子**
     - 不支持
     - 连接类型：right join、full join，semi-anti join
       连接条件：不同数据类型，复杂的不等条件
   * - **Material 算子**
     - 支持
     - 全部
   * - **ShareInputScan 算子**
     - 支持
     - 全部
   * - **ForeignScan 算子**
     - 支持
     - 全部
   * - **HashJoin 算子**
     - 支持
     - 连接类型：inner join，left join，right join，full join，semi join，anti join，semi-anti join
   * - **HashJoin 算子**
     - 不支持
     - 连接条件：不同数据类型，复杂的不等条件
   * - **Sort 算子**
     - 支持
     - 排序顺序：递增、递减算法：order by，order by limit
   * - **Motion 算子**
     - 支持
     - GATHER（将元组从多个发送器发送到一个接收器），GATHER_SINGLE（单节点聚集），HASH（简单的 hash 条件），BROADCAST（广播聚集），EXPLICIT（显式聚集）
   * - **Motion 算子**
     - 不支持
     - Hash 聚集（复杂的 Hash 条件）
   * - **表达式**
     - 支持
     - case when、is distinct、is not distinct、grouping、groupid、stddev_sample、abs、round、upper、textcat、date_pli、coalesce、substr
   * - **Bench**
     - 支持
     - ClickHouse，TPC-H，TPC-DS，ICW，ICW-ORCA

性能测评
--------

TPC-H
~~~~~

TPC-H 总共有 22 个查询 SQL 语句，相比于非向量化执行，向量化整体提速 2 倍 +。对于纯聚合的 SQL 语句，向量化相比于非向量化可以提速 3 倍 +。

TPC-DS
~~~~~~

TPC-DS 共有 99 个查询 SQL 语句，环境为 1T 数据。相比于非向量化执行，向量化整体提速 2 倍 +。

.. list-table:: 向量化查询性能对比
   :header-rows: 1
   :align: left

   * - 语句
     - 未使用向量化的查询时间 (s)
     - 使用向量化的查询时间 (s)
     - 时间差 (s) = 非向量化 - 向量化
     - 提升（倍）
   * - 1
     - 18
     - 54
     - 36
     - 3
   * - 2
     - 3
     - 9
     - 6
     - 3
   * - 3
     - 14
     - 23
     - 9
     - 1.64
   * - 4
     - 22
     - 44
     - 22
     - 2
   * - 5
     - 11
     - 28
     - 17
     - 2.54
   * - 6
     - 7
     - 10
     - 3
     - 1.43
   * - 7
     - 13
     - 22
     - 9
     - 1.69
   * - 8
     - 11
     - 28
     - 17
     - 2.55
   * - 9
     - 21
     - 62
     - 41
     - 2.95
   * - 10
     - 12
     - 22
     - 10
     - 1.83
   * - 11
     - 5
     - 5
     - 0
     - -
   * - 12
     - 11
     - 15
     - 4
     - 1.36
   * - 13
     - 13
     - 28
     - 15
     - 2.15
   * - 14
     - 7
     - 10
     - 3
     - 1.43
   * - 15
     - 7
     - 12
     - 5
     - 1.71
   * - 16
     - 4
     - 7
     - 3
     - 1.75
   * - 17
     - 20
     - 92
     - 72
     - 4.6
   * - 18
     - 20
     - 79
     - 59
     - 3.95
   * - 19
     - 13
     - 13
     - 0
     - -
   * - 20
     - 13
     - 23
     - 10
     - 1.77
   * - 21
     - 61
     - 72
     - 11
     - 1.15
   * - 22
     - 18
     - 18
     - 0
     - -
   * - 总计
     - 324
     - 676
     - 352
     - 2.086419753

.. list-table:: 向量化查询性能对比
   :header-rows: 1
   :align: left

   * - 语句
     - 未使用向量化的查询时间 (s)
     - 使用向量化的查询时间 (s)
     - 时间差 (s) = 非向量化 - 向量化
     - 提升（倍）
   * - 1
     - 5
     - 2
     - 3
     - 2.50
   * - 2
     - 10
     - 4
     - 6
     - 2.50
   * - 3
     - 5
     - 2
     - 3
     - 2.50
   * - 4
     - 41
     - 19
     - 22
     - 2.16
   * - 5
     - 11
     - 11
     - 0
     - 1.00
   * - 6
     - 10
     - 4
     - 6
     - 2.50
   * - 7
     - 12
     - 4
     - 8
     - 3.00
   * - 8
     - 13
     - 8
     - 5
     - 1.63
   * - 9
     - 11
     - 7
     - 4
     - 1.57
   * - 10
     - 12
     - 5
     - 7
     - 2.40
   * - 11
     - 30
     - 14
     - 16
     - 2.14
   * - 12
     - 3
     - 2
     - 1
     - 1.50
   * - 13
     - 10
     - 6
     - 4
     - 1.67
   * - 14
     - 46
     - 37
     - 9
     - 1.24
   * - 15
     - 10
     - 2
     - 8
     - 5.00
   * - 16
     - 13
     - 7
     - 6
     - 1.86
   * - 17
     - 13
     - 5
     - 8
     - 2.60
   * - 18
     - 15
     - 5
     - 10
     - 3.00
   * - 19
     - 12
     - 4
     - 8
     - 3.00
   * - 20
     - 3
     - 2
     - 1
     - 1.50
   * - 21
     - 6
     - 1
     - 5
     - 6.00
   * - 22
     - 14
     - 5
     - 9
     - 2.80
   * - 23
     - 125
     - 43
     - 82
     - 2.91
   * - 24
     - 147
     - 60
     - 87
     - 2.45
   * - 25
     - 13
     - 4
     - 9
     - 3.25
   * - 26
     - 7
     - 2
     - 5
     - 3.50
   * - 27
     - 11
     - 5
     - 6
     - 2.20
   * - 28
     - 7
     - 6
     - 1
     - 1.17
   * - 29
     - 12
     - 4
     - 8
     - 3.00
   * - 30
     - 11
     - 3
     - 8
     - 3.67
   * - 31
     - 13
     - 6
     - 7
     - 2.17
   * - 32
     - 7
     - 2
     - 5
     - 3.50
   * - 33
     - 10
     - 5
     - 5
     - 2.00
   * - 34
     - 11
     - 4
     - 7
     - 2.75
   * - 35
     - 16
     - 5
     - 11
     - 3.20
   * - 36
     - 10
     - 4
     - 6
     - 2.50
   * - 37
     - 6
     - 3
     - 3
     - 2.00
   * - 38
     - 23
     - 7
     - 16
     - 3.29
   * - 39
     - 25
     - 22
     - 3
     - 1.14
   * - 40
     - 5
     - 2
     - 3
     - 2.50
   * - 41
     - 1
     - 1
     - 0
     - 1.00
   * - 42
     - 5
     - 2
     - 3
     - 2.50
   * - 43
     - 7
     - 3
     - 4
     - 2.33
   * - 44
     - 4
     - 4
     - 0
     - 1.00
   * - 45
     - 12
     - 3
     - 9
     - 4.00
   * - 46
     - 17
     - 6
     - 11
     - 2.83
   * - 47
     - 13
     - 7
     - 6
     - 1.86
   * - 48
     - 8
     - 5
     - 3
     - 1.60
   * - 49
     - 7
     - 6
     - 1
     - 1.17
   * - 50
     - 11
     - 3
     - 8
     - 3.67
   * - 51
     - 11
     - 18
     - -7
     - 0.61
   * - 52
     - 6
     - 2
     - 4
     - 3.00
   * - 53
     - 7
     - 3
     - 4
     - 2.33
   * - 54
     - 20
     - 16
     - 4
     - 1.25
   * - 55
     - 6
     - 2
     - 4
     - 3.00
   * - 56
     - 9
     - 7
     - 2
     - 1.29
   * - 57
     - 8
     - 4
     - 4
     - 2.00
   * - 58
     - 7
     - 4
     - 3
     - 1.75
   * - 59
     - 19
     - 9
     - 10
     - 2.11
   * - 60
     - 9
     - 6
     - 3
     - 1.50
   * - 61
     - 13
     - 5
     - 8
     - 2.60
   * - 62
     - 4
     - 2
     - 2
     - 2.00
   * - 63
     - 7
     - 3
     - 4
     - 2.33
   * - 64
     - 28
     - 13
     - 15
     - 2.15
   * - 65
     - 18
     - 7
     - 11
     - 2.57
   * - 66
     - 5
     - 3
     - 2
     - 1.67
   * - 67
     - 489
     - 205
     - 284
     - 2.39
   * - 68
     - 16
     - 8
     - 8
     - 2.00
   * - 69
     - 10
     - 4
     - 6
     - 2.50
   * - 70
     - 17
     - 16
     - 1
     - 1.06
   * - 71
     - 9
     - 4
     - 5
     - 2.25
   * - 72
     - 80
     - 47
     - 33
     - 1.70
   * - 73
     - 11
     - 4
     - 7
     - 2.75
   * - 74
     - 25
     - 9
     - 16
     - 2.78
   * - 75
     - 20
     - 13
     - 7
     - 1.54
   * - 76
     - 4
     - 4
     - 0
     - 1.00
   * - 77
     - 9
     - 5
     - 4
     - 1.80
   * - 78
     - 29
     - 12
     - 17
     - 2.42
   * - 79
     - 16
     - 6
     - 10
     - 2.67
   * - 80
     - 11
     - 7
     - 4
     - 1.57
   * - 81
     - 10
     - 3
     - 7
     - 3.33
   * - 82
     - 10
     - 4
     - 6
     - 2.50
   * - 83
     - 3
     - 3
     - 0
     - 1.00
   * - 84
     - 8
     - 2
     - 6
     - 4.00
   * - 85
     - 6
     - 3
     - 3
     - 2.00
   * - 86
     - 4
     - 2
     - 2
     - 2.00
   * - 87
     - 24
     - 7
     - 17
     - 3.43
   * - 88
     - 21
     - 8
     - 13
     - 2.63
   * - 89
     - 7
     - 4
     - 3
     - 1.75
   * - 90
     - 4
     - 1
     - 3
     - 4.00
   * - 91
     - 6
     - 2
     - 4
     - 3.00
   * - 92
     - 6
     - 1
     - 5
     - 6.00
   * - 93
     - 11
     - 3
     - 8
     - 3.67
   * - 94
     - 8
     - 5
     - 3
     - 1.60
   * - 95
     - 66
     - 24
     - 42
     - 2.75
   * - 96
     - 7
     - 2
     - 5
     - 3.50
   * - 97
     - 14
     - 5
     - 9
     - 2.80
   * - 98
     - 6
     - 3
     - 3
     - 2.00
   * - 99
     - 7
     - 3
     - 4
     - 2.33
   * - 总计
     - 000
     - 916
     - /
     - 2.18
