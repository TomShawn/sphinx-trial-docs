UnionStore 存储格式
===================

本文档介绍 UnionStore 的使用场景、使用方法、使用限制和使用该功能的常见问题。

UnionStore 是面向 Heap 表及其索引的新存储引擎，结合 HashData Lightning 构成计算、存储分离架构。UnionStore 的核心思想是 "Log is database"，通过持久化计算层日志并进行日志 replay 来构建数据，以供计算层查询。

通过 UnionStore 实现计算、存储的解耦，可实现根据实际负载进行计算资源调整，提升资源性价比。UnionStore 支持多租户、单租户多实例读写，可实现资源有效利用、多集群共享同一份数据。

使用场景
--------

构建 UnionStore 集群存储业务/用户数据，适用于以下场景：

-  写多读少：对于写入多查询少、业务数据量较大的场景，UnionStore 可以实现存储扩展并将数据存放在成本更低的可靠性存储，提升存储性价比。
-  读多写少：对于业务查询量较大、写入相对较小的场景，对 CPU、内存资源依赖较多。可将数据存储于 UnionStore，为计算节点配置更多计算资源、减少本地存储资源，提升查询性能。
-  多租户：UnionStore 支持多租户，可将多个计算集群的数据存储在同一个 UnionStore 下的不同租户，实现资源的有效利用。

前提条件
--------

若要在 HashData Lightning 上使用 UnionStore 特性，必须先有一个可用的 HashData Lightning 集群。

安装 UnionStore
---------------

在使用 UnionStore 前，你需要先安装 UnionStore。参照以下步骤进行安装：

.. caution:: 以下安装方法仅适用于 HashData Lightning 在测试环境进行本地部署，不能用于生产环境。

1. 在集群节点目录 ``<>`` 目录中找到 UnionStore 的安装包 ``unionstore.tar.gz``\ ，以及安装脚本 ``unionstore_deploy.sh``\ 。

2. 用 Vim 编辑器打开 ``unionstore_deploy.sh`` 脚本文件，填写脚本中的对应参数，填写后保存关闭。关于参数的描述，见脚本注释。

   .. image:: /images/unionstore-config.png

3. 执行 ``unionstore_deploy.sh`` 脚本， UnionStore 会被自动部署。

使用方法
--------

第 1 步：创建 UnionStore 租户
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

要创建 UnionStore 租户，你需要使用 UnionStore 安装包中的 neon_local 工具。

1. 将 环境变量 :literal:`NEO``N``_REPO_DIR` 设置为 page server 所在的目录，以 ``/home/gpadmin/pageserver`` 为例：

   .. code:: shell

      export NEON_REPO_DIR=/home/gpadmin/pageserver

2. 在 page server 所在机器上执行以下命令创建租户：

   .. code:: shell

      ./target/release/neon_local tenant create

   返回结果如下：

   .. code:: shell

      tenant 176349c483c0578faca41101fa70e19f successfully created on the pageserver

      Created an initial timeline '30cf96abf49fbb6f6c9712fc71c83d40' at Lsn 0/4AABC88 for tenant: 176349c483c0578faca41101fa70e19f

   在返回结果中，\ ``"176349c483c0578faca41101fa70e19f"`` 是新创建的租户 ID，在一个 UnionStore 集群中是唯一的。\ ``"30cf96abf49fbb6f6c9712fc71c83d40"`` 是时间线 ID，类似于 Git 的 branch，这里就使用一个时间线即可。

第 2 步：配置 HashData Lightning 参数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

创建好 UnionStore 租户后，你需要将租户相关信息补充到 HashData Lightning 的配置文件 ``postgresql.conf`` 中，你需要为每个节点的配置文件都补充这些信息，即：

.. raw:: latex

    \begingroup
    \renewcommand{\arraystretch}{1.5} % 调整表格行间距
    \fontsize{5pt}{6pt}\selectfont % 设置表格字体大小为更小

.. list-table::
   :header-rows: 1
   :align: left
   :widths: 15 20 8 8 18

   * - 配置参数名
     - 描述说明
     - 默认值
     - 是否为必填
     - 示例
   * - ``shared_preload_libraries``
     - HashData Lightning 数据库启动时，需要加载插件的动态库名称。
     - 空
     - 是
     - ``shared_preload_libraries = unionstore``
   * - ``unionstore.tenant_id``
     - UnionStore 的租户 ID。
     - 空
     - 是
     - ``unionstore.tenant_id='176349c483c0578faca41101fa70e19f'``
   * - ``unionstore.timeline_id``
     - UnionStore 租户的时间线 ID。
     - 空
     - 是
     - ``unionstore.timeline_id='30cf96abf49fbb6f6c9712fc71c83d40'``
   * - ``unionstore.safekeepers``
     - 日志组件的 IP 和端口，默认是三副本。用来与日志服务建立连接以及持久化日志。需要与安装部署 UnionStore 时你所填写的保持一致。
     - 空
     - 是
     - ``unionstore.safekeepers='127.0.0.1:5454,127.0.0.1:5455,127.0.0.1:5457'``
   * - ``unionstore.pageserver_connstring``
     - UnionStore PageServer 组件的 IP/PORT。用来与 PageServer 建立连接，读取 Page 及其他一些数据。需要与安装部署 UnionStore 时你所填写的保持一致。
     - 空
     - 是
     - ``unionstore.pageserver_connstring='postgresql://no_user:@127.0.0.1:64000'``

