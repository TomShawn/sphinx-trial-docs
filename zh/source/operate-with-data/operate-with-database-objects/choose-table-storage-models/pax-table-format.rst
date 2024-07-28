.. raw:: latex

   \newpage

PAX 存储格式
============

HashData Lighting 支持 PAX (Partition Attributes Across) 存储格式。

PAX 是一种数据库存储格式，它结合了行式存储 (NSM，N-ary Storage Model) 和列式存储 (DSM，Decomposition Storage Model) 的优点，旨在提高数据库的查询性能，尤其是在缓存效率方面。在 OLAP 场景下，PAX 拥有媲美行式存储的批量写入性能和列式存储的读取性能。PAX 既能适应云环境下基于对象存储的存储模型，也能适应于线下传统基于物理文件的存储方式。

与传统存储格式相比，PAX 还有以下特性：

-  数据更新和删除：AX 采用标记删除的方式对数据进行删除和更新，这样可以有效地管理存储在物理文件中的数据变更，而无需立即重写整个数据文件。
-  并发控制与读写隔离：PAX 使用多版本并发控制 (MVCC) 技术来实现高效的并发控制和读写隔离，其控制粒度达到单个数据文件级别，增强了操作的安全性和效率。
-  索引支持：支持 B-tree 索引，这有助于加速查询操作，特别是在处理大量数据时可以显著提高数据检索速度。
-  数据编码与压缩：PAX 提供多种数据编码（如 run-length encoding, delta encoding）和压缩方法（如 zstd, zlib），及多种压缩级别，这些特性帮助减少存储空间需求，同时优化读取性能。
-  统计信息：数据文件包含详细的统计信息，这些信息用于快速过滤和查询优化，从而减少不必要的数据扫描，加快查询处理速度。
-  向量化引擎：PAX 还支持向量化引擎，在 v1.5.3 中为实验性特性，旨在进一步提高数据处理能力和查询性能，特别是在数据分析和报表生成等应用场景中。

适用场景
--------

PAX 的混合存储能力使其适合于需要处理大量数据写入和频繁查询的复杂 OLAP 应用。无论是在云基础设施中寻求高性能数据分析解决方案，还是在传统数据中心环境中处理大规模数据集，PAX 都能提供强大支持。

使用方法
--------

创建 PAX 的表
~~~~~~~~~~~~~

要创建 PAX 格式的表，你需要将表的访问方式 (Table Access Method) 设为 PAX，可以参照以下任一方法进行设置：

-  在建表时显式使用 ``USING PAX`` 子句，例如：

   .. code:: sql

      CREATE TABLE t1(a int, b int, c text) USING PAX;
      -- t1 为 PAX 表，可以作为普通 heap 表使用。

-  先设置表的默认访问方式，然后再建表：

   .. code:: sql

      -- 设置表的默认访问方式，此后新建的表都将使用 PAX 格式。
      SET default_table_access_method = pax;

      -- 隐式使用默认表访问方式，即 PAX。
      CREATE TABLE t1(a int, b int, c text);

在建表时，你还可以指定部分列的最小值和最大值信息，以加速查询：

.. code:: sql

   -- 通过 WITH(minmax_columns='b,c') 指定了对
   -- 列 b 和 c 记录最小值和最大值（minmax）统计信息。
   -- 这可以帮助优化那些涉及这两列的查询，
   -- 因为系统可以快速判断哪些数据块可能包含符合条件的数据。
   CREATE TABLE p2(a INT, b INT, c INT) USING pax WITH(minmax_columns='b,c');

   INSERT INTO p2 SELECT i, i * 2, i * 3 FROM generate_series(1,10)i;


  -- 由于 b 列有 minmax 统计信息，
  -- 系统可以快速定位到可能包含该值的数据块，从而加速查询过程。
   SELECT * FROM p2 WHERE b = 4;

  -- 同样，由于 b 列的 minmax 信息，系统能迅速确定没有数据块能满足这个条件
  --（如果所有生成的值都是正的），可能直接返回没有数据的结果，从而避免不必要的数据扫描。
   SELECT * FROM p2 WHERE b < 0;

   -- 修改表 p2 的 minmax 统计信息设置，使其仅适用于列 b。对于之后插入的数据，
   -- 只有 b 列会维护这种统计信息，而对已存在的数据不会产生影响，也不会进行重新写入或调整。
   ALTER TABLE p2 SET(minmax_columns='b');

