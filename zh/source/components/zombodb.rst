.. raw:: latex

   \newpage

使用 ZomboDB 集成 Elastic Search
===================================

ZomboDB 是 HashData Lightning 的一个插件，可以使 HashData Lightning 和 Elasticsearch 协同工作，让 HashData Lightning 拥有 Elasticsearch 丰富的全文检索和文本分析能力。

ZomboDB 实际上是数据表的外部索引，用户通过创建索引的 SQL 语法，即可在已有的 HashData Lightning 表上建立 ZomboDB 的索引。

ZomboDB 可以管理 Elasticsearch 集群上的索引，并且保证事务层面上文本检索的正确性。

ZomboDB 支持大多数 HashData Lightning 的 SQL 语法，例如 ``CREATE INDEX``\ 、\ ``COPY``\ 、\ ``INSERT``\ 、\ ``UPDATE``\ 、\ ``DELETE``\ 、\ ``SELECT``\ 、\ ``ALTER``\ 、\ ``DROP``\ 、\ ``REINDEX``\ 、\ ``(auto)VACUUM``\ 。

工作原理
--------

ZomboDB 连接 HashData Lightning 集群和 Elasticsearch 集群，无论这两个集群是否部署在相同或者不同的主机上，只需保证集群主机之间的网络连接畅通即可。

HashData Lightning 数据表中的一个 ZomboDB 索引 (index)，实际上对应 Elasticsearch 中的一个索引。在大数据量下，为了避免 HashData Lightning 中的每个 segment 都去扫描索引下的全量数据，可以将不同 segment 中的数据分发到索引下的各个分片 (shard) 中，这样能够保证每个 segment 下扫描 ES 数据的效率。

.. image:: /images/zombodb-1.png

创建索引和加载数据流程
~~~~~~~~~~~~~~~~~~~~~~

下图展示了数据表创建 ZomboDB 索引，并加载数据的大致流程。

.. image:: /images/zombodb-2.png

整个过程都是在和 HashData Lightning 集群中的 Coordinator 节点进行通信和交互。

1. 在 HashData Lightning 集群中创建数据表，并且加载相应的数据。
2. 使用 ``CREATE INDEX`` 语法创建 ZomboDB 的索引。此时需要保证 Elasticsearch 的集群处于可用状态，并且网络和 HashData Lightning 集群互通。
3. 创建的过程中，ZomboDB 会自动将表中已有的数据插入到 Elasticsearch 中对应的 index 里面，如果发生了错误，或者手动回滚事务，那么也会自动清理 ES 中的数据。

在索引创建完成后，后续有新的数据插入到表中，都会自动将数据插入到对应 Elasticsearch 的 index 里。

查询数据流程
~~~~~~~~~~~~

下图展示了存在 ZomboDB 索引的情况下，对数据进行查询的大致流程。

.. image:: /images/zombodb-3.png

1. 用户侧使用 ZomboDB 的查询语法，基于 ZomboDB 的索引进行查询。ZomboDB 的查询和普通的 select 基本上没有区别，只是需要使用 ZomboDB 特定的标识符 ``==>``\ 。
2. HashData Lightning 集群中的 Coordinator 节点将查询分发给各个 Segment。
3. 每个 Segment 各自执行查询，只需要查询对应的 Elasticsearch 的 index 中某个 Shard 的数据。
4. 每个 Segment 将查询的结果返回给 Coordinator 节点。
5. Coordinator 节点收到 Segment 的结果，进行聚合或者其他操作，并返回给用户。

安装
----

安装 ZomboDB 有两种方式：使用 gppkg 包或使用 RPM 包。

.. attention:: 

   -  自 HashData Lightning v1.5.0 起，gppkg 包和 RPM 包各提供 HTTPS 和 HTTP 两个版本。即：
       -  gppkg 包（HTTPS 版）
       -  gppkg 包（HTTP 版）
       -  RPM 包（HTTPS 版）
       -  RPM 包（HTTP 版）
   -  如果 ZomboDB 使用的 Elasticsearch 集群配置了 HTTPS，那么安装 ZomboDB 时应选择 HTTPS 版本的安装包。
   -  安装 ZomboDB 时，如果需要使用自定义证书，那么需要声明环境变量 ``SSL_CERT_FILE``\ ，例如 ``export SSL_CERT_FILE=/path/to/your/cert``\ ，否则将会使用系统默认证书。

使用 gppkg 包安装
~~~~~~~~~~~~~~~~~

1. 执行以下命令将 gppkg 包修改为自己的 gppkg 包名即可完成安装。

   .. code:: bash

      # zombodb-1.1-24716-release.gppkg 为 gppkg 包
      gppkg -i zombodb-1.1-24716-release.gppkg

2. 执行以下命令进行验证。

   .. code:: sql

      -- 通过 psql postgres 进入数据库，创建 ZomboDB 扩展
      postgres=# create extension zombodb;

      -- 出现如下结果表示安装成功
      CREATE EXTENSION

使用 RPM 包安装
~~~~~~~~~~~~~~~

1. 执行以下命令安装 ZomboDB。

   .. code:: bash

      # installroot 为 HashData Lightning 安装目录
      # zombodb_centos_pg14-3000.1.5_1.x86_64-24716-release.rpm 为提供的 ZomboDB rpm 包
      yum install zombodb_centos_pg14-3000.1.5_1.x86_64-24716-release.rpm --installroot=/usr/local/cloudberry-db-devel/

2. 执行以下命令进行验证。

   .. code:: sql

      -- 通过 psql postgres 进入数据库，创建 ZomboDB 扩展
      postgres=# create extension zombodb;

      -- 出现如下结果表示安装成功
      CREATE EXTENSION

使用说明
--------

创建和使用索引
~~~~~~~~~~~~~~

创建索引
^^^^^^^^

``CREATE INDEX`` 语法可以为全部或部分字段创建索引。

为全部字段创建索引
''''''''''''''''''

创建 ZomboDB 索引的语法如下。

.. code:: sql

   CREATE INDEX index_name 
          ON table_name 
          USING zombodb ((table_name.*)) 
          WITH (...);

``((table_name.*))`` 表示索引表中全部的字段，即将表中所有的字段都存储到 ES 中，这样对表的任意字段的内容都可以进行检索。

ZomboDB 生成了一个 UUID 作为面向 Elasticsearch 的索引名称，同时为了保证可读性，也为索引名称赋予了别名，别名的命名规范是 ``数据库名称.scheme 名称.表名称.索引名称-索引的 OID``\ ，可以通过 zdb.index_stats 表进行查询，这个表存储了 ZomboDB 索引的相关统计信息。

.. code:: sql

   demo=# select * from zdb.index_stats where pg_index_name = 'idxproducts'::regclass;
                    alias                  |     es_index_name      |          url           | table_name | pg_index_name | es_docs | es_size | es_size_bytes | pg_docs_estimate | pg_size | pg_size_bytes | shards | replicas | doc_count | aborted_xids
   ----------------------------------------+------------------------+------------------------+------------+---------------+---------+---------+---------------+------------------+---------+---------------+--------+----------+-----------+--------------
    demo.public.products.idxproducts-17840 | 17096.2200.17098.17840 | http://localhost:9200/ | products   | idxproducts   | 5       | 20 kB   |         20264 |                0 | 512 kB  |        524288 | 5      | 0        | 5         |            0
   (1 row)

为部分字段创建索引
''''''''''''''''''

仍然以创建索引小节中提到的 products 表为示例，来展示如何为部分字段添加索引。products 表定义如下。

.. code:: sql

   CREATE TABLE products (
     id SERIAL8 NOT NULL PRIMARY KEY,
     name text NOT NULL,
     keywords varchar(64)[],
     short_summary text,
     long_description text,
     price bigint,
     inventory_count integer,
     discontinued boolean default false,
     availability_date date
   ) DISTRIBUTED BY (id);

如果想要为一个表的部分字段添加索引，可以创建一个自定义的方法，并且使用 ``ROW()`` 组合返回一个自定义的类型，类型中可以添加需要索引的字段。

需要注意的是自定义方法只能有一个参数，并且参数类型是需要索引的表类型。

下面以 products 表为例，来展示如何索引部分字段。

1. 创建自定义类型。

   .. code:: sql

      -- 这里创建了一个自定义的类型，其中有三个字段，表示最终存储到 ES 的字段信息
      CREATE TYPE products_idx_type AS (
          id bigint, 
          name varchar, 
          description text
      );

2. 创建自定义方法。

   .. code:: none

      CREATE FUNCTION products_idx_func(products) RETURNS products_idx_type IMMUTABLE STRICT LANGUAGE sql AS $$
      SELECT ROW (
              $1.id,
              $1.name,
              COALESCE($1.short_summary, '') || ' ' || COALESCE($1.long_description, '')
              )::products_idx_type;
      $$;

   此方法的参数是 products 表，方法行为也很简单，即通过 ROW 将 products 表中的字段映射为自定义类型 ``products_idx_type``\ 。

   这里我们将 products 表的两个字段 ``short_summary`` 和 ``long_description`` 组合成了自定义类型中的 description 字段，也可以按照此方法组合任意想要索引的字段。

3. 创建索引。

   .. code:: sql

      CREATE INDEX idxproducts ON products USING zombodb ((products_idx_func(products.*))) with (url='http://localhost:9200/');

   需要注意这里和索引全部字段的区别，我们使用了自定义方法进行创建。

4. 进行查询。

   .. code:: none

      demo=# select * from products where products_idx_func(products) ==> 'box';
      id | name |               keywords               |         short_summary          |                                  long_description                                   | price | inventory_count | discontinued | availability_date
      ----+------+--------------------------------------+--------------------------------+-------------------------------------------------------------------------------------+-------+-----------------+--------------+-------------------
      4 | Box  | {wooden,box,"negative space",square} | Just an empty box made of wood | A wooden container that will eventually rot away.  Put stuff it in (but not a cat). | 17000 |               0 | t            | 2015-07-01
      (1 row)

修改索引
^^^^^^^^

ZomboDB 索引支持原生的 ``ALTER INDEX`` 语法对其属性进行修改，比如可以将索引配置项指定为一个新值，或者重置为默认值。示例如下。

.. code:: sql

   alter index idxproducts set (batch_size=50000);

删除索引
^^^^^^^^

当删除任何有关包含 ZomboDB 索引的对象时，例如显式删除 index，删除表、Scheme、数据库时，都会将对应的 Elasticsearch 中的 index 删除掉。

需要注意的是，如果是删除数据库（DROP Database）的话，则不会删除对应的 ES 索引，因为我们目前没办法在 ZomboDB 中获取到删除数据库的通知。

DROP 语法是事务安全的，也就是说会在事务提交的时候将对应的 Elasticsearch index 删除。

语法选项
^^^^^^^^

下面提到的所有选项都可以在创建索引的时候进行指定，也可以通过 ``ALTER INDEX`` 语法进行修改或重置。

必填选项
''''''''

-  ``url``

   url 表示 Elasticsearch 集群的地址，这个选项是必须指定的，但是如果在配置文件 ``postgresql.conf`` 中指定了 ``zdb.default_elasticsearch_url``\ ，则会使用这个指定的值，创建索引的时候就可以不写 url。

   ::

      Type: string
      Default: zdb.default_elasticsearch_url

