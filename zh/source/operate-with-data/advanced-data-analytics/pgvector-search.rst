pgvector 向量相似搜索
=====================

pgvector 是一款开源的向量相似搜索插件，支持精确和近似最近邻搜索，以及 L2 距离、内积和余弦距离，详情参见 `pgvector/pgvector: Open-source vector similarity search for Postgres <https://github.com/pgvector/pgvector>`__\ 。HashData Lightning 支持通过 SQL 语句使用 pgvector 来进行数据存储、查询、索引、混合搜索等操作。

本文档介绍如何在 HashData Lightning 中使用 pgvector 插件。

快速开始
--------

创建插件：

.. code:: sql

   CREATE EXTENSION vector;

创建一个三维向量的列：

.. code:: sql

   CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));

插入向量数据：

.. code:: sql

   INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');

通过 L2 距离获取最近邻：

.. code:: sql

   SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;

说明：内积和余弦距离分别使用 ``<#>`` 和 ``<=>`` 表示。

存储数据
--------

创建一张带有向量列的表：

.. code:: sql

   CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));

或者给现有的表添加一个向量列：

.. code:: sql

   ALTER TABLE items ADD COLUMN embedding vector(3);

插入向量：

.. code:: sql

   INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');

插入/更新向量：

.. code:: sql

   INSERT INTO items (id, embedding) VALUES (1, '[1,2,3]'), (2, '[4,5,6]')
       ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding;

删除向量：

.. code:: sql

   DELETE FROM items WHERE id = 1;

查询数据
--------

获取与一个向量的最近邻：

.. code:: sql

   SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;

获取一行的最近邻：

.. code:: sql

   SELECT * FROM items WHERE id != 1 ORDER BY embedding <-> (SELECT embedding FROM items WHERE id = 1) LIMIT 5;

获取在特定距离范围内的行：

.. code:: sql

   SELECT * FROM items WHERE embedding <-> '[3,1,2]' < 5;

获取距离：

.. code:: sql

   SELECT embedding <-> '[3,1,2]' AS distance FROM items;

对于内积，乘以 ``-1``\ （因为 ``<#>`` 返回负内积）。