查看已有表的格式
~~~~~~~~~~~~~~~~

要查看一张表是否为 PAX 格式，可使用下面任一方法：

-  使用 ``psql`` 命令 ``\d+``\ ：

   .. code:: sql

      gpadmin=# \d+ t1
                                                  Table "public.t1"
      Column |  Type   | Collation | Nullable | Default | Storage  | Compression | Stats target | Description
      --------+---------+-----------+----------+---------+----------+-------------+--------------+-------------
      a      | integer |           |          |         | plain    |             |              |
      b      | integer |           |          |         | plain    |             |              |
      c      | text    |           |          |         | extended |             |              |
      Distributed by: (a)
      Access method: pax

-  查询系统目录表 ``pg_class`` 和 ``pg_am``\ ：

   .. code:: sql

      SELECT relname, amname FROM pg_class, pg_am WHERE relam = pg_am.oid AND relname = 't1';

      relname | amname
      ---------+--------
      t1      | pax
      (1 row)

对 TOAST 数据类型的支持
------------------------

PAX 完整地支持了 TOAST（即 The Oversized-Attribute Storage Technique）的 4 种存储方式：

-  ``PLAIN`` 不允许压缩和线外存储。对于不支持 ``TOAST`` 数据类型的列，这是唯一可能的策略。
-  ``EXTENDED`` 允许压缩和线外存储。这是大多数 ``TOAST`` 数据类型的默认设置。首先尝试压缩，如果行仍然太大，则使用线外存储。
-  ``EXTERNAL`` 只允许线外存储，不允许压缩。``EXTERNAL`` 对于宽文本和 ``bytea`` 列的子字符串操作更快（以增加存储空间为代价），因为这些操作经过优化，可以在未压缩的情况下取得部分数据。
-  ``MAIN`` 允许压缩，但不允许线外存储。实际上，Heap 表仍然会对这些列进行线外存储，但只作为没有其他方法使行足够小以适应页面时的最后手段。但 PAX 在这一点上会进行任何线外存储。

与其他存储格式一样，PAX 默认开启 ``TOAST`` 生成，且 PAX 不依赖于 Page 管理数据，这意味着 PAX 可以存储超过 2 MiB 的数据。更多有关 ``TOAST`` 的内容，请参考 `PostgreSQL 文档 - TOAST <https://www.postgresql.org/docs/14/storage-toast.html>`_\ 。

使用限制
--------

-  使用向量化扫描时，可通过 ``ctid`` 进行过滤，但目前不支持 ``porc_vec`` 格式的向量化扫描。
-  在索引支持方面，PAX 存储格式目前仅支持 B-tree (``btree``) 索引。使用 GiST 或 SP-GiST (``gist/spgist``) 索引时会遇到 bug。
-  与传统的 ``heap`` 表不同，PAX 格式不支持 ``TOAST`` 字段。目前，全列数据被保存在同一个数据文件中。
-  PAX 格式暂不支持使用 ``pg_dump`` 或 ``pg_restore`` 进行数据备份和恢复，PAX 表在这些操作中会被忽略。
-  PAX 格式暂不支持写前日志 (WAL)，因此在主服务器 (primary) 与镜像服务器 (mirror) 之间不进行数据备份。

相关 SQL 选项
-------------

PAX 支持若干 SQL 选项，用来控制 PAX 的行为。你可以在 ``WITH()`` 子句中使用这些选项，例如 ``WITH(minmax_columns='b,c', storage_format=porc)``\ 。

.. raw:: latex

    \begingroup
    \renewcommand{\arraystretch}{1.5} % 调整表格行间距
    \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小
  