Elasticsearch 选项
''''''''''''''''''

-  ``shards``

   Elasticsearch 中索引的分片数量，默认是每个 index 指定 5 个分片，这个选项可以通过 ``ALTER INDEX`` 进行修改，但是必须执行 ``REINDEX`` 才会生效。

   ::

      Type: integer
      Default: 5
      Range: [1, 32768]

-  ``replicas``

   指定 Elasticsearch 索引的每个分片的副本数量，默认值是系统 GUC 值 ``zdb.default_replicas``\ ，可以通过 ``ALTER INDEX`` 进行修改并且是立即生效的。

   ::

      Type: integer
      Default: zdb.default_replicas

-  ``alias``

   索引的别名，可以以更加方便可读的方式来命名 ZomboDB 的索引，可以通过 ``ALTER INDEX`` 进行修改并且是立即生效。

   普通的 SELECT 语句使用的是实际的索引名，而聚合函数例如 ``zdb.count``\ 、\ ``zdb.terms`` 则会使用索引别名。

   ::

      Type: string
      Default: "database.schema.table.index-index_oid"

-  ``refresh_interval``

   这个选项指定了 Elasticsearch 索引多久对修改进行一次刷新，以保证其可以被搜索到。默认这个值是 ``-1``\ ，因为 ZomboDB 想要自己控制何时刷新，来保证 MVCC 的正确性。

   一般情况下，不建议去修改这个配置，除非能够接受 HashData Lightning 搜索的结果暂时不符合预期。可以通过 ``ALTER INDEX`` 进行修改并且是立即生效。

   ::

      Type: string
      Default: "-1"

-  ``type_name``

   指定向 Elasticsearch 索引插入数据的 type 名称。默认情况下，在 Elasticsearch 5x 和 6x 下这个 type 是 ``_doc``\ ，在 Elasticsearch 7x 及之后，这个选项被废弃，只能指定为 ``_doc``\ ，因此这种情况下没必要去修改这个值。

   注意这个选项只能在创建索引的时候进行指定，不能通过 ``ALTER INDEX`` 修改。

   ::

      Type: string
      Default: "_doc"

-  ``translog_durability``

   在每次 Index、delete、update、bulk request 之后，是否需要持久化并提交 Elasticsearch 索引的 translog，这个选项接受以下两个有效的值。

   -  request：在每次请求之后，都持久化并提交 translog，在硬件发生故障的情况下，已经提交的修改不会丢失。
   -  async：每次持久化和提交 translog 都由默认的间隔调度，如果硬件发生故障，可能丢失部分数据。

   在 Elasticsearch 7.4 之后，这个选项被废弃了，在后续的版本中可能被删除。可参考 `Elasticsearch 官方文档 <https://www.elastic.co/guide/en/elasticsearch/reference/7.16/index-modules-translog.html#%5C_translog_settings>`__\ 。

   ::

      Type: string
      Default: "request"
      Valid values: "request", "async"

-  ``max_result_window``

   ZomboDB 在每次 scroll 请求中可以接受的从 Elasticsearch 中获取的最大数据量。参考 `Elasticsearch 官方文档 <https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules.html#index-max-result-window>`__\ 。

   ::

      Tyoe: integer
      Default: 10000
      Range: [1, INT_32_MAX]

-  ``total_fields_limit``

   Elasticsearch 中 index 的最大字段数。参考 `Elasticsearch 官方文档 <https://www.elastic.co/guide/en/elasticsearch/reference/master/mapping-settings-limit.html>`__\ 。

   ::

      Type: integer
      Default: 1000
      Range: [1, INT_32_MAX]

-  ``max_terms_count``

   在 Elasticsearch 的 Term 查询中，可以使用的最大 Term 条件数量。增加这个选项可能使 cross-index join 的性能得到提升。参考 `Elasticsearch 官方文档 <https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules.html#index-max-terms-count>`__\ 。

   ::

      Type: integer
      Default: 65535
      Range: [1, INT_32_MAX]

-  ``max_analyze_token_count``

   ``_analyze`` API 给单次请求生成的最大的 token 数量，这个选项通常是给非常大的文档开启自定义的高亮时使用。参考 `Elasticsearch 官方文档 <https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-analyze.html#tokens-limit-settings>`__\ 。

   ::

      Type: integer
      Default: 10000
      Range: [1, INT_32_MAX]

网络选项
''''''''

-  ``bulk_concurrency``

   当向 Elasticsearch 写入数据的时候，ZomboDB 是发送多次 HTTP 请求。这个配置可以控制发送请求的并发数据量，可以通过这个配置来保证并发数量不会压垮 Elasticsearch 的集群。可以通过 ``ALTER INDEX`` 修改并立即生效。

   ::

      Type: integer
      Default: CPU 核心数
      Range: [1, CPU 核心数]

-  ``batch_size``

   当向 Elasticsearch 写入数据的时候，ZomboDB 会将多次请求通过批量发送一次 HTTP 请求到 ES，默认值是 8 MB。

   ::

      Type: integer (in bytes)
      Default: 8388608
      Range: [1024, (INT_MAX/2)-1]

-  ``compression_level``

   设置 HTTP 请求包的压缩级别，网络环境越差，可以将其设置为一个更大的值。设置为 0 表示关闭所有的压缩。

   ::

      Type: integer
      Default: 1
      Range: [0, 9]