.. code:: sql

   SELECT (embedding <#> '[3,1,2]') * -1 AS inner_product FROM items;

对于余弦相似度，使用 ``1`` 减去余弦距离。

.. code:: sql

   SELECT 1 - (embedding <=> '[3,1,2]') AS cosine_similarity FROM items;

求向量的平均值：

.. code:: sql

   SELECT AVG(embedding) FROM items;

求一组向量的平均值：

.. code:: sql

   SELECT category_id, AVG(embedding) FROM items GROUP BY category_id;

索引数据
--------

默认情况下，pgvector 执行精确的最近邻搜索，提供很高的召回率。

如果需要更高的召回率，你可以通过添加索引来使用近似最近邻搜索，不过这会降低一些性能。与添加普通的索引不同的是，在添加近似索引后，\ **查询将会得到不同的结果**\ 。

pgvector 支持添加如下索引类型：

-  IVFFlat
-  HNSW（在 ``0.5.`` 中添加）

IVFFlat 索引
~~~~~~~~~~~~

.. topic:: IVFFlat 背景信息

   索引是在大规模数据集上进行高效的向量搜索的一种方法，特别适用于近似最近邻搜索（ANN）。

   IVFFlat 索引的基本原理如下：

      -  分区搜索空间：IVFFlat 索引通过将数据分割成多个“列表”来工作。这些列表是通过对数据集进行聚类（如 K-means 算法）形成的，每个列表代表数据空间中的一个聚类。
      -  降低搜索复杂度：在执行搜索时，不是在整个数据集上进行搜索，而是先确定搜索向量可能属于哪些列表（即哪些聚类），然后只在这些列表中搜索，从而减少计算量。

   IVFFlat 索引有如下应用场景：

      -  大规模数据集：对于包含大量向量的数据集，全量搜索（即检查每一个向量）会非常耗时。IVFFlat 通过聚类和分区方法优化搜索过程。
      -  近似搜索：IVFFlat 是一种近似最近邻搜索方法，适用于需要快速响应时间且可以接受一定程度上的搜索结果不精确的场景。

   要使用 IVFFlat 索引实现良好的召回率，可以参照以下最佳实践：

      -  在表中有一些数据之后创建索引。
      -  选择适当数量的列表。对于不超过 100 万行的表，建议使用行数除以 1000 作为列表数量。对于超过 100 万行的表，建议使用行数的平方根作为列表数量。
      -  在查询时指定适当数量的探测次数（探测次数越高，召回率越高，速度越慢），建议先尝试列表数量的平方根。为每个要使用的距离函数添加索引。

创建索引
^^^^^^^^

下面每种距离度量方法都有其特定的使用场景。选择哪种方法创建索引取决于你希望优化的搜索类型。例如，如果你的应用侧重于找到方向上相似但大小可能不同的向量，那么使用余弦距离创建的索引可能更合适。相反，如果你关注的是向量之间的直线距离，则应选择基于
L2 距离的索引。

其中 ``lists`` 指定分割的列表数量。

L2 距离：

.. code:: sql

   CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

内积：

.. code:: sql

   CREATE INDEX ON items USING ivfflat (embedding vector_ip_ops) WITH (lists = 100);

余弦距离：

.. code:: sql

   CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

.. attention:: HashData Lightning 目前最多支持对 2000 维的向量进行索引。

指定探测次数
^^^^^^^^^^^^

.. attention:: 

   探测次数指的是在执行近似最近邻搜索时，系统检查的“列表”数量。这些列表是数据集根据特定聚类算法（如
   K-means）分割成的子集。增加探测次数意味着系统会检查更多的列表来寻找最近邻，从而提高找到更准确结果的可能性。

   较高的探测次数可以提高搜索的准确度，但同时会增加计算量，导致搜索速度变慢。因此，探测次数是一个需要根据具体应用场景进行权衡的参数。

指定探测次数（默认为 1）：

.. code:: sql

   SET ivfflat.probes = 10;

如果取较大的探测次数值，在性能上会有一定的损失，从而影响速度，但可以获得更高的召回率，并且可以将其设置为列表数量以进行精确最近邻搜索（此时优化器不会使用索引）。

在事务中使用 ``SET LOCAL`` 来为单个查询设置探测次数：

.. code:: sql

   BEGIN;
   SET LOCAL ivfflat.probes = 10;
   SELECT ...
   COMMIT;

查看索引进度
^^^^^^^^^^^^

你可以在索引创建时查看索引进度：

.. code:: sql

   SELECT phase, tuples_done, tuples_total FROM pg_stat_progress_create_index;

进度各阶段包括：

-  ``initializing``\ ：索引创建过程的开始阶段。在此阶段，系统准备所有必要的资源和配置。
-  ``performing k-means``\ ：使用 k-means
   算法将向量数据集分割成多个列表（即聚类）。
-  ``sorting tuples``\ ：对数据（元组）进行排序。根据向量值或者它们属于的列表进行排序，以优化索引结构和提高搜索效率。
-  ``loading tuples``\ ：数据实际被加载到索引结构中，即将元组数据写入索引，确保数据结构符合索引要求。

.. attention:: ``tuples_done`` 和 ``tuples_total`` 仅在加载元组阶段填充。

使用过滤条件
^^^^^^^^^^^^

创建 IVFFlat 索引时，你可以使用 ``WHERE``
子句来限定索引的范围。这种方法允许在进行向量搜索时，仅考虑符合特定条件的数据行，从而提高搜索的效率和准确性。

对带有 ``WHERE`` 子句的最近邻查询进行索引：

.. code:: sql

   SELECT * FROM items WHERE category_id = 123 ORDER BY embedding <-> '[3,1,2]' LIMIT 5;

对于精确搜索，对一个或多个 ``WHERE`` 列创建索引：

.. code:: sql

   CREATE INDEX ON items (category_id);

对向量列进行部分索引以进行近似搜索：

.. code:: sql

   CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 100)
       WHERE (category_id = 123);

对于多个不同 ``WHERE`` 列的近似搜索，可以使用分区。

.. code:: sql

   CREATE TABLE items (embedding vector(3), category_id int) PARTITION BY LIST(category_id);

HNSW 索引
~~~~~~~~~

.. topic:: HNSW 背景信息

   HNSW（Hierarchical Navigable Small World）索引是一种高效的近似最近邻搜索算法，用于处理大规模和高维数据集。

   HNSW 索引的基本原理如下

      -  多层级图结构：HNSW 索引通过构建一个多层级的图来组织数据。在这个图中，每个节点代表一个数据点（或向量），而节点之间的边表示这些点在空间中的相对邻近性。
      -  搜索优化：这种多层级结构允许在搜索时快速跳过大量不相关的数据点，从而快速定位到查询向量的近邻区域。这大大提高了查询的效率。

   HNSW 索引的应用场景如下：

      -  高维数据：对于高维度的数据集，HNSW 索引特别有效，因为它在处理高维空间中的复杂邻近关系时性能出色。
      -  大规模数据集：HNSW 适用于大数据量，因为它的查询性能（速度和召回率的平衡）优于许多其他类型的索引。