.. raw:: latex

    \endgroup

一个示例的配置参数如下，你需要替换为实际的参数值：

::

   shared_preload_libraries=unionstore
   unionstore.tenant_id='176349c483c0578faca41101fa70e19f'
   unionstore.timeline_id='30cf96abf49fbb6f6c9712fc71c83d40'
   unionstore.safekeepers='127.0.0.1:5454,127.0.0.1:5455,127.0.0.1:5457'
   unionstore.pageserver_connstring='postgresql://no_user:@127.0.0.1:64000'

第 3 步：安装 HashData Lightning 插件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HashData Lightning 使用插件与 UnionStore 进行日志写入与数据读取等交互，完成配置之后，你需要在使用 UnionStore 的数据库中安装插件：

.. code:: sql

   CREATE EXTENSION unionstore;

插件安装完成之后，HashData Lightning 会创建新的 access method，通过下面 SQL 语句可以查看：

.. code:: sql

   unionstore=# SELECT * FROM pg_am;

.. code:: sql

   oid  |   amname    |         amhandler         | amtype
   -------+-------------+---------------------------+--------
        2 | heap        | heap_tableam_handler      | t
      403 | btree       | bthandler                 | i
      405 | hash        | hashhandler               | i
      783 | gist        | gisthandler               | i
     2742 | gin         | ginhandler                | i
     4000 | spgist      | spghandler                | i
     3580 | brin        | brinhandler               | i
     7024 | ao_row      | ao_row_tableam_handler    | t
     7166 | ao_column   | ao_column_tableam_handler | t
     7013 | bitmap      | bmhandler                 | i
    16403 | union_store | heap_tableam_handler      | t
   (11 rows)

以上返回结果中，\ ``union_store`` 则是为使用 UnionStore 新创建的 access method。

第 4 步：在 UnionStore 中创建和使用表和索引
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

安装完 HashData Lightning 插件并新建了 union_store 的 access method 后，就可以创建 UnionStore 表和索引了。

创建 UnionStore 表的语法如下：

.. code:: sql

   CREATE TABLE <table_name> (xxx) USING union_store;

创建 UnionStore Btree 索引(其他索引类似)的语法如下：

.. code:: sql

   CREATE INDEX ON <table_name> USING BTREE (column_name);

示例如下：

.. code:: sql

   --- 建表
   CREATE TABLE unionstore_table (c1 INT, c2 VARCHAR, c3 TIMESTAMP) USING union_store;

   unionstore=# \dt+ unionstore_table
                                                List of relations
    Schema |       Name       | Type  |  Owner  | Storage | Persistence | Access method |  Size  | Description
   --------+------------------+-------+---------+---------+-------------+---------------+--------+-------------
    public | unionstore_table | table | gpadmin |         | permanent   | union_store   | 128 kB |
    
    --- 建索引
   CREATE INDEX ON unionstore_table USING btree (c1);
    
    --- 写入数据
   INSERT INTO unionstore_table SELECT t,t,now() FROM generate_series(1,100) t;
    
    --- 查询
   SELECT * FROM unionstore_table WHERE c1 = 55;

    c1 | c2 |             c3
   ----+----+----------------------------
    55 | 55 | 2023-07-04 16:47:49.373224
   (1 row)

使用限制
--------

-  UnionStore 不支持存储 AO 或 AOCS 表。

-  UnionStore 不支持 temp 和 unlogged 表及其索引。

   UnionStore 核心思想是 "Log is database"，但是 temp 和 unlogged 表没有日志，因此无法将其数据持久化到 UnionStore，所以无法支持。

-  UnionStore 不支持 tablespace。

   UnionStore 底层实现目前只支持 default tablespace，所以使用 UnionStore 无法进行 tablespace 的创建、database/table/index 的 tablespace 修改。

兼容信息
--------

只有 v1.4.0 及后续版本的 HashData Lightning 可以使用 UnionStore。v1.3.0 以及之前版本的 HashData Lightning 不兼容 UnionStore，因为这些版本的内核未做兼容和适配。
