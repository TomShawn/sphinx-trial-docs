并发创建索引
============

CREATE INDEX CONCURRENTLY
-------------------------

本文档介绍如何在 HashData Lightning 中并发创建索引，即在创建索引的同时执行插入、更新、删除语句。

在 HashData Lightning 中使用 ``CREATE INDEX`` 创建索引期间，其他事务虽然可以正常读取表数据，但是 HashData Lightning 会阻塞对表发起的数据插入、更新、删除等 DML 操作。直到索引创建完成，HashData Lightning 才会执行这些 DML 操作。

对于生产环境中的表，如果表数据量较大，使用 ``CREATE INDEX`` 创建索引花费的时间可能很长，导致表数据更新长时间被阻塞，可能出现严重的问题。

为了解决这一问题，你可以使用 ``CREATE INDEX CONCURRENTLY`` 语法来并发创建索引，创建索引期间，HashData Lightning 不会阻塞对应的表数据更新。

**提示**

当指定此选项时，HashData Lightning 将会执行两次表扫描，并且等待所有更新表数据的事务完成。这样创建索引时，会增加一些额外的扫描表开销，可能会比普通创建索引的执行时间更长。但是由于这种方式不阻塞表的正常更新操作，这会对一些生产环境中的数据表非常有用。

使用场景
~~~~~~~~

-  适用于生产环境中数据量较大的表，希望在为表创建索引期间正常执行插入、更新、删除等 DML 操作。
-  对创建索引的速度要求不高，且有充足的系统资源可供消耗，可以接受创建索引的耗时稍长于 ``CREATE INDEX``\ 。

使用方法
~~~~~~~~

1. 执行以下命令并重启 HashData Lightning 数据库，以开启 GDD 相关的配置参数。

   .. code:: shell

      gpconfig -c gp_enable_global_deadlock_detector -v true
      gpstop -ra

   **注意**

   在 HashData Lightning 数据库中，默认关闭 GDD（由配置参数 ``gp_enable_global_deadlock_detector`` 控制）。此时在 ``heap`` 表上执行的 ``UPDATE`` 或 ``DELETE`` 语句将会占据 ``ExclusiveLock`` 锁，而这个锁将会和 ``CREATE INDEX CONCURRENTLY`` 冲突，因此想要在并发创建索引时不阻塞表的 ``UPDATE`` 或 ``DELETE`` 操作，必须先开启 GDD。

2. 使用 ``CREATE INDEX CONCURRENTLY`` 语法并发创建索引。

   假设有一个名为 ``orders`` 的表，其中包含一个名为 ``order_date`` 的日期列。你可以并发地创建一个基于该列的索引 ``idx_orders_order_date``\ ：

   .. code:: sql

      CREATE INDEX CONCURRENTLY idx_orders_order_date ON orders (order_date);

使用限制
~~~~~~~~

-  不支持在临时表上并发创建索引。
-  不支持显式地通过 ``BEGIN`` 开启事务然后执行 ``CREATE INDEX CONCURRENTLY``\ 。
-  目前并发创建索引只支持 ``heap`` 表，不支持 ``AO``/\ ``AOCS`` 表和分区表。但是对于分区表，可以单独为每个分区表并发创建索引。

常见问题处理
~~~~~~~~~~~~

在使用 ``CREATE INDEX CONCURRENTLY`` 创建表索引的过程中，如果出现了错误，例如出现死锁或者唯一索引的唯一性校验失败，索引创建会失败，但是会在表中留下一个 ``INVALID`` 的无效索引。在查询时，HashData Lightning 会被忽略掉这个无效索引，因为它是不完整的。

要查看一张表的无效索引，可以通过 ``\d`` 选项来查看该表的 ``INVALID`` 索引：

.. code:: shell

   cloudberry=# \d tab
                   Table "public.tab"
    Column |  Type   | Collation | Nullable | Default
   --------+---------+-----------+----------+---------
    col    | integer |           |          |
   Indexes:
       "idx_col" btree (col) INVALID
   Distributed by: (col)

对于这种 ``INVALID`` 的无效索引，你可以手动 ``DROP`` 删除掉或者通过 ``REINDEX`` 重新构建索引。

REINDEX CONCURRENTLY
--------------------

本节介绍如何在 HashData Lightning 中并发重建索引，即在重建索引的同时执行插入、更新、删除语句。

在 HashData Lightning 中使用 ``REINDEX`` 重建索引期间，HashData Lightning 会锁定索引被重建的表以防止写入，并通过对表的单次扫描来执行整个索引的重建。在此期间，其他事务虽然可以正常读取表数据，但是 HashData Lightning 会阻塞对表发起的数据插入、更新、删除等 DML 操作。直到索引重建完成，HashData Lightning 才会执行这些 DML 操作。