.. list-table::
   :header-rows: 1
   :align: left
   :widths: 12 7 10 17

   * - 名称
     - 类型
     - 合法值
     - 描述
   * - ``storage_format``
     - string
     - - porc
       - porc_vec
     - 控制内部存储格式。``porc`` 不会保存空值。``porc_vec`` 始终会保存定长字段的空值，不管列值是否为空。默认值是 ``porc``。
   * - ``compresstype``
     - string
     - - none
       - rle
       - delta
       - zstd
       - zlib
     - 列值进行压缩编码的方式，只能选择其中一种。默认值是 ``none``。
   * - ``compresslevel``
     - ``int``
     - 区间 ``[0, 19]``
     - 表示压缩级别，默认值是 0。值小时压缩更快，值大时压缩率更高。只有配合 ``compresstype`` 使用才有效。
   * - ``partition_by``
     - ``string``
     - 表中合法的列名
     - 写入批量数据时，尽可能将数据按指定列分区存放到相同的数据文件中，提高数据聚集的相关性。v1.5.3 只支持整数类型。此分区键与分区表无关，是 PAX 内部组织数据的建议。
   * - ``partition_ranges``
     - ``string``
     - ``FROM(XX) TO(YY) [every(DD)]``
     - 该选项必须与 ``partition_by`` 配合使用，设置分区范围。可以只设置一个范围，也可以将一个大的范围划分成多个不相邻的小范围。尽可能将每个范围内的数据放入同一个数据文件中。不在范围内的数据会放入默认数据文件里。
   * - ``minmax_columns``
     - ``string``
     - 表中以逗号分隔的合法列名
     - 对定义在表中的列记录 ``minmax`` 统计信息，以加快数据查询。列重命名后，列数据不会再记录统计信息。使用 ``ALTER TABLE`` 修改 ``minmax_columns`` 后，只会对未来新写入的数据文件生效，不会影响原来的数据文件。

.. raw:: latex

    \endgroup

以上 ``option`` 的值只会影响到新插入和更新的数据，并不会影响到已经存在的数据。

相关系统参数
------------

以下系统参数 (GUC) 用于设置当前会话中 PAX 表的行为，执行 ``SET <参数>=<值>`` 即可，例如 ``SET pax_enable_filter=true``\ 。

.. raw:: latex

    \begingroup
    \renewcommand{\arraystretch}{1.5} % 调整表格行间距
    \fontsize{7pt}{8pt}\selectfont % 设置表格字体大小

.. list-table::
   :header-rows: 1
   :align: left
   :widths: 12 6 10 17

   * - 参数名
     - 值类型
     - 合法值
     - 描述
   * - ``pax_enable_filter``
     - ``bool``
     - ``true`` 和 ``false``
     - 指定对列数据是否开启基于统计信息的过滤。默认值是 ``true``，表示开启过滤。
   * - ``pax_scan_reuse_buffer_size``
     - ``int``
     - 区间 ``[1MiB, 32MiB]``
     - 扫描时使用的缓冲块大小，默认值是 ``8 MiB``。
   * - ``pax_max_tuples_per_group``
     - ``int``
     - 区间 ``[0x4000, 0x80000]``
     - 指定每个 group 内最多允许有多少条数据。默认值是 ``0x20000``。
   * - ``pax_max_tuples_per_file``
     - ``int``
     - 区间 ``[0x4000, 0xFFFFFF]``
     - 指定每个数据文件里最多允许有多少条数据，其中最大值 ``0xFFFFFF`` 是当前的上限。默认值是 ``0x140000``。
   * - ``pax_max_size_per_file``
     - ``int``
     - 区间 ``[8MiB, 320MiB]``
     - 每个数据文件允许的最大物理容量。这里设置的大小不是硬性要求，实际可能略大于设定的大小。太大或太小的数值都会对性能产生负面影响。默认值是 ``64 MiB``。

.. raw:: latex

    \endgroup

最佳实践
--------

-  使用分区选项：

    -  当数据需要在某一整数列上导入，并且满足以下条件时，推荐使用分区选项：

       -  数据在该列上分布相对均匀，且范围较广，没有极端的聚集情形。
       -  该列常用作查询过滤条件或作为连接 (``join``) 的键。

    -  需要注意的是，PAX 的分区键仅在单次批量导入数据时有效，多次写入的数据之间无法再次调整。分区键的设置仅对未来插入或更新的数据生效，因此在变更分区键后，新导入的数据将按新的分区键处理。

-  使用 ``minmax`` 统计信息：

   -  对于数据分布范围广且常用于查询过滤的列，设置记录该列的 ``minmax`` 值可以显著加速查询过程。
   -  利用 ``minmax`` 统计，如果一个数据文件中所有的列都不满足 ``minmax`` 或空值测试，则可以快速跳过整个文件，避免进行不必要的数据扫描。
   -  重要的注意事项：\ ``minmax`` 的效果依赖于数据的插入方式。如果 PAX 表的数据是通过批量插入（如 ``batch insert`` 或 ``copy``\ ）且每个批次内的数据范围是连续的，则 ``minmax`` 会非常有效。相反，如果数据插入是随机的，\ ``minmax`` 过滤的效果可能会较差。