嵌套类型 Mapping 选项
'''''''''''''''''''''

-  ``nested_fields_limit``

   一个索引中不同的嵌套 Mapping 的最大个数。参考 `Elasticsearch 官方文档 <https://www.elastic.co/guide/en/elasticsearch/reference/master/mapping-settings-limit.html>`__\ 。

   ::

      Type: integer
      Default: 1000
      Range: [1, INT_32_MAX]

-  ``nested_objects_limit``

   一个包含所有嵌套类型的文档的最大嵌套 JSON 类型的数量。当一个文档包含了太多的嵌套类型的时候，这个选项可以预防内存溢出错误。参考 `Elasticsearch 官方文档 <https://www.elastic.co/guide/en/elasticsearch/reference/master/mapping-settings-limit.html#mapping-settings-limit>`__\ 。

   ::

      Type: integer
      Default: 10000
      Range: [1, INT_32_MAX]

-  ``nested_object_date_detection``

   如果这个选项打开的话（默认不启用），拥有 json 或者 jsonb 类型的嵌套对象，其新的 string 类型的字段会去检查其文档是否匹配指定的动态日期格式。参考 `Elasticsearch 官方文档 <https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-field-mapping.html#date-detection>`__\ 。

   ::

      Type: bool
      Default: false

-  ``nested_object_numeric_detection``

   类似 ``nested_object_date_detection`` 选项，但是是针对的数值类型，例如 float 或者 integer。参考 `Elasticsearch 官方文档 <https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-field-mapping.html#numeric-detection>`__\ 。

   ::

      Type: bool
      Default: true

-  ``nested_object_text_mapping``

   默认情况下，ZomboDB 会使用上述的 mapping 类型来映射 string 类型的属性，如果在嵌套对象中存在的话。

   只能在创建索引的时候更改。

   ::

      Type: String (as JSON)
      Default: {
              "type": "keyword",
              "ignore_above": 10922,
              "normalizer": "lowercase",
              "copy_to": "zdb_all"
              }

高级选项
''''''''

-  ``include_source``

   此配置控制每个文档的源字段是否应该包含在 Elasticsearch 的 ``_source`` 字段中。关闭此选项可以减少 ES 文档的大小，但是并不建议在生产环境中这样做。

   ::

      Type: bool
      Default: true

使用示例
^^^^^^^^

下面以一个完整的示例，来展示如何创建和使用 ZomboDB 索引。

1. 进入 HashData Lightning 集群环境，创建 demo 示例数据库。

   .. code:: bash

      createdb demo

2. 打开 psql 客户端，并连接到 demo 数据库。

   .. code:: bash

      psql demo

3. 创建示例数据表 products。

   .. code:: sql

      CREATE TABLE products (
      id SERIAL8 NOT NULL PRIMARY KEY,
      name text NOT NULL,
      keywords varchar(64)[],
      short_summary text,
      long_description text,
      price bigint,
      inventory_count integer,
      discontinued boolean default false,
      availability_date date
      ) DISTRIBUTED BY (id);

4. 向 products 表中插入几条数据。

   .. code:: sql

      COPY products FROM PROGRAM 'curl https://raw.githubusercontent.com/zombodb/zombodb/master/TUTORIAL-data.dmp';

5. 检查 ZomboDB 插件是否存在，如果不存在则创建 ZomboDB 插件。

   .. code:: sql

      SELECT * FROM pg_extension WHERE extname = 'zombodb';

      -- 如果不存在则创建插件
      CREATE extension zombodb;

6. 创建 ZomboDB 索引，需要保证有一个可用的 Elasticsearch 集群，并且网络和 HashData Lightning 集群保持畅通。

   .. code:: sql

      CREATE INDEX idxproducts ON products USING zombodb ((products.*)) WITH (url='http://<Elastic 集群 IP 地址>:9200/');

   这里使用 ``products.*`` 表示为 products 表的所有字段创建索引，这意味着 products 表的每个字段都会存储到 Elasticsearch 中。也可以索引指定的字段，具体用法可见管理索引小节。url 是 Elasticsearch 集群的地址和端口。

   .. attention::

      -  如果编译的 ZomboDB 是 HTTPS 版本，那么这里的 url 地址需要填写 ``https``\ 。
      -  如果有用户名和密码验证，那么需要在 url 中加上用户名和密码，例如：\ ``http://username:password@<Elastic 集群 IP 地址>:9200/``\ 。

7. 查看 products 表结构信息，检查 ZomboDB 索引是否创建成功。

   .. code:: none

      demo=# \d products
                                              Table "public.products"
          Column       |          Type           | Collation | Nullable |               Default
      -------------------+-------------------------+-----------+----------+--------------------------------------
      id                | bigint                  |           | not null | nextval('products_id_seq'::regclass)
      name              | text                    |           | not null |
      keywords          | character varying(64)[] |           |          |
      short_summary     | text                    |           |          |
      long_description  | text                    |           |          |
      price             | bigint                  |           |          |
      inventory_count   | integer                 |           |          |
      discontinued      | boolean                 |           |          | false
      availability_date | date                    |           |          |
      Indexes:
          "products_pkey" PRIMARY KEY, btree (id)
          "idxproducts" zombodb ((products.*)) WITH (url='http://localhost:9200/')
      Distributed by: (id)

8. 开始执行 ZomboDB 查询，使用 ZomboDB 的查询操作符 ``==>`` 即可，下面是一个简单的模糊查询的例子。

   .. code:: sql

      demo=# select * from products where products ==> 'sports,box';
      id |   name   |               keywords               |         short_summary          |                                  long_description                                   | price | inventory_count | discontinued | availability_date
      ----+----------+--------------------------------------+--------------------------------+-------------------------------------------------------------------------------------+-------+-----------------+--------------+-------------------
      2 | Baseball | {baseball,sports,round}              | It's a baseball                | Throw it at a person with a big wooden stick and hope they don't hit it             |  1249 |               2 | f            | 2015-08-21
      4 | Box      | {wooden,box,"negative space",square} | Just an empty box made of wood | A wooden container that will eventually rot away.  Put stuff it in (but not a cat). | 17000 |               0 | t            | 2015-07-01
      (2 rows)

   执行以下命令查看这条 SQL 的执行计划，可以看到使用了 ZomboDB 的索引进行查询。

   .. code:: sql

      demo=# explain select * from products where products ==> 'sports,box';
                                          QUERY PLAN
      ------------------------------------------------------------------------------------
      Gather Motion 3:1  (slice1; segments: 3)  (cost=0.00..0.03 rows=1 width=153)
      ->  Index Scan using idxproducts on products  (cost=0.00..0.01 rows=1 width=153)
              Index Cond: (ctid ==> '{"query_string":{"query":"sports,box"}}'::zdbquery)
      Optimizer: Postgres query optimizer

ZomboDB 查询语法
~~~~~~~~~~~~~~~~

ZomboDB Query Language (ZQL) 是 ZomboDB 提供的简单文本查询的语法。ZQL 提供下列的查询语法：

-  布尔操作符 (WITH、AND、OR、NOT)
-  单词
-  短语
-  指定字段
-  近似单词或短语
-  通配符
-  直接通过 Elasticsearch 的 JSON 查询

布尔查询
^^^^^^^^

例子 1：查询任意字段包含 wine 或者 bear，并且包含 cheese 的文档。

.. code:: sql

   select * from products where products ==> 'wine or bear and cheese';

例子 2：查询所有包含 bear 和 cheese，并且不包含 food，加上包含 wine 的文档。

.. code:: sql

   select * from products where products ==> 'wine or beer and cheese not food';

布尔条件也可以使用对应的操作符替代。

-  WITH: ``%``
-  AND: ``&``
-  OR: ``,``
-  NOT: ``!``

所以上面的例子可以进行如下改写。

.. code:: sql

   wine & bear,cheese

.. code:: sql

   wine, bear & cheese !food

指定字段查询
^^^^^^^^^^^^

例子：直接在 sql 中指定某个字段进行查询。

.. code:: sql

   ubuntu=# select * from products where products ==> 'price:17000';
    id | name |               keywords               |         short_summary          |                                  long_description                                   | price |
    inventory_count | discontinued | availability_date
   ----+------+--------------------------------------+--------------------------------+-------------------------------------------------------------------------------------+-------+
   -----------------+--------------+-------------------
     4 | Box  | {wooden,box,"negative space",square} | Just an empty box made of wood | A wooden container that will eventually rot away.  Put stuff it in (but not a cat). | 17000 |
                  0 | t            | 2015-07-01
   (1 row)

Value List 查询
^^^^^^^^^^^^^^^

ZomboDB 支持 Value List 查询，在 sql 中指定需要查询的字段的 value 数组，用 ``[]`` 表示。例子：

.. code:: sql

   select * from products where products ==> 'price=[17000,1249]';

近似搜索
^^^^^^^^

近似搜索允许表明条件（或短语）应该在一定数量的标记内。操作符是 ``W/n`` 和 ``WO/n``\ ，其中 n 表示距离。W/n 表示任意顺序，WO/n 表示按顺序。例如：句子 ``The quick brown fox jumped over the lazy dog's back``\ ，近似搜索的短语 ``jumped w/2 quick``\ ，即可匹配到上面的句子。原因：

-  jumped 和 quick 之间的距离不超过 2。
-  没有顺序的限制。

如果近似搜索的短语是 ``jumped wo/2 quick``\ ，则不能匹配到上面的句子，因为顺序是相反的。

例子：

.. code:: sql

   ubuntu=# select * from products where products ==> 'will w/2 wooden';
    id | name |               keywords               |         short_summary          |                                  long_description                                   | price |
    inventory_count | discontinued | availability_date
   ----+------+--------------------------------------+--------------------------------+-------------------------------------------------------------------------------------+-------+
   -----------------+--------------+-------------------
     4 | Box  | {wooden,box,"negative space",square} | Just an empty box made of wood | A wooden container that will eventually rot away.  Put stuff it in (but not a cat). | 17000 |
                  0 | t            | 2015-07-01
   (1 row)

Elasticsearch JSON 查询
^^^^^^^^^^^^^^^^^^^^^^^

ZomboDB 允许使用直接兼容 Elasticsearch 的 JSON 查询。事实上，这个功能在 ZomboDB 的查询语言中作为一个单运算符运行，所以可以将 Elasticsearch 的 JSON 查询与 ZomboDB 的查询结构混合匹配。

要使用直接的 JSON 查询，只需将 Elasticsearch 兼容的 JSON 包裹在 ``({})`` 中。

例子：

.. code:: none

   ubuntu=# select * from products where products ==> 'square or ({"term": {"price": 1899}})';
    id |   name    |                     keywords                      |                  short_summary                  |                                              long_descript
   ion                                              | price | inventory_count | discontinued | availability_date
   ----+-----------+---------------------------------------------------+-------------------------------------------------+-----------------------------------------------------------
   -------------------------------------------------+-------+-----------------+--------------+-------------------
     3 | Telephone | {communication,primitive,"alexander graham bell"} | A device to enable long-distance communications | Use this to call your friends and family and be annoyed by
    telemarketers.  Long-distance charges may apply |  1899 |             200 | f            | 2015-08-11
     4 | Box       | {wooden,box,"negative space",square}              | Just an empty box made of wood                  | A wooden container that will eventually rot away.  Put stu
   ff it in (but not a cat).                        | 17000 |               0 | t            | 2015-07-01
   (2 rows)

Query DSL
~~~~~~~~~

ZomboDB 支持不同的方式来生成适配 Elasticsearch 的查询语句。可以通过 ZomboDB 的 ZQL 查询语句直接生成 JSON 格式的 Elasticsearch Query DSL，或者使用 ZomboDB 的类似于 Elasticsearch Query DSL 的 SQL Builder API。

无论使用 ZomboDB 的何种方式进行查询，例如典型的 SELECT 语句或者聚合函数，都可以更换为下面的查询方式。以 SELECT 语句为例，假设我们的 SQL 是查询所有包含 ``cats and dogs`` 的数据，基础的查询模板如下所示。

.. code:: sql

   SELECT * FROM table WHERE table ==> 'cats and dogs query here'

注意：无论使用哪种查询方式，这个查询实际上是在用 JSON 的方式生成 `Elasticsearch Query DSL <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html>`__\ 。

ZomboDB 使用 ``zdbquery`` 的自定义类型来进行抽象，它可以被转换为 text、json、jsonb 格式。因此，ZomboDB 的查询标识符 ``==>`` 右侧的类型就是 ``zdbquery``\ 。

本小节并不是讲述 Elasticsearch 查询的功能细节，如果觉得这里的信息不太充分，可以查阅 Elasticsearch 相关文档，在适当的地方会有对应的 Elasticsearch 的文档链接。也就是说，本小节讨论的是如何使用 ZomboDB 支持的方式来生成查询。

ZomboDB 查询语句
~~~~~~~~~~~~~~~~

ZQL 是 ZomboDB 特有的文本类型查询语句，可以指定一些复杂条件的查询格式，例如：

.. code:: sql

   select * from products where products ==> 'box wooden';
   select * from products where products ==> 'box AND wooden';

为了展示这种查询条件所代表的对应 Elasticsearch 的 JSON 格式的 QueryDSL，可以使用 zdb.dump_query 函数来查询展示，如下所示。

.. code:: none

   demo=# select zdb.dump_query('idxproducts', 'box and wooden');
                 dump_query
   ---------------------------------------
    {                                    
      "bool": {                          
        "must": [                        
          {                              
            "bool": {                    
              "should": [                
                {                        
                  "match": {             
                    "zdb_all": {         
                      "query": "box",    
                      "boost": 1.0       
                    }                    
                  }                      
                },                       
                {                        
                  "match": {             
                    "long_description": {
                      "query": "box",    
                      "boost": 1.0       
                    }                    
                  }                      
                }                        
              ]                          
            }                            
          },                             
          {                              
            "bool": {                    
              "should": [                
                {                        
                  "match": {            
                    "zdb_all": {         
                      "query": "wooden", 
                      "boost": 1.0       
                    }                    
                  }                      
                },                       
                {                        
                  "match": {             
                    "long_description": {
                      "query": "wooden", 
                      "boost": 1.0       
                    }                    
                  }                      
                }                        
              ]                          
            }                            
          }                              
        ]                                
      }                                  
    }

Direct JSON
^^^^^^^^^^^

ZQL 是一种更易读的方式，也可以直接指定 Elasticsearch 中的 JSON 查询条件，如下所示。

.. code:: none

   demo=# select * from products where products ==> '{ "bool": { "should": [ { "bool": { "should": [ { "match": { "zdb_all": { "query": "box", "boost": 1.0 } } }, { "match": { "long_description": { "query": "box", "boost": 1.0 } } } ] } }, { "bool": { "should": [ { "match": { "zdb_all": { "query": "wooden", "boost": 1.0 } } }, { "match": { "long_description": { "query": "wooden", "boost": 1.0 } } } ] } } ] } }';
    id |   name   |               keywords               |         short_summary          |                                  long_description                                   | pri
   ce | inventory_count | discontinued | availability_date
   ----+----------+--------------------------------------+--------------------------------+-------------------------------------------------------------------------------------+----
   ---+-----------------+--------------+-------------------
     2 | Baseball | {baseball,sports,round}              | It's a baseball                | Throw it at a person with a big wooden stick and hope they don't hit it             |  12
   49 |               2 | f            | 2015-08-21
     4 | Box      | {wooden,box,"negative space",square} | Just an empty box made of wood | A wooden container that will eventually rot away.  Put stuff it in (but not a cat). | 170
   00 |               0 | t            | 2015-07-01
   (2 rows)

SQL Builder API
^^^^^^^^^^^^^^^

ZomboDB 以函数方式支持 Elasticsearch 的 Query DSL 查询，并且所有的函数都在名为 dsl 的 scheme 里面。这些函数都会返回 ``zdbquery`` 类型，并且可以互相组合形成复杂的查询条件。

这种 DSL 查询方式的主要优势在于这些方法会在 HashData Lightning 的语法检查阶段进行语法和类型的检查，有错误会及时报告，可以根据报错信息及时修改你的查询。

通常，每个函数和一个 Elasticsearch 的查询类型相关联，这些函数的默认值实际上都是对应的 Elasticsearch 中的查询的默认值。

所有的查询都是通过简单的函数形式，例如下面的查询等价于包含两个关键词的查询 ``box and wooden``\ 。

.. code:: sql

   select * from products where products ==> dsl.and('box', 'wooden');
   select * from products where products ==> dsl.and(dsl.term('zdb_all', 'box'), dsl.term('zdb_all', 'wooden'));

针对 DSL 的函数，可以在其后加 ``::json`` 查询其对应的 JSON 格式。

.. code:: none

   demo=# select dsl.and('box', 'wooden')::json;
                                              and
   ------------------------------------------------------------------------------------------
    {"bool":{"must":[{"query_string":{"query":"box"}},{"query_string":{"query":"wooden"}}]}}
   (1 row)

   demo=# select dsl.and(dsl.term('zdb_all', 'box'), dsl.term('zdb_all', 'wooden'))::json;
                                                  and
   --------------------------------------------------------------------------------------------------
    {"bool":{"must":[{"term":{"zdb_all":{"value":"box"}}},{"term":{"zdb_all":{"value":"wooden"}}}]}}
   (1 row)

简单布尔函数
''''''''''''

-  ``dsl.and``

   生成包含在 Elasticsearch 的 ``must`` 子句中的 bool 条件。

   .. code:: sql

      FUNCTION dsl.and(
          VARIADIC queries zdbquery[]
      ) RETURNS zdbquery

-  ``dsl.or()``

   生成包含在 Elasticsearch 的 ``should`` 子句中的 bool 条件。

   .. code:: sql

      FUNCTION dsl.or(
          VARIADIC queries zdbquery[]
      ) RETURNS zdbquery

-  ``dsl.not()``

   生成包含在 Elasticsearch 的 ``must_not`` 子句中的 bool 条件。

   .. code:: sql

      FUNCTION dsl.not(
          VARIADIC queries zdbquery[]
      ) RETURNS zdbquery

-  `dsl.bool() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html>`_

   这个函数代表 Elasticsearch 中的 ``bool`` 查询，可以包含多个 bool 类型的查询条件，并且可以和 ``dsl.must()``\ 、\ ``dsl.must_not()``\ 、 ``dsl.should()``\ 、\ ``dsl.filter()`` 进行组合，形成复杂的查询。

   .. code:: sql

      FUNCTION dsl.bool(
          VARIADIC queries dsl.esqdsl_bool_part
      ) RETURNS zdbquery

   查询例子：

   .. code:: none

      demo=# select * from products where products ==> dsl.bool(dsl.must('person'), dsl.should('box'));
      id |   name   |        keywords         |  short_summary  |                            long_description                             | price | inventory_count | discontinued | av
      ailability_date
      ----+----------+-------------------------+-----------------+-------------------------------------------------------------------------+-------+-----------------+--------------+---
      ----------------
      2 | Baseball | {baseball,sports,round} | It's a baseball | Throw it at a person with a big wooden stick and hope they don't hit it |  1249 |               2 | f            | 20
      15-08-21
      (1 row)

-  `dsl.must() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html>`__

   这个函数代表 Elasticsearch QueryDSL 中 ``bool`` 查询的 must 子句，它可以作为 ``dsl.bool`` 函数中的 must 条件，并且可以出现多次。

   .. code:: sql

      FUNCTION dsl.must(
          VARIADIC queries zdbquery[]
      )RETURNS dsl.esqdsl_must

-  `dsl.must_not() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html>`__

   这个函数代表 Elasticsearch QueryDSL 中 ``bool`` 查询的 must_not
   子句。

   .. code:: sql

      FUNCTION dsl.must_not (
          VARIADIC queries zdbquery[]
      )RETURNS dsl.esqdsl_must_not

-  `dsl.should() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html>`__

   这个函数代表 Elasticsearch QueryDSL 中 ``bool`` 查询的 should 子句。

   .. code:: sql

      FUNCTION dsl.should (
          VARIADIC queries zdbquery[]
      )RETURNS dsl.esqdsl_should

-  `dsl.filter() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html>`__

   这个函数代表 Elasticsearch QueryDSL 中 ``bool`` 查询的 filter 子句。此函数被设计为与 ``dsl.bool()`` 的筛选参数一起使用。它的参数可以是 ZomboDB 返回 zdbquery 类型的 dsl 函数中的一个或多个。

   .. code:: sql

      FUNCTION dsl.filter (
          VARIADIC queries zdbquery[]
      )RETURNS dsl.esqdsl_filter

ES Query DSL
''''''''''''

-  `dsl.boosting() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-boosting-query.html>`__

   返回与正查询匹配的文档，同时降低与负查询匹配的文档的相关性得分。这个方法表示 Elasticsearch 中的 ``Boosting query``\ 。

   .. code:: sql

      FUNCTION dsl.boosting (
         positive zdbquery,
         negative zdbquery,
         negative_boost real DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.common() <https://www.elastic.co/guide/en/elasticsearch/reference/7.17/query-dsl-common-terms-query.html>`__

   Elasticsearch 7.3.0 之后不再支持，这个方法表示 Elasticsearch 中的 Query DSL common Query。

   .. code:: sql

      FUNCTION dsl.common (
          field text,
          query text,
          boost real DEFAULT NULL,
          cutoff_frequency real DEFAULT NULL,
          analyzer text DEFAULT NULL,
          minimum_should_match integer DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.constant_score() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-constant-score-query.html>`__

   包装了另一个 zdbquery 条件的查询，并为过滤器中的每个文档返回等于查询提升值的常量分数。

   .. code:: sql

      FUNCTION dsl.constant_score (
          boost real,
          query zdbquery)
      RETURNS zdbquery

-  `dsl.datetime_range() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-range-query.html>`__

   匹配文档某个字段的范围，这个函数主要是匹配时间戳类型的数据。此形式用于时间戳值。

   ZomboDB 将自动将指定的时间转换为 UTC（与 Elasticsearch 兼容），但是，如果没有指定时间戳所代表的时区，那么 Cloudberry Database 将首先假设它属于服务器正在运行的任何时区（通过 `TimeZone GUC <https://www.postgresql.org/docs/14/datatype-datetime.html#DATATYPE-TIMEZONES>`__\ ）。

   .. code:: sql

      FUNCTION dsl.datetime_range (
          field text,
          lt timestamp with time zone DEFAULT NULL,
          gt timestamp with time zone DEFAULT NULL,
          lte timestamp with time zone DEFAULT NULL,
          gte timestamp with time zone DEFAULT NULL,
          boost real DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.dis_max() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-dis-max-query.html>`__

   返回一个或多个包装的查询条件所匹配的结果。

   .. code:: sql

      FUNCTION dsl.dis_max (
          queries zdbquery[],
          boost real DEFAULT NULL,
          tie_breaker real DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.field_exists() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-exists-query.html>`__

   返回指定的字段数据不为空的结果。

   .. code:: sql

      FUNCTION dsl.field_exists (
          field text)
      RETURNS zdbquery

-  ``dsl.field_missing()``

   方法行为和 ``dsl.field_exists`` 相反，返回指定字段数据为空的文档。

   .. code:: sql

      FUNCTION dsl.field_missing (
          field text)
      RETURNS zdbquery

-  `dsl.fuzzy() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-fuzzy-query.html>`__

   Elasticsearch 中的 fuzzy 查询，基于莱文斯坦编辑距离算法。

   .. code:: sql

      FUNCTION dsl.fuzzy (
          field text,
          value text,
          boost real DEFAULT NULL,
          fuzziness integer DEFAULT NULL,
          prefix_length integer DEFAULT NULL,
          max_expansions integer DEFAULT NULL,
          transpositions boolean DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.match() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html>`__

   ``match`` 查询，可以接受 text、numerics 和 datas 类型，分析这些条件，并返回匹配的结果。zerotermsquery 为枚举值，可以取 ``none`` 和 ``all``\ 。

   .. code:: sql

      FUNCTION dsl.match (
          field text,
          query text,
          boost real DEFAULT NULL,
          analyzer text DEFAULT NULL,
          minimum_should_match integer DEFAULT NULL,
          lenient boolean DEFAULT NULL,
          fuzziness integer DEFAULT NULL,
          fuzzy_rewrite text DEFAULT NULL,
          fuzzy_transpositions boolean DEFAULT NULL,
          prefix_length integer DEFAULT NULL,
          cutoff_frequency real DEFAULT NULL,
          auto_generate_synonyms_phrase_query boolean DEFAULT NULL,
          zero_terms_query zerotermsquery DEFAULT NULL,
          operator operator DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.match_all() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-all-query.html>`__

   最简单的查询条件，匹配所有的结果。

   .. code:: sql

      FUNCTION dsl.match_all (
          boost real DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.match_phrase() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query-phrase.html>`__

   ``match_phrase`` 查询分析文本并生成短语查询。

   .. code:: sql

      FUNCTION dsl.match_phrase (
          field text,
          query text,
          boost real DEFAULT NULL,
          slop integer DEFAULT NULL,
          analyzer text DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.match_phrase_prefix() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query-phrase-prefix.html>`__

   ``ds.match_phrase_prefix()`` 和 ``match_phrase`` 类似，只是它可以支持在最后一个 text 查询中匹配前缀。

   .. code:: sql

      FUNCTION dsl.match_phrase_prefix (
          field text,
          query text,
          boost real DEFAULT NULL,
          slop integer DEFAULT NULL,
          analyzer text DEFAULT NULL,
          max_expansions integer DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.more_like_this() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-mlt-query.html>`__

   More Like This 查询找到和指定文档相似的文档集合。

   .. code:: sql

      FUNCTION dsl.more_like_this (
          "like" text,
          fields text[] DEFAULT NULL,
          stop_words text[] DEFAULT ARRAY[...],
          boost real DEFAULT NULL,
          unlike text DEFAULT NULL,
          analyzer text DEFAULT NULL,
          minimum_should_match integer DEFAULT NULL,
          boost_terms real DEFAULT NULL,
          include boolean DEFAULT NULL,
          min_term_freq integer DEFAULT NULL,
          max_query_terms integer DEFAULT NULL,
          min_doc_freq integer DEFAULT NULL,
          max_doc_freq integer DEFAULT NULL,
          min_word_length integer DEFAULT NULL,
          max_word_length integer DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.multi_match() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html>`__

   multi_match 基于 match 查询，支持多字段的查询。zerotermsquery 为枚举值，可以取 ``none`` 和 ``all``\ 。

   .. code:: sql

      FUNCTION dsl.multi_match (
          fields text[],
          query text,
          boost real DEFAULT NULL,
          analyzer text DEFAULT NULL,
          minimum_should_match integer DEFAULT NULL,
          lenient boolean DEFAULT NULL,
          fuzziness integer DEFAULT NULL,
          fuzzy_rewrite text DEFAULT NULL,
          fuzzy_transpositions boolean DEFAULT NULL,
          prefix_length integer DEFAULT NULL,
          cutoff_frequency real DEFAULT NULL,
          auto_generate_synonyms_phrase_query boolean DEFAULT NULL,
          zero_terms_query zerotermsquery DEFAULT NULL,
          operator operator DEFAULT NULL,
          match_type matchtype DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.query_string() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html>`__

   相当于 Elasticsearch 中的 query string。querystringdefaultoperator 为枚举值，可以取 ``and`` 和 ``or``\ 。

   .. code:: sql

      FUNCTION dsl.query_string(
          query text,
          default_field text DEFAULT NULL,
          allow_leading_wildcard boolean DEFAULT NULL,
          analyze_wildcard boolean DEFAULT NULL,
          analyzer text DEFAULT NULL,
          auto_generate_synonyms_phrase_query boolean DEFAULT NULL,
          boost real DEFAULT NULL,
          default_operator querystringdefaultoperator DEFAULT NULL,
          enable_position_increments boolean DEFAULT NULL,
          fields text[] DEFAULT NULL,
          fuzziness integer DEFAULT NULL,
          fuzzy_max_expansions bigint DEFAULT NULL,
          fuzzy_transpositions boolean DEFAULT NULL,
          fuzzy_prefix_length bigint DEFAULT NULL,
          lenient boolean DEFAULT NULL,
          max_determinized_states bigint DEFAULT NULL,
          minimum_should_match integer DEFAULT NULL,
          quote_analyzer text DEFAULT NULL,
          phrase_slop bigint DEFAULT NULL,
          quote_field_suffix text DEFAULT NULL,
          time_zone text DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.nested() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-nested-query.html>`__

   嵌套查询允许查询嵌套的对象或者文档。scoremode 为枚举值，可以取 ``avg``, ``sum``, ``min``, ``max`` 和 ``none``\ 。

   .. code:: sql

      FUNCTION dsl.nested (
          path text,
          query zdbquery,
          score_mode scoremode DEFAULT 'avg'::scoremode),
          ignore_unmapped boolean DEFAULT NULL
      RETURNS zdbquery

-  ``dsl.noteq()``

   生成一个 bool 查询，其参数必须是 must_not 的字段。

   .. code:: sql

      FUNCTION dsl.noteq (
          query zdbquery)
      RETURNS zdbquery

-  ``dsl.phrase()``

   类似于 ``dsl.match_phrase`` 函数，只是参数更精简。

   .. code:: sql

      FUNCTION dsl.phrase (
          field text,
          query text,
          boost real DEFAULT NULL,
          slop integer DEFAULT NULL,
          analyzer text DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.prefix() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-prefix-query.html>`__

   匹配包含具体前缀的字段的文档。

   .. code:: sql

      FUNCTION dsl.prefix (
          field text,
          prefix text,
          boost real DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.range() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-range-query.html>`__

   匹配指定字段的一个范围，目前针对 numeric 类型的字段，返回包含匹配字段的文档。

   .. code:: sql

      FUNCTION dsl.range (
          field text,
          lt numeric DEFAULT NULL,
          gt numeric DEFAULT NULL,
          lte numeric DEFAULT NULL,
          gte numeric DEFAULT NULL,
          boost real DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.range() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-range-query.html>`__

   匹配指定字段的一个范围，目前针对 text 类型的字段，返回包含匹配字段的文档。

   .. code:: sql

      FUNCTION dsl.range (
          field text,
          lt text DEFAULT NULL,
          gt text DEFAULT NULL,
          lte text DEFAULT NULL,
          gte text DEFAULT NULL,
          boost real DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.regexp() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-regexp-query.html>`__

   正则表达式匹配。

   .. code:: sql

      FUNCTION dsl.regexp (
          field text,
          regexp text,
          boost real DEFAULT NULL,
          flags regexflags[] DEFAULT NULL,
          max_determinized_states integer DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.script() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-script-query.html>`__

   允许使用自定义脚本作为查询条件。

   .. code:: sql

      FUNCTION dsl.script (
          source_code text,
          params json DEFAULT NULL,
          lang text DEFAULT 'painless'::text)
      RETURNS zdbquery

-  `dsl.span_containing() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-span-containing-query.html>`__

   返回包含另一个 query 查询的条件。

   .. code:: sql

      FUNCTION dsl.span_containing (
          little zdbquery,
          big zdbquery)
      RETURNS zdbquery

-  `dsl.span_first() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-span-first-query.html>`__

   等价于 Elasticsearch 中的 span first 查询。

   .. code:: sql

      FUNCTION dsl.span_first (
          query zdbquery,
          "end" integer)
      RETURNS zdbquery

-  `dsl.span_masking() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-span-field-masking-query.html>`__

   等价于 Elasticsearch 中的 span field masking 查询。

   .. code:: sql

      FUNCTION dsl.span_masking (
          field text,
          query zdbquery)
      RETURNS zdbquery

-  `dsl.span_multi() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-span-multi-term-query.html>`__

   等价于 Elasticsearch 中的 span multi term 查询。

   .. code:: sql

      FUNCTION dsl.span_multi (
          query zdbquery)
      RETURNS zdbquery

-  `dsl.span_near() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-span-near-query.html>`__

   等价于 Elasticsearch 中的 span near 查询。

   .. code:: sql

      FUNCTION dsl.span_near (
          in_order boolean,
          slop integer,
          VARIADIC clauses zdbquery[])
      RETURNS zdbquery

-  `dsl.span_not() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-span-not-query.html>`__

   等价于 Elasticsearch 中的 span not 查询。

   .. code:: sql

      FUNCTION dsl.span_not (
          include zdbquery,
          exclude zdbquery,
          pre integer DEFAULT NULL,
          post integer DEFAULT NULL,
          dist integer DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.span_or() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-span-or-query.html>`__

   等价于 Elasticsearch 中的 span or 查询。

   .. code:: sql

      FUNCTION dsl.span_or (
          VARIADIC clauses zdbquery[])
      RETURNS zdbquery

-  `dsl.span_term() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-span-term-query.html>`__

   等价于 Elasticsearch 中的 span term 查询。

   .. code:: sql

      FUNCTION dsl.span_term (
          field text,
          value text,
          boost real DEFAULT NULL)
      RETURNS zdbquery

-  `dsl.span_within() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-span-within-query.html>`__

   等价于 Elasticsearch 中的 span within 查询。

   .. code:: sql

      FUNCTION dsl.span_within (
          little zdbquery,
          big zdbquery)
      RETURNS zdbquery

-  ``dsl.term()``

   ``dsl.term`` 支持多种数据类型查询，可以通过 ``\df dfs.term`` 查看，下面以 numeric 为例。

   .. code:: sql

      FUNCTION dsl.term (
          field text,
          value numeric,
          boost real DEFAULT NULL)
      RETURNS zdbquery

   在倒排索引中，指定字段的条件查询。这个方法只针对 numeric 类型的数据。例子：

   .. code:: sql

      select * from articles where articles==>dsl.terms('body', 'one', 'two');

   该语句会将如下格式的 json 传递给 ES 进行查询。

   .. code:: shell

      {"term":{"body":{"value":12}}}

-  `dsl.terms() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-terms-query.html>`__

   ``dsl.terms`` 支持多种数据类型查询，可以通过 ``\df dfs.terms`` 查看，下面以 text 为例。

   .. code:: none

      postgres=# \df dsl.terms;
                                          List of functions
      Schema | Name  | Result data type |               Argument data types                | Type 
      --------+-------+------------------+--------------------------------------------------+------
      dsl    | terms | zdbquery         | field text, VARIADIC "values" bigint[]           | func
      dsl    | terms | zdbquery         | field text, VARIADIC "values" boolean[]          | func
      dsl    | terms | zdbquery         | field text, VARIADIC "values" double precision[] | func
      dsl    | terms | zdbquery         | field text, VARIADIC "values" integer[]          | func
      dsl    | terms | zdbquery         | field text, VARIADIC "values" real[]             | func
      dsl    | terms | zdbquery         | field text, VARIADIC "values" smallint[]         | func
      dsl    | terms | zdbquery         | field text, VARIADIC "values" text[]             | func
      (7 rows)

   .. code:: sql

      FUNCTION dsl.terms (
          field text,
          VARIADIC "values" text[])
      RETURNS zdbquery

   返回任意字段包含查询条件的数据，这个方法只针对 text 类型的数据。例子：

   .. code:: sql

      select * from articles where articles==>dsl.terms('body', 'one', 'two');

   该语句会将如下格式的 json 传递给 ES 进行查询。

   .. code:: shell

      {"terms":{"body":["one","two"]}}

-  `dsl.terms_array() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-terms-query.html>`__

   相当于包含多个 term 条件的 dsl.term 函数，针对任意类型的数据。第二个字段适用于 Postgres 任意数据类型的数组。

   .. code:: sql

      FUNCTION dsl.terms_array (
          field text,
          "values" anyarray)
      RETURNS zdbquery

-  `dsl.terms_lookup() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-terms-query.html#query-dsl-terms-lookup>`__

   相当于 Elasticsearch 中的 Query DSL terms lookup 查询。当有多个过滤字段的时候，使用该函数非常有用。

   .. code:: sql

      FUNCTION dsl.terms_lookup (
          field text,
          index text,  -- es_index_name, 可以通过select es_index_name from zdb.zdb.index_stats; 获得
          type text,
          id text,
          path text,
          routing text) -- 格式 segment-index, 示例：segment-1,表示查询gp_segment_id 为 1 的数据
      RETURNS zdbquery

-  `dsl.wildcard() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-wildcard-query.html>`__

   返回匹配通配符条件的数据。

   支持的通配符是 ``.*``\ （匹配任何字符序列，包括空字符），以及 ``?``\ （匹配任何单个字符）。注意，该查询可能很慢，因为需要遍历许多项。为了防止通配符查询极其缓慢，通配符术语不应该以通配符 ``.*`` 或 ``?`` 开头。

   .. code:: sql

      FUNCTION dsl.wildcard (
          field text,
          wildcard text,
          boost real DEFAULT NULL)
      RETURNS zdbquery

PostGIS 支持
^^^^^^^^^^^^

ZomboDB 中提供了对 PostGIS 插件最基础的支持。

ZomboDB 会自动将 ``geometry`` 和 ``geography`` 类型映射为 Elasticsearch 中的 ``geo_shape`` 类型。

-  `dsl.geo_shape() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-geo-shape-query.html>`__

   geo_shape 查询使用与 geo_shape 映射相同的网格正方形，表示查找具有与查询形状相交的形状的文档。 它还将使用与字段映射定义相同的 PrefixTree 配置。

   查询支持定义查询形状的方法：通过提供整个形状定义。

   .. code:: sql

      FUNCTION dsl.geo_shape(
          field text,
          geojson_shape json,
          relation geoshaperelation
      ) RETURNS zdbquery

-  `dsl.geo_polygon() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-geo-polygon-query.html>`__

   给定一个 point 对象数组，生成 Elasticsearch 中的 ``geo_polygon`` 查询。

   .. code:: sql

      FUNCTION dsl.geo_polygon(
          field text, 
          VARIADIC points point[]
      ) RETURNS zdbquery

-  `dsl.geo_bounding_box() <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-geo-bounding-box-query.html>`__

   给定一个 box 对象，生成 Elasticsearch 的 ``geo_bounding_box`` 查询。

   .. code:: sql

      FUNCTION dsl.geo_bounding_box(
          field text, 
          bounding_box box, 
          box_type geoboundingboxtype DEFAULT 'memory'::geoboundingboxtype
      )

聚合函数
~~~~~~~~

ZomboDB 支持几乎所有 Elasticsearch 中的聚合操作，并将其封装成对应的 sql 函数。在所有的场景中，以下函数返回的结果保证了事务层面的正确性。

任意 JSON 聚合
^^^^^^^^^^^^^^

-  `zdb.arbitrary_agg <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html>`__

   这个函数支持所有 Elasticsearch 中的 JSON 格式的查询语句，返回值是 JSON 格式的数据。

   .. code:: sql

      FUNCTION zdb.arbitrary_agg(
          index regclass,
          query zdbquery,
          agg_json json) 
      RETURNS json

单值聚合
^^^^^^^^

-  `zdb.avg <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-avg-aggregation.html>`__

   查询指定条件下，指定字段的平均值。

   .. code:: sql

      FUNCTION zdb.avg(
          index regclass,
          field text,
          query zdbquery) 
      RETURNS numeric

   例子：

   .. code:: sql

      demo=# select zdb.avg('idxproducts', 'price', dsl.match_all());
      avg
      ------
      7512
      (1 row)

-  `zdb.cardinality <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-cardinality-aggregation.html>`__

   计算不同值的近似计数的单值指标聚合。可以从文档中的特定字段中提取值。

   .. code:: sql

      FUNCTION zdb.cardinality(
          index regclass,
          field text,
          query zdbquery) 
      RETURNS numeric

-  `zdb.count <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-count.html>`__

   返回指定查询条件下，Elasticsearch 中文档的数据总计，类似 Elasticsearch 中的 ``_count`` API。

   .. code:: sql

      FUNCTION zdb.count(
          index regclass,
          query zdbquery) 
      RETURNS bigint

-  ``zdb.raw_count``

   和 ``zdb.count`` 类似，但是不保证事务层面的正确性，它会统计所有 Elasticsearch 中对应索引的文档，比如被删除的、旧版本的数据。

   .. code:: sql

      FUNCTION zdb.raw_count(
          index regclass,
          query zdbquery) 
      RETURNS bigint SET zdb.ignore_visibility = true

-  `zdb.max <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-max-aggregation.html>`__

   返回指定查询条件下，指定字段的最大值。

   .. code:: sql

      FUNCTION zdb.max(
          index regclass,
          field text,
          query zdbquery) 
      RETURNS numeric

   例子：

   .. code:: sql

      ubuntu=# select zdb.max('idxproducts', 'price', dsl.match_all());
      max
      -------
      17000

-  `zdb.min <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-max-aggregation.html>`__

   返回指定查询条件下，指定字段的最小值。

   .. code:: sql

      FUNCTION zdb.min(
          index regclass,
          field text,
          query zdbquery) 
      RETURNS numeric

-  `zdb.missing <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-missing-aggregation.html>`__

   查询在指定条件下，指定字段为空，或者没有这个字段的数据量。

   .. code:: sql

      FUNCTION zdb.missing(
          index regclass,
          field text,
          query zdbquery) 
      RETURNS numeric

-  `zdb.sum <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-sum-aggregation.html>`__

   返回指定查询条件下，指定字段的总计值。

   .. code:: sql

      FUNCTION zdb.sum(
          index regclass,
          field text,
          query zdbquery) 
      RETURNS numeric

-  `zdb.value_count <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-valuecount-aggregation.html>`__

   查询指定条件下，值的总计。

   .. code:: sql

      FUNCTION zdb.value_count(
          index regclass,
          field text,
          query zdbquery) 
      RETURNS numeric

多行/列聚集
^^^^^^^^^^^

-  ``zdb.adjacency_matrix`` 返回邻接矩阵形式的 bucket 聚合。

   .. code:: sql

      FUNCTION zdb.adjacency_matrix(
          index regclass,
          labels text[],
          filters zdbquery[]) 
      RETURNS TABLE (
          key text,
          doc_count bigint)

-  ``zdb.adjacency_matrix_2x2`` 与 ``zdb.adjacency_matrix`` 类似，但是返回的是 2x2 的矩阵。

   .. code:: sql

      FUNCTION zdb.adjacency_matrix_2x2(
          index regclass,
          labels text[],
          filters zdbquery[]) 
      RETURNS TABLE (
          "-" text,
          "1" text,
          "2" text)

-  ``zdb.adjacency_matrix_3x3`` 与 ``zdb.adjacency_matrix`` 类似，但是返回的是 3x3 的矩阵。

   .. code:: sql

      FUNCTION zdb.adjacency_matrix_3x3(
          index regclass,
          labels text[],
          filters zdbquery[]) 
      RETURNS TABLE (
          "-" text,
          "1" text,
          "2" text),
          "3" text)

-  ``zdb.adjacency_matrix_4x4`` 与 ``zdb.adjacency_matrix`` 类似，但是返回的是 4x4 的矩阵。

   .. code:: sql

      FUNCTION zdb.adjacency_matrix_4x4(
          index regclass,
          labels text[],
          filters zdbquery[]) 
      RETURNS TABLE (
          "-" text,
          "1" text,
          "2" text),
          "3" text),
          "4" text)

-  ``zdb.adjacency_matrix_5x5`` 与 ``zdb.adjacency_matrix`` 类似，但是返回的是 5x5 的矩阵。

   .. code:: sql

      FUNCTION zdb.adjacency_matrix_5x5(
          index regclass,
          labels text[],
          filters zdbquery[]) 
      RETURNS TABLE (
          "-" text,
          "1" text,
          "2" text),
          "3" text),
          "4" text),
          "5" text)

-  `zdb.date_histogram <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-datehistogram-aggregation.html>`__

   相当于 Elasticsearch 中的直方图查询，只能用于 date 数据类型。由于日期在 Elasticsearch 内部表示为 long 值，因此也可以在日期上使用正常直方图，但准确性会受到影响。

   .. code:: sql

      FUNCTION zdb.date_histogram(
          index regclass,
          field text,
          query zdbquery,
          "interval" text,
          format text DEFAULT 'yyyy-MM-dd') 
      RETURNS TABLE (
          key numeric,
          key_as_string text,
          doc_count bigint)

-  `zdb.date_range <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-daterange-aggregation.html>`__

   专用于日期值的范围聚合。

   .. code:: sql

      FUNCTION zdb.date_range(
          index regclass,
          field text,
          query zdbquery,
          date_ranges_array json) 
      RETURNS TABLE (
          key text,
          "from" numeric,
          from_as_string timestamp with time zone,
          "to" numeric,
          to_as_string timestamp with time zone,
          doc_count bigint)

-  `zdb.extended_stats <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-extendedstats-aggregation.html>`__

   一种多值指标聚合，用于计算从聚合文档中提取的数值的统计信息。 这些值可以从文档中的特定数字字段中提取。

   .. code:: sql

      FUNCTION zdb.extended_stats(
          index regclass,
          field text,
          query zdbquery,
          sigma int DEFAULT 0) 
      RETURNS TABLE (
          count bigint,
          min numeric,
          max numeric,
          avg numeric,
          sum numeric,
          sum_of_squares numeric,
          variance numeric,
          stddev numeric,
          stddev_upper numeric,
          stddev_lower numeric)

-  `zdb.filters <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-filters-aggregation.html>`__

   类似 ``zdb.count``\ ，支持多个 zdbquery 的查询条件。

   .. code:: sql

      FUNCTION zdb.filters(
          index regclass,
          labels text[],
          filters zdbquery[]) 
      RETURNS TABLE (
          label text,
          doc_count bigint)

-  `zdb.histogram <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-histogram-aggregation.html>`__

   Elasticsearch 中的多桶直方图查询。

   .. code:: sql

      FUNCTION zdb.histogram(
          index regclass,
          field text,
          query zdbquery,
          "interval" float8) 
      RETURNS TABLE (
          key numeric,
          doc_count bigint)

-  `zdb.ip_range <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-iprange-aggregation.html>`__

   IP 地址类型的数据的范围聚合查询。

   .. code:: sql

      FUNCTION zdb.ip_range(
          index regclass,
          field text,
          query zdbquery,
          ip_ranges_array json) 
      RETURNS TABLE (
          key text,
          "from" inet,
          "to" inet,
          doc_count bigint)

-  `zdb.matrix_stats <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-matrix-stats-aggregation.html>`__

   matrix_stats 聚合是一种数值聚合操作，计算文档的某些字段的统计值。

   .. code:: sql

      FUNCTION zdb.matrix_stats(
          index regclass,
          fields text[],
          query zdbquery) 
      RETURNS TABLE (
          name text,
          count bigint,
          mean numeric,
          variance numeric,
          skewness numeric,
          kurtosis numeric,
          covariance json,
          correlation json)

-  `zdb.percentile_ranks <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-percentile-rank-aggregation.html>`__

   用于计算从聚合文档中提取的数值的一个或多个百分位数排名。

   .. code:: sql

      FUNCTION zdb.percentile_ranks(
          index regclass,
          field text,
          query zdbquery,
          "values" text DEFAULT '') 
      RETURNS TABLE (
          percentile numeric,
          value numeric)

-  `zdb.percentiles <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-percentile-aggregation.html>`__

   一种多值指标聚合，用于计算从聚合文档中提取的数值的一个或多个百分位数。 这些值可以从文档中的特定数字字段中提取。

   .. code:: sql

      FUNCTION zdb.percentiles(
          index regclass,
          field text,
          query zdbquery,
          percents text DEFAULT '') 
      RETURNS TABLE (
          percentile numeric,
          value numeric)

-  `zdb.range <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-range-aggregation.html>`__

   range 范围查询。

   .. code:: sql

      FUNCTION zdb.range(
          index regclass,
          field text,
          query zdbquery,
          ranges_array json) 
      RETURNS TABLE (
          key text,
          "from" numeric,
          "to" numeric,
          doc_count bigint)

-  `zdb.significant_terms <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-significantterms-aggregation.html>`__

   返回集合中有趣的或异常出现的术语的聚合。

   具体而言，该聚合可以在一个数据集中找到出现频率高于期望值的术语，从而发现数据集中的有趣信息。它可以用于分析文本数据，例如新闻文章、社交媒体帖子或产品评论等等。 
   .. code:: sql

      FUNCTION zdb.significant_terms(
          index regclass, 
          field text, 
          query zdbquery, 
          include text DEFAULT '.*'::text, 
          size_limit integer DEFAULT 2147483647, 
          min_doc_count integer DEFAULT 3)
      RETURNS TABLE (
          term text,
          doc_count bigint,
          score numeric,
          bg_count bigint)

-  ``zdb.significant_terms_two_level``

   兼容 ``zdb.significant_terms`` 函数，并使用 ``zdb.terms`` 函数作为 first_field，\ ``zdb.significant_terms`` 作为 second_field。

   .. code:: sql

      FUNCTION zdb.significant_terms_two_level(
          index regclass,
          first_field text,
          second_field text,
          query zdbquery,
          size bigint DEFAULT 0) 
      RETURNS TABLE (
          first_term text,
          second_term text,
          doc_count bigint,
          score numeric,
          bg_count bigint,
          doc_count_error_upper_bound bigint,
          sum_other_doc_count bigint)

-  `zdb.significant_text <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-significanttext-aggregation.html>`__

   类似于 ``zdb.significant_terms``\ ，但有以下区别。

   -  专门为类型文本字段而设计。
   -  不需要字段数据或文档值。
   -  对文本内容进行即时重新分析，这意味着它也可以过滤重复的、有噪音的文本部分，否则会使统计数据出现偏差。

   .. code:: sql

      FUNCTION zdb.significant_text(
          index regclass,
          field text,
          query zdbquery,
          sample_size int DEFAULT 0,
          filter_duplicate_text boolean DEFAULT true) 
      RETURNS TABLE (
          term text,
          doc_count bigint,
          score numeric,
          bg_count bigint)

-  `zdb.suggest_terms <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-suggesters.html>`__

   不算聚合函数，主要功能是对 terms 的查询语句提供建议。

   .. code:: sql

      FUNCTION zdb.suggest_terms(
          index regclass,
          field_name text,
          suggest test,
          query zdbquery,
      ) RETURNS TABLE (
          term text,
          offset bigint,
          length bigint,
          suggestion text,
          score double precision,
          frequency bigint,
      )

-  `zdb.stats <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-stats-aggregation.html>`__

   多值度量聚合，对从聚合的文档中提取的数值进行计算统计。这些数值可以从文档中的特定数字字段中提取。

   .. code:: sql

      FUNCTION zdb.stats(
          index regclass,
          field text,
          query zdbquery) 
      RETURNS TABLE (
          count bigint,
          min numeric,
          max numeric,
          avg numeric,
          sum numeric
      )

-  ``zdb.tally``

   提供了对 Elasticsearch 术语聚合的直接访问，不能与 fulltext 类型的字段一起使用。其结果是事务安全的。

   如果没有指定词干，将不会返回任何结果。要匹配所有术语，请使用 ``^.*`` 的词干。

   .. code:: sql

      FUNCTION zdb.tally(
          index regclass, 
          field_name text,
          [ is_nested bool],
          stem text, 
          query ZDBQuery, 
          size_limit integer DEFAULT '2147483647', 
          order_by TermsOrderBy DEFAULT 'count', 
          shard_size integer DEFAULT '2147483647', 
          count_nulls bool DEFAULT 'true'
      ) RETURNS TABLE (
          term text,
          count bigint
      )

   ``zdb.tally`` 函数的参数说明如下。

   -  index：要查询的 ZomboDB 索引的名称。
   -  field_name：字段的名称，从该字段衍生出查询条件。
   -  is_nested_bool：可选参数，表示术语应该只来自匹配的嵌套对象子元素，默认值是 false。
   -  stem：一个正则表达式，用来过滤返回的 term。
   -  zdbquery：zdbquery 条件。
   -  order_by：如何对结果进行排序。order_by 参数的默认值是 count，它按出现次数从大到小对文档进行排序。reverse_count 的值会将它们从小到大排序。
   -  count_nulls：包含 NULL（即缺失）值的行是否应该包括在结果中。

-  ``zdb.terms_array``

   与函数 ``zdb.terms`` 类似，只是返回的格式是 ``text[]``\ 。

   .. code:: sql

      FUNCTION zdb.terms_array(
          index regclass,
          field text,
          query zdbquery,
          size_limit bigint DEFAULT 0,
          order_by TermsOrderBy DEFAULT 'count') 
      RETURNS text[]

-  ``zdb.terms_two_level``

   与 ``zdb.significant_terms_two_level()`` 类似，适配 ``zdb.terms`` 函数，只是提供了两级的嵌套 term 条件，分别对应 first_field 和 second_field。

   .. code:: sql

      FUNCTION zdb.terms_two_level(
          index regclass,
          first_field text,
          second_field text,
          query zdbquery,
          order_by TwoLevelTermsOrderBy DEFAULT 'count',
          size bigint DEFAULT 0) 
      RETURNS TABLE (
          first_term text,
          second_term text,
          doc_count bigint
      )

-  `zdb.top_hits <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-top-hits-aggregation.html>`__

   top_hits 聚合可以跟踪被聚合的最相关的文档。这个聚合函数的目的是作为子聚合器使用，这样就可以在每个桶中聚合出最匹配的文档。

   .. code:: sql

      FUNCTION zdb.top_hits(
          index regclass,
          fields text[],
          query zdbquery,
          size int) 
      RETURNS TABLE (
          ctid tid,
          score float4,
          source json
      )

-  ``zdb.top_hits_with_id``

   与 ``zdb.top_hits`` 类似，只是返回了 Elasticsearch 中的 \_id 字段，而不是 HashData Lightning 系统列 ctid。

   .. code:: sql

      FUNCTION zdb.top_hits_with_id(
          index regclass,
          fields text[],
          query zdbquery,
          size_limit int) 
      RETURNS TABLE (
          _id text,
          score float4,
          source json
      )

排序和高亮
~~~~~~~~~~

ZomboDB 提供了 zdb.score 和 zdb.highlight 方法用于排序和高亮。

-  ``zdb.score``

   ZomboDB 提供了 ``zdb.score`` 方法来返回当前行的分数。可以使用 zdb.score，并且可以通过 ``zdb.score`` 来排序。

   .. code:: sql

      FUNCTION
          zdb.score(tid)
      RETURNS real;

   在没有 ORDER BY 子句的 sql 语句中，结果集返回的顺序是不确定的，如果想要按照 Elasticsearch 的文档分值来进行排序的话，可以使用 ``zdb.score``\ 。

   ``zdb.score`` 函数的参数始终是 HashData Lightning 表中每条数据的系统隐藏列 ctid，ZomboDB 使用这个 ctid 标识数据的唯一性。

   下面以取出分值并根据分值排序为例。

   .. code:: none

      demo=# select zdb.score(ctid), * from products where products ==> 'sports,box' order by score desc;
          score        | id |   name   |               keywords               |         short_summary          |                                  long_description
                      | price | inventory_count | discontinued | availability_date
      --------------------+----+----------+--------------------------------------+--------------------------------+---------------------------------------------------------------------
      ----------------+-------+-----------------+--------------+-------------------
      1.8357605934143066 |  4 | Box      | {wooden,box,"negative space",square} | Just an empty box made of wood | A wooden container that will eventually rot away.  Put stuff it in (
      but not a cat). | 17000 |               0 | t            | 2015-07-01
      1.363322138786316 |  2 | Baseball | {baseball,sports,round}              | It's a baseball                | Throw it at a person with a big wooden stick and hope they don't hit
      it             |  1249 |               2 | f            | 2015-08-21
      (2 rows)

-  ``zdb.highlight``

   ZomboDB 支持查询结果的高亮，调用函数 ``zdb.highlight`` 即可。

   .. code:: sql

      FUNCTION
          zdb.highlight(
              tid, 
              fieldname [, json_highlight_descriptor]
          ) 
      RETURNS text[];

   和 ``zdb.score`` 函数一样，\ ``zdb.highlight`` 函数的第一个参数是系统隐藏列 ctid。

   高亮查询示例如下。

   .. code:: none

      demo=# select zdb.highlight(ctid, 'long_description'), * from products where products ==> 'wooden,person';
                                                  highlight                                             | id |   name   |               keywords               |         short_summary
              |                                  long_description                                   | price | inventory_count | discontinued | availability_date
      --------------------------------------------------------------------------------------------------+----+----------+--------------------------------------+------------------------
      --------+-------------------------------------------------------------------------------------+-------+-----------------+--------------+-------------------
      {"Throw it at a <em>person</em> with a big <em>wooden</em> stick and hope they don't hit it"}    |  2 | Baseball | {baseball,sports,round}              | It's a baseball
              | Throw it at a person with a big wooden stick and hope they don't hit it             |  1249 |               2 | f            | 2015-08-21
      {"A <em>wooden</em> container that will eventually rot away.  Put stuff it in (but not a cat)."} |  4 | Box      | {wooden,box,"negative space",square} | Just an empty box made
      of wood | A wooden container that will eventually rot away.  Put stuff it in (but not a cat). | 17000 |               0 | t            | 2015-07-01
      (2 rows)

   可以看到查询的结果集中，返回了一个表示高亮数据的 ``highlight`` 字段。

   还可以对高亮显示的 tag 进行修改，默认是 ``<em></em>``\ ，如下所示，将 tag 改为了 ``<b></b>``\ 。

   .. code:: none

      demo=# SELECT zdb.score(ctid), zdb.highlight(ctid, 'long_description', zdb.highlight(pre_tags=>'{<b>}', post_tags=>'{</b>}')), long_description FROM products WHERE products ==> 'wooden,person' ORDER BY score desc;
          score        |                                           highlight                                            |                                  long_description

      --------------------+------------------------------------------------------------------------------------------------+------------------------------------------------------------
      -------------------------
      1.9209332466125488 | {"Throw it at a <b>person</b> with a big <b>wooden</b> stick and hope they don't hit it"}      | Throw it at a person with a big wooden stick and hope they
      don't hit it
      1.839343547821045 | {"A <b>wooden</b> container that will eventually rot away.  Put stuff it in (but not a cat)."} | A wooden container that will eventually rot away.  Put stuf
      f it in (but not a cat).
      (2 rows)

SQL 函数
~~~~~~~~

ZomboDB 提供了一些有用的功能函数，来帮助查询索引的相关信息。

函数描述及例子如下。

-  ``zdb.internal_version``

   返回当前安装的 ZomboDB 共享库的版本。

   如果返回的数据格式不符合
   ``SELECT zdb.schema_version()``\ ，说明版本存在问题。

-  ``zdb.schema_version``

   返回 ZomboDB 版本信息的格式，如下所示。

   .. code:: sql

      demo=# select zdb.schema_version();
              schema_version
      --------------------------------
      @DEFAULT_VERSION@ (@GIT_HASH@)
      (1 row)

-  ``zdb.request``

   向指定 index 的 Elasticsearch 集群发送 HTTP 请求。

   .. code:: sql

      FUNCTION zdb.request(index regclass, 
          endpoint text, 
          method text DEFAULT 'GET', 
          post_data text DEFAULT NULL) 
      RETURNS text

   例子：查看索引的配置信息。

   .. code:: none

      demo=# select zdb.request('idxproducts', '_settings');





                                                                                      request





      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      {"42529.2200.43269.43277":{"settings":{"index":{"mapping":{"nested_fields":{"limit":"1000"},"nested_objects":{"limit":"10000"},"total_fields":{"limit":"1000"}},"refresh_interval
      ":"-1","translog":{"durability":"request"},"provided_name":"42529.2200.43269.43277","query":{"default_field":"zdb_all"},"max_result_window":"10000","creation_date":"1672039152946
      ","sort":{"field":"zdb_ctid","order":"asc"},"analysis":{"filter":{"zdb_truncate_to_fit":{"length":"10922","type":"truncate"},"shingle_filter":{"max_shingle_size":"2","min_shingle
      _size":"2","token_separator":"$","output_unigrams":"true","type":"shingle"},"shingle_filter_search":{"max_shingle_size":"2","min_shingle_size":"2","token_separator":"$","output_u
      nigrams_if_no_shingles":"true","output_unigrams":"false","type":"shingle"}},"normalizer":{"exact":{"filter":["lowercase"],"type":"custom","char_filter":[]},"lowercase":{"filter":
      ["lowercase"],"type":"custom","char_filter":[]}},"analyzer":{"fulltext_with_shingles_search":{"filter":["lowercase","shingle_filter_search"],"type":"custom","tokenizer":"standard
      "},"emoji":{"tokenizer":"emoji"},"phrase":{"copy_to":"zdb_all","filter":["zdb_truncate_to_fit","lowercase"],"type":"standard"},"zdb_all_analyzer":{"filter":["zdb_truncate_to_fit"
      ,"lowercase"],"type":"standard"},"fulltext":{"filter":["zdb_truncate_to_fit","lowercase"],"type":"standard"},"zdb_standard":{"filter":["zdb_truncate_to_fit","lowercase"],"type":"
      standard"},"fulltext_with_shingles":{"filter":["lowercase","shingle_filter","zdb_truncate_to_fit"],"type":"custom","tokenizer":"standard"}},"tokenizer":{"emoji":{"pattern":"([\\u
      d83c\\udf00-\\ud83d\\ude4f]|[\\ud83d\\ude80-\\ud83d\\udeff])","type":"pattern","group":"1"}}},"max_terms_count":"65535","number_of_replicas":"0","uuid":"n1FUxdmtQei32AmeOU4JIg","
      version":{"created":"7170499"},"routing":{"allocation":{"include":{"_tier_preference":"data_content"}}},"number_of_shards":"5","analyze":{"max_token_count":"10000"}}}}}
      (1 row)

   还可以直接发送搜索数据的请求，例子如下。

   .. code:: none

      demo=# select zdb.request('idxproducts', '_search');


                                              request


      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      -------------------------------------------------------------------------------------------
      {"took":1,"timed_out":false,"_shards":{"total":5,"successful":5,"skipped":0,"failed":0},"hits":{"total":{"value":2,"relation":"eq"},"max_score":1.0,"hits":[{"_index":"42529.2200
      .43283.43292","_type":"_doc","_id":"281474976710657","_score":1.0,"_routing":"segment-1","_source":{"id":1,"name":"Magical Widget","keywords":["magical","widget","round"],"short_
      summary":"A widget that is quite magical","long_description":"Magical Widgets come from the land of Magicville and are capable of things you can't imagine","price":9900,"inventor
      y_count":42,"discontinued":false,"availability_date":"2015-08-31","zdb_ctid":1,"zdb_cmin":0,"zdb_cmax":0,"zdb_xmin":3}},{"_index":"42529.2200.43283.43292","_type":"_doc","_id":"z
      db_aborted_xids","_score":1.0,"_routing":"segment-0","_source":{"zdb_aborted_xids":[]}}]}}
      (1 row)

-  `profile_query <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-profile.html>`__

   使用 Elasticsearch 的 Profile API 提供 Query 的详细查询时间和执行细节信息。

   .. code:: sql

      FUNCTION profile_query(index regclass, query zdbquery) RETURNS json

-  ``zdb.determine_index``

   提供 relation 的 OID，或者包含 ZomboDB 索引的表、索引名称，返回具体的 ZomboDB 索引名称。

   .. code:: sql

      FUNCTION zdb.determine_index(relation regclass) RETURNS regclass

-  ``zdb.index_name``

   返回 ZomboDB 为 Elasticsearch 的 index 生成的名称。

   .. code:: sql

      FUNCTION zdb.index_name(index regclass) RETURNS text

   例子：

   .. code:: sql

      demo=# select zdb.index_name('idxproducts');
          index_name
      ------------------------
      42529.2200.43283.43292
      (1 row)

-  ``zdb.index_url``

   返回 ZomboDB 索引对应的 Elasticsearch 集群的地址。

   .. code:: sql

      FUNCTION zdb.index_url(index regclass) RETURNS text

   例子：

   .. code:: sql

      demo=# select zdb.index_url('idxproducts');
          index_url
      ------------------------
      http://localhost:9200/
      (1 row)

-  ``zdb.index_type_name``

   返回 Elasticsearch 索引的 ``_type`` 名称，默认是 doc。

   .. code:: sql

      FUNCTION zdb.index_type_name(index regclass) RETURNS text

   例子：

   .. code:: sql

      demo=# select zdb.index_type_name('idxproducts');
      index_type_name
      -----------------
      doc
      (1 row)

-  ``zdb.index_field_lists``

   返回 ZomboDB 索引定义的字段列表。

   .. code:: sql

      FUNCTION zdb.index_field_lists(index_relation regclass) RETURNS TABLE ("fieldname" text, "fields" text[])

-  ``zdb.index_mapping``

   返回 ZomboDB 索引对应的 Elasticsearch 的 mapping 定义。

   .. code:: none

      demo=# SELECT * FROM zdb.index_mapping('idxproducts');




                                                                                                                          index_mapping





      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      --------------------------------------------------------------------------
      {"42529.2200.43283.43292": {"mappings": {"_routing": {"required": true}, "properties": {"id": {"type": "long"}, "name": {"type": "text", "copy_to": ["zdb_all"], "analyzer": "zdb
      _standard", "fielddata": true}, "price": {"type": "long"}, "zdb_all": {"type": "text", "analyzer": "zdb_all_analyzer"}, "keywords": {"type": "keyword", "copy_to": ["zdb_all"], "n
      ormalizer": "lowercase", "ignore_above": 10922}, "zdb_cmax": {"type": "integer"}, "zdb_cmin": {"type": "integer"}, "zdb_ctid": {"type": "long"}, "zdb_xmax": {"type": "long"}, "zd
      b_xmin": {"type": "long"}, "discontinued": {"type": "boolean"}, "short_summary": {"type": "text", "copy_to": ["zdb_all"], "analyzer": "zdb_standard", "fielddata": true}, "invento
      ry_count": {"type": "integer"}, "long_description": {"type": "text", "analyzer": "fulltext", "fielddata": true}, "zdb_aborted_xids": {"type": "long"}, "availability_date": {"type
      ": "keyword", "fields": {"date": {"type": "date"}}, "copy_to": ["zdb_all"]}}, "date_detection": false, "dynamic_templates": [{"strings": {"mapping": {"type": "keyword", "copy_to"
      : "zdb_all", "normalizer": "lowercase", "ignore_above": 10922}, "match_mapping_type": "string"}}, {"dates_times": {"mapping": {"type": "keyword", "fields": {"date": {"type": "dat
      e", "format": "strict_date_optional_time||epoch_millis||HH:mm:ss.S||HH:mm:ss.SX||HH:mm:ss.SS||HH:mm:ss.SSX||HH:mm:ss.SSS||HH:mm:ss.SSSX||HH:mm:ss.SSSS||HH:mm:ss.SSSSX||HH:mm:ss.S
      SSSS||HH:mm:ss.SSSSSX||HH:mm:ss.SSSSSS||HH:mm:ss.SSSSSSX"}}, "copy_to": "zdb_all"}, "match_mapping_type": "date"}}, {"objects": {"mapping": {"type": "nested", "include_in_parent"
      : true}, "match_mapping_type": "object"}}], "numeric_detection": false}}}
      (1 row)

-  ``zdb.field_mapping``

   返回指定的字段在 Elasticsearch 的 field mapping 定义。

   .. code:: sql

      FUNCTION zdb.field_mapping(index_relation regclass, field_name text) RETURNS json

   例子：

   .. code:: none

      demo=# SELECT * FROM zdb.field_mapping('idxproducts', 'short_summary');
                                          field_mapping
      -----------------------------------------------------------------------------------------
      {"type": "text", "copy_to": ["zdb_all"], "analyzer": "zdb_standard", "fielddata": true}
      (1 row)

ES \_cat API
------------

ZomboDB 支持大多数的 Elasticsearch 的 ``_cat`` API 操作，将其数据映射为对应的视图。

cat API 的视图支持来自多个 Elasticsearch 集群的 ZomboDB 索引。

cat API 的视图功能强大，可以在一些聚合操作中负责复杂的分析操作。

.. list-table:: 
   :header-rows: 1
   :align: left
   :widths: 11 19

   * - API 操作
     - 说明
   * - VIEW zdb.index_stats
     - 严格来说这并不属于标准的 Elasticsearch 的 \_cat API，但它提供了一个简单的视图来查看所有的 ZomboDB 索引统计信息。可以查看索引的名称、别名、URL、表名、数据量大小等信息。
   * - `VIEW zdb.cat_aliases <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-alias.html>`__
     - 查看所有的索引别名，包含 filter 和 routing 相关信息。
   * - `VIEW zdb.cat_allocation <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-allocation.html>`__
     - 查看有多少 Shard 被分配到了哪些 node 上，以及一些磁盘的使用情况统计。
   * - `VIEW zdb.cat_count <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-count.html>`__
     - 查看 Elasticsearch 集群中文档的总和统计，以及每个 index 的文档数量。
   * - `VIEW zdb.cat_fielddata <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-fielddata.html>`__
     - 查看 fielddata 在每个节点上占用了多少堆内存。
   * - `VIEW zdb.cat_health <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-health.html>`__
     - 查看 Elasticsearch 集群的健康状态。
   * - `VIEW zdb.cat_indices <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-indices.html>`__
     - 查看每个索引的统计信息，例如名称、数据量等。
   * - `VIEW zdb.cat_master <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-master.html>`__
     - 返回集群中 master 或 coordinator 节点的信息，包含 IP 地址、节点名称、Node ID 等信息。
   * - `VIEW zdb.cat_nodeattrs <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-nodeattrs.html>`__
     - 查看自定义的节点属性信息。
   * - `VIEW zdb.cat_nodes <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-nodes.html>`__
     - 查看集群中所有的节点信息。
   * - `VIEW zdb.cat_pending_tasks <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-pending-tasks.html>`__
     - 返回当前集群级别的任务列表，即等待被执行的任务，例如创建索引、update、allocate shard 等。
   * - `VIEW zdb.cat_plugins <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-plugins.html>`__
     - 查看集群中安装的 Elasticsearch 插件。
   * - `VIEW zdb.cat_thread_pool <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-thread-pool.html>`__
     - 查看集群中每个 node 上的线程池信息。
   * - `VIEW zdb.cat_shards <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-shards.html>`__
     - 查看每个 Node 上的分片信息。
   * - `VIEW zdb.cat_segments <https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-segments.html>`__
     - 返回集群中每个 index 的分片的 Segment 信息。

Vacuum 支持
-----------

ZomboDB 索引与 HashData Lightning ``(auto)VACUUM`` 操作完全互通，保证 ZomboDB 中索引的数据可以被 ``VACUUM``\ ，这对高水平的搜索性能十分重要。

因为 ZomboDB 在索引中存储了行级的可见性信息，所以 ZomboDB 的 ``Vacuum`` 过程与标准的索引类型如 B-tree 有很大的不同。

ZomboDB 的 Vacuum 的大致原理是：

1. 找到所有被废弃的 xmin 的文档，这些数据代表插入/更新失败或终止的行，它们可以被删除。
2. 找到所有提交的事务的 xmax 文档，这些代表被删除的行，或是提交事务的更新行的旧版本数据，它们可以被删除。
3. 查找所有被废弃的 xmax 的文档，这些数据代表更新/删除事务失败或终止的行，这些行可以将其 xmax 重置为 null。
4. 从 ZomboDB 的废弃事务 id 列表中，确定那些没有被引用为 xmin 或 xmax，这些单独的 xid 值可以从列表中删除，因为它们不再被引用了。

需要注意的是，\ ``VACUUM FULL`` 也会 reindex 表的任何索引，包括 ZomboDB 索引。因此，一个 ``VACUUM FULL`` 可能需要很长的时间。

``VACUUM FREEZE`` 将调整堆上的 ``xmin``/\ ``xmax`` 值，但不会改变 ZomboDB 索引中的任何东西。