对于实时生产环境中的数据库，在大表上执行 ``REINDEX`` 索引重建可能需要数小时才能完成。即使是较小的表，索引重建也会锁定写入者的时间，这对生产系统来说是不可接受的。

为了解决这一问题，你可以使用 ``REINDEX CONCURRENTLY`` 语法来并发重建索引，使 HashData Lightning 以最小的写入锁定来重建索引，实现在重建索引期间执行插入、更新、删除等 DML 操作。

.. _使用场景-1:

使用场景
~~~~~~~~

-  适用于生产环境中数据量较大的表，希望在为表重建索引期间正常执行插入、更新、删除等 DML 操作。
-  对重建索引的速度要求不高，且有充足的系统资源可供消耗，可以接受重建索引的耗时长于 ``REINDEX``\ 。

实现原理
~~~~~~~~

使用 ``REINDEX CONCURRENTLY`` 并发重建索引时，HashData Lightning 会在多个单独的事务中执行以下内部操作：

1. HashData Lightning 将一个新的临时索引定义添加到 ``pg_index`` 表中，用该索引来替换旧的索引。同时在会话级别加上 ``SHARE UPDATE EXCLUSIVE`` 锁，以防止在处理过程中出现任何模式对表的修改。
2. 扫描表数据，进行第一次建立索引的操作。一旦建立好索引，其标志 ``pg_index.indisready`` 被设置为 ``true``\ ，以准备好插入。执行建立索引的事务结束后，该索引对其他会话是可见的。这个步骤是在一个单独的事务中为每个索引完成的。
3. HashData Lightning 再执行一次表扫描，将第一次扫描过程中被修改的数据更新到索引中。这个步骤也是在单独的事务中完成的。
4. 将旧索引的定义改为引用新的索引定义，同时修改索引的名称。\ ``pg_index.indisvalid`` 的值对于新索引被切换为 ``true``\ ，对于旧的索引被切换为 ``false``\ 。
5. 旧索引的 ``pg_index.indisready`` 被切换为 ``false``\ ，以防止任何新元组的插入。
6. 旧的索引被丢弃。索引和表的 ``SHARE UPDATE EXCLUSIVE`` 锁被释放。

.. _使用方法-1:

使用方法
~~~~~~~~

1. 执行以下命令并重启 HashData Lightning 数据库，以开启 GDD 相关的配置参数。

   .. code:: shell

      gpconfig -c gp_enable_global_deadlock_detector -v true
      gpstop -ra

2. 使用 ``REINDEX CONCURRENTLY`` 语法并发重建索引。

   假设有一个名为 ``orders`` 的表，其中包含一个名为 ``order_date`` 的日期列，该列的索引为 ``idx_orders_order_date``\ 。你可以并发地重建该索引 ``idx_orders_order_date``\ ：

   .. code:: sql

      REINDEX INDEX CONCURRENTLY idx_orders_order_date;

.. _使用限制-1:

使用限制
~~~~~~~~

-  不支持在事务块中执行 ``REINDEX CONCURRENTLY``\ ，也就是说不能显式地通过 ``BEGIN`` 开启事务，然后执行并发重建索引。
-  ``REINDEX SYSTEM`` 不支持 ``CONCURRENTLY`` 并发重构，因为系统目录不能被并发地重建索引。

.. _常见问题处理-1:

常见问题处理
~~~~~~~~~~~~

在使用 ``REINDEX CONCURRENTLY`` 重建索引时，如果出现了问题，例如在一个唯一索引中违反了唯一性约束，\ ``REINDEX CONCURRENTLY`` 命令将会失败。此时除了已存在的旧索引之外，还会留下一个 ``INVALID`` 的临时索引，这个索引在查询中会被忽略，因为它是不完整的。

要查看这个表的 ``INVALID`` 索引，可使用 ``\d`` 选项：

.. code:: shell

   cloudberry=# \d tab
                   Table "public.tab"
    Column |  Type   | Collation | Nullable | Default
   --------+---------+-----------+----------+---------
    col    | integer |           |          |
   Indexes:
       "idx_col_ccnew" btree (col) INVALID
   Distributed by: (col)

-  如果标记为 ``INVALID`` 的索引后缀为 ``ccnew``\ （如上面示例），那么它对应在并发重构操作中创建的临时索引。推荐使用 ``DROP INDEX`` 丢弃该索引，然后再次尝试 ``REINDEX CONCURRENTLY``\ 。
-  如果标记为 ``INVALID`` 的索引后缀为 ``ccold``\ ，那么它对应的是原始索引。推荐通过 ``DROP INDEX`` 直接丢弃该索引，因为重建工作已经成功。
