.. raw:: latex

   \newpage

使用 RoaringBitMap 位图运算
============================

HashData Lightning 支持 RoaringBitMap，这是一种高效的 Bitmap（位图）压缩算法，其在各种编程语言和大数据平台中已获广泛应用。通过整合 RoaringBitmap 功能，HashData Lightning 提供了一种原生的数据库数据类型，支持丰富的数据库函数和聚合操作。

RoaringBitmap 优于传统的压缩 Bitmap，如 WAH、EWAH 或 Concise，尤其在性能方面表现突出。在某些情况下，RoaringBitmap 的处理速度可以比传统压缩方法快数百倍，同时提供更优的压缩效率，甚至在某些应用场景中，其性能还能超越未压缩的 Bitmap。这种位计算的高效性特别适合进行大数据基数计算，常用于数据去重、标签筛选和时间序列等复杂计算。

.. topic:: Bitmap 简介

   Bitmap（位图）是一种数据结构，用于高效地存储和操作由 0 和 1 组成的二进制数据。它主要用于快速查找、高效存储以及对大量布尔数据（如“是”或“否”）的集合进行操作。在 Bitmap 中，每个元素仅占用一个二进制位，因此可以极大地节省存储空间，同时实现快速的数据处理。

   Bitmap 的常见应用包括成员检测、去重、统计计算、数据过滤和筛选。

编译安装（仅面向内部技术支持人员）
----------------------------------

.. code:: shell

   git clone git@code.hashdata.xyz:cloudberry/plugins/gpdb-roaringbitmap.git

   cd gpdb-roaringbitmap
   make install

使用方法
--------

加载插件
~~~~~~~~

在使用 RoaringBitMap 前，你需要先加载 ``roaringbitmap`` 插件。请确保该插件文件已同步到所有节点对应的目录下。

.. code:: sql

   CREATE EXTENSION roaringbitmap;

创建表
~~~~~~

你可以在建表语句 ``CREATE TABLE`` 中指定 ``roaringbitmap`` 类型的字段。

以下表 ``t1`` 包含了一个名为 ``bitmap`` 的字段，其数据类型为 ``roaringbitmap``\ 。该字段专门用于存储和操作 ``RoaringBitmap`` 类型的数据。

.. code:: sql

   CREATE TABLE t1 (id integer, bitmap roaringbitmap);

创建一个 Bitmap
~~~~~~~~~~~~~~~

-  使用 ``RB_BUILD`` 函数创建位图：

   .. code:: sql

      INSERT INTO t1 SELECT 1,RB_BUILD(ARRAY[1,2,3,4,5,6,7,8,9,200]);

   以上语句插入一行数据到表 ``t1``\ 。其中，\ ``id`` 字段的值为 ``1``\ ，而 ``bitmap`` 字段则通过 ``RB_BUILD`` 函数生成。\ ``RB_BUILD`` 函数接受一个整数数组作为参数，并构建一个 ``RoaringBitmap`` 对象。在这个例子中，它构建了一个包含数字 1, 2, 3, 4, 5, 6, 7, 8, 9, 和 200 的位图。这意味着在这个位图中，这些具体的位置将被设为 1，表明这些元素存在。

-  使用 ``RB_BUILD_AGG`` 函数将数值聚合为位图：

   .. code:: sql

      INSERT INTO t1 SELECT 2,RB_BUILD_AGG(e) FROM GENERATE_SERIES(1,100) e;

   以上语句使用 PostgreSQL 的 ``GENERATE_SERIES`` 函数生成从 1 到 100 的序列，每个数字作为变量 ``e`` 的值。\ ``RB_BUILD_AGG`` 函数将这些值聚合为一个 ``RoaringBitmap``\ 。这个函数通常用于聚合操作，将多个输入值整合到一个 ``RoaringBitmap`` 中。因此，这里创建的 ``RoaringBitmap`` 包含了 1 到 100 的所有整数。在这条插入语句中，\ ``id`` 字段的值为 ``2``\ 。

Bitmap 并集运算
~~~~~~~~~~~~~~~

.. code:: sql

   SELECT RB_OR(a.bitmap,b.bitmap) FROM (SELECT bitmap FROM t1 WHERE id = 1) AS a,(SELECT bitmap FROM t1 WHERE id = 2) AS b;

以上 ``SELECT`` 语句使用了 ``RB_OR`` 函数来执行两个 ``RoaringBitmap`` 数据的逻辑 "OR" 操作，即并集操作。

这条语句合并两个特定 ``RoaringBitmap`` 数据集的内容，使得得到的新 ``RoaringBitmap`` 包含原来两个数据集中的所有元素。这在处理大数据集时特别有用，例如合并两个不同时间段或条件下的用户行为数据，以便进行综合分析。

Bitmap 并集交集聚合运算
~~~~~~~~~~~~~~~~~~~~~~~

-  使用 ``RB_OR_AGG`` 进行并集聚合运算：

   .. code:: sql

      SELECT RB_OR_AGG(bitmap) FROM t1;

   以上语句使用 ``RB_OR_AGG`` 函数对表 ``t1`` 中所有行的 ``bitmap`` 列进行逻辑 "OR" 聚合操作，也就是并集操作。这意味着它会遍历表中每一行的 ``bitmap`` 数据，并将所有的 ``bitmap`` 合并成一个，其中任何一行有标记为 1 的位在结果 ``bitmap`` 中也会被标记为 1。这适用于合并多个数据集的情况，以获取所有数据集中任意出现的元素。