创建 HNSW 索引的时间较长，占用内存较多，但在查询性能（速度-召回权衡）方面性能更好。与 IVFFlat 不同，HNSW 索引没有像 IVFFlat 那样的训练步骤，因此可以在表中没有任何数据的情况下创建索引。

为要使用的每个距离函数添加索引。

.. _创建索引-1:

创建索引
^^^^^^^^

下面每种距离度量方法都有其特定的使用场景。选择哪种方法创建索引取决于你希望优化的搜索类型。例如，如果你的应用侧重于找到方向上相似但大小可能不同的向量，那么使用余弦距离创建的索引可能更合适。相反，如果你关注的是向量之间的直线距离，则应选择基于 L2 距离的索引。

L2 距离：

.. code:: sql

   CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);

内积：

.. code:: sql

   CREATE INDEX ON items USING hnsw (embedding vector_ip_ops);

余弦距离：

.. code:: sql

   CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);

可索引向量的最大维数为 2000。

索引选项
^^^^^^^^

-  ``m`` ：每层的最大连接数（默认为 16）。
-  ``ef_construction`` ：用于构建图的动态候选列表的大小（默认为 64）。

.. code:: sql

   CREATE INDEX ON items USING hnsw (embedding vector_l2_ops) WITH (m = 16, ef_construction = 64);

较大的 ``ef_construction`` 值提供更高的召回率，但以索引建立时间/插入速度为代价。

查询选项
^^^^^^^^

指定搜索的动态候选列表的大小（默认为 40）。较大的值提供更好的召回，但以速度为代价。

.. code:: sql

   SET hnsw.ef_search = 100;

在事务中使用 ``SET LOCAL`` 将其设置为单个查询

.. code:: sql

   BEGIN;
   SET LOCAL hnsw.ef_search = 100;
   SELECT ...
   COMMIT;

.. _查看索引进度-1:

查看索引进度
^^^^^^^^^^^^

你可以在创建 HNSW 索引时查看进度：

.. code:: sql

   SELECT phase, round(100.0 * blocks_done / nullif(blocks_total, 0), 1) AS "%" FROM pg_stat_progress_create_index;

HNSW 索引建立包括以下阶段：

-  ``initializing``\ ：索引创建过程的开始阶段。在此阶段，系统准备所有必要的资源和配置，以便开始构建索引。
-  ``loading tuples``\ ：数据点（或向量）被添加到多层级图中，并建立相应的连接。

.. _使用过滤条件-1:

使用过滤条件
^^^^^^^^^^^^

创建 HNSW 索引时，你可以使用 ``WHERE`` 子句来限定索引的范围。这种方法允许在进行向量搜索时，仅考虑符合特定条件的数据行，从而提高搜索的效率和准确性。

.. code:: sql

   SELECT * FROM items WHERE category_id = 123 ORDER BY embedding <- '[3,1,2]' LIMIT 5;

为确切搜索在一个或多个 ``WHERE`` 列上创建索引：

.. code:: sql

   CREATE INDEX ON items (category_id);

在向量列上为近似搜索创建部分索引：

.. code:: sql

   CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 100)WHERE (category_id = 123);

对于多个 ``WHERE`` 列的不同值进行近似搜索，使用分区：

.. code:: sql

   CREATE TABLE items (embedding vector(3), category_id int) PARTITION BY LIST(category_id);

混合搜索
--------

与 HashData Lightning 全文搜索一起使用进行混合搜索：

.. code:: sql

   SELECT id, content FROM items, plainto_tsquery('hello search') query
       WHERE textsearch @@ query ORDER BY ts_rank_cd(textsearch, query) DESC LIMIT 5;

性能
----

使用 ``EXPLAIN ANALYZE`` 进行性能调试：

.. code:: sql

   EXPLAIN ANALYZE SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;

精确搜索
~~~~~~~~

如果想要加快没有索引的查询速度，你可以调大参数 ``max_parallel_workers_per_gather`` 的值。

.. code:: sql

   SET max_parallel_workers_per_gather = 4;

如果向量已经归一化为长度为 1（例如 `OpenAI 的嵌入向量 <https://platform.openai.com/docs/guides/embeddings/which-distance-function-should-i-use>`__\ ），使用内积可以获得最佳性能。

.. code:: sql

   SELECT * FROM items ORDER BY embedding <#> '[3,1,2]' LIMIT 5;

近似搜索
~~~~~~~~

如果要加快带有索引的查询速度，你可以增加反向列表的数量（牺牲一定的召回率）。

.. code:: sql

   CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 1000);

这些是关于在 pgvector 中进行最近邻搜索和性能优化的一些指南。根据需要和数据结构，你可以根据这些指南进行调整和优化。