-  使用 ``RB_AND_AGG`` 进行交集聚合运算：

   .. code:: sql

      SELECT RB_AND_AGG(bitmap) FROM t1;

   ``RB_AND_AGG`` 函数对表 ``t1`` 中的 ``bitmap`` 数据执行逻辑 "AND" 聚合操作，即交集操作。这个函数只有在所有 ``bitmap`` 中相应的位都为 1 时，结果 ``bitmap`` 中的对应位才会被设置为 1。这种操作通常用于找出所有数据集中共同的元素。

-  使用 ``RB_XOR_AGG`` 进行对称差集聚合运算：

   .. code:: sql

      SELECT RB_XOR_AGG(bitmap) FROM t1;

   ``RB_XOR_AGG`` 函数执行逻辑 "XOR" 聚合操作，也就是对称差集。这个操作会比较所有 ``bitmap``\ ，并在结果 ``bitmap`` 中设置那些在奇数数量的 ``bitmap`` 中出现的位。这意味着如果一个位在奇数个 ``bitmap`` 中为 1，它在结果中也为 1；如果在偶数个 ``bitmap`` 中为 1，结果中则为 0。这有助于识别那些只在部分数据集中出现的特殊元素。

-  使用 ``RB_BUILD_AGG`` 函数进行聚合运算：

   .. code:: sql

      SELECT RB_BUILD_AGG(e) FROM GENERATE_SERIES(1,100) e;

   以上语句使用 ``RB_BUILD_AGG`` 函数对从 ``GENERATE_SERIES(1,100)`` 生成的连续整数进行聚合，创建一个包含这些整数的 ``RoaringBitmap``\ 。此函数通常用于从一系列单独的元素中创建一个紧凑的 ``RoaringBitmap``\ ，这在处理连续数据或者需要高效压缩的场合非常有用。

统计基数
~~~~~~~~

.. code:: sql

   SELECT RB_CARDINALITY(bitmap) FROM t1;

以上语句使用了 ``RB_CARDINALITY`` 函数，其目的是计算表 ``t1`` 中每一行的 ``bitmap`` 字段中的基数，也就是该 ``RoaringBitmap`` 中设置为 1 的位的数量。基数 (Cardinality) 指的是一个集合中独特元素的数量。在 ``RoaringBitmap`` 的上下文中，这意味着计算该位图中代表的集合中有多少个不同的整数。例如，如果一个 ``RoaringBitmap`` 包含数字 1, 2, 3, 和 5，则其基数为 4。

将 Bitmap 转化为 SETOF integer 整数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  使用 ``RB_ITERATE`` 函数进行转化：

   .. code:: sql

      SELECT RB_ITERATE(bitmap) FROM t1 WHERE id = 1;

   ``RB_ITERATE`` 函数通常用于迭代 ``RoaringBitmap`` 中所有设置为 1 的位，并返回它们代表的值。在以上查询中，该函数会对 ``id`` 为 1 的 ``bitmap`` 字段中的所有元素进行迭代，返回包含所有这些元素的结果集。这样可以方便地查看或处理这个位图中所有的元素。

-  使用 ``RB_ITERATE_DECREMENT`` 函数进行转化：

   .. code:: sql

      SELECT RB_ITERATE_DECREMENT(bitmap) FROM t1 WHERE id = 1;

   ``RB_ITERATE_DECREMENT`` 函数的作用类似于 ``RB_ITERATE``\ ，但它在迭代时以降序返回位图中的元素。这意味着如果位图中包含的元素是 1, 2, 3, 4，该函数将返回 4, 3, 2, 1。这对于需要按照从高到低的顺序处理或检查位图中的元素时非常有用。

bytea 和 roaringbitmap 数据类型之间转换
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  将 ``roaringbitmap`` 类型转化为 ``bytea`` 类型：

   .. code:: sql

      SELECT RB_BUILD('{1,2,3}')::BYTEA;

   以上语句首先使用 ``RB_BUILD`` 函数创建一个包含整数 1, 2, 和 3 的 ``RoaringBitmap``\ 。随后，通过类型转换操作符 ``::BYTEA``\ ，这个 ``RoaringBitmap`` 对象被转换成 ``bytea`` 类型。\ ``bytea`` 是 PostgreSQL 中用于存储二进制数据的数据类型，这意味着转换后的结果是 ``RoaringBitmap`` 对象的二进制表示。

-  将 ``bytea`` 类型转化为 ``roaringbitmap`` 类型：

   .. code:: sql

      SELECT '\x3a3000000100000000000000100000000100'::ROARINGBITMAP;

   以上语句从一个 ``bytea`` 类型的二进制字符串开始，该字符串通过字面量方式给出（以 ``\x`` 开头表示十六进制的二进制数据）。通过类型转换操作符 ``::ROARINGBITMAP``\ ，这个二进制数据被转换为 ``RoaringBitmap`` 类型。这表示你可以将存储在二进制格式的 ``RoaringBitmap`` 数据重新转换回其对应的位图数据结构。
