扩缩容集群
==========

HashData Lightning 通过 gpshrink 与 gpexpand 实现弹性伸缩，gpshrink 和 gpexpand 是 HashData Lightning 的缩容和扩容工具。gpexpand 源于 Greenplumn，而 gpshrink 则是在 HashData Lightning v1.5.2 中进一步实现的新特性。

-  集群资源空闲时，例如磁盘空间占用长期低于 20%、CPU 或内存占用率持续较低，则可以使用 gpshrink 来实现集群的缩容，从而节省服务器资源。
-  集群资源紧张时，例如磁盘空间占用长期超过 80%、CPU 或内存占用率持续较高，则可以通过 gpexpand 来实现集群的扩容，从而增加服务器资源。

对于集群扩容，用户通过增加服务器资源，然后通过 gpexpand 工具可以在新增的服务器上增加新的 segment，从而实现集群的扩容。对于集群缩容，用户可以通过 gpshrink 工具删除多余服务器上的 segment，从而实现集群缩容。

gpshrink 和 gpexpand 在执行时分为两阶段：

-  在准备阶段，会收集数据库中所有需要重分布的用户表信息。
-  在数据重分布阶段，会将数据库集群中的所有表进行数据重分布，即将现有的数据库集群中的数据重新分布到扩容或缩容后的数据库中。

使用 gpshrink 缩容集群
----------------------

1. 创建一个三节点的集群。

   .. code:: bash

      make create-demo-cluster

2. 创建测试表 test 并查看缩容前的状态。

   .. code:: sql

      -- 建表并插入数据
      CREATE TABLE test(a INT); 
      INSERT INTO test SELECT i FROM generate_series(1,100) i;
      -- 查看 test 表的数据分布
      SELECT gp_segment_id, COUNT(*) FROM test GROUP BY gp_segment_id;
      -- 查看元数据状态
      SELECT * FROM gp_distribution_policy;
      SELECT * FROM gp_segment_configuration;

3. 创建 shrinktest 文件，在其中写入待删除的 segment 的信息。

   .. code:: sql

      touch shrinktest

   segment 信息的格式为 ``hostname|address|port|datadir|dbid|content|role``\ ，每个 segment 的信息需包括 primary 和 mirror 的信息，如下所示。若要删除多个 segment，则需将 ``content`` 较大的 segment 写在前面，确保 perferred role 与 role 是一致的，先写 p 再写 m。

   .. code:: bash

      # 以删除一个 segment 为例，以下为写入的 primary 和 mirror 的信息
      i-thd001y0|i-thd001y0|7004|/home/gpadmin/cloudberrydb/gpAux/gpdemo/datadirs/dbfast3/demoDataDir2|4|2|p
      i-thd001y0|i-thd001y0|7007|/home/gpadmin/cloudberrydb/gpAux/gpdemo/datadirs/dbfast_mirror3/demoDataDir2|7|2|m

4. 执行 ``gsphrink`` 命令两次。

   .. code:: bash

      # 准备阶段
      gpshrink -i shrinktest
      # 重分布阶段
      gpshrink -i shrinktest

   ======== ==================================================
   主要参数 描述
   ======== ==================================================
   -i       指定要删除的 segment 文件。
   -c       清理已收集的表信息。
   -a       收集重分布后表的统计信息。
   -d       设置最长执行持续时间，超时将终止，用于重分布阶段。
   ======== ==================================================

   gpshrink 主要分两阶段实现：

   -  第一条 ``gpshrink -i shrinktest`` 命令实际上完成了缩容的准备工作：基于输入文件 ``shrinktest`` 读取被删除的 segment，创建对应的表 ``gpshrink.status``\ （用于记录 gpshrink 的状态和 ``gpshrink.status_detail``\ （用于记录每个表的状态），并获取所有需要执行重分布的表。

   -  第二条 ``gpshrink -i shrinktest`` 命令则完成了缩容的数据重分布工作：计算删除 segment 后的 sgement size，对每个表执行 ``gpshrink``\ ，实现数据重分布，最后在 ``gp_segment_configuration`` 中删除相应的 segment。在重分布阶段，不建议用户执行创建表的操作，因为新建的表将无法重分布在缩容后的集群中。也可能会出现一些语句执行失败的现象，因为有些表处于被锁定状态。

   -  若第一条 ``gpshrink -i shrinktest`` 执行失败，可能的原因是 ``shrinktest`` 文件错误导致执行中断，此时只需通过 ``gpshrink -c`` 清除其中收集的数据，再重新执行 ``gpshrink -i shrinktest``\ 。
   -  若第二条 ``gpshrink -i shrinktest`` 发生错误，用户需要登陆数据库，检查数据库中表的状态，并进行进一步的数据重分布或者回滚。

5. 缩容后再次查看 test 表的状态。

   .. code:: sql

      -- 查看 test 表的数据分布
      SELECT gp_segment_id, COUNT(*) FROM test GROUP BY gp_segment_id;
      -- 查看元数据状态
      SELECT * FROM gp_distribution_policy;
      SELECT * FROM gp_segment_configuration;

使用 gpexpand 扩容集群
----------------------

1. 创建一个三个节点的集群。

   .. code:: bash

      make create-demo-cluster

2. 创建测试表 test 并查看扩容前的状态。

   .. code:: sql

      -- 建表并插入数据
      CREATE TABLE test(a INT); 
      INSERT INTO test SELECT i FROM generate_series(1,100) i;
      -- 查看 test 表的数据分布
      SELECT gp_segment_id, COUNT(*) FROM test GROUP BY gp_segment_id;
      -- 查看元数据状态
      SELECT * FROM gp_distribution_policy;
      SELECT * FROM gp_segment_configuration;

3. 创建 expandtest 文件，在其中写入待增加的 segment 的信息。

   .. code:: shell

      touch expandtest

   Segment 信息的格式为 ``hostname|address|port|datadir|dbid|content|mode``\ ，每个 segment 的信息需包括 primary 和 mirror 的信息，下面以增加两个节点为例：

   .. code:: bash

      # 以增加两个 segment 为例，以下为写入的 primary 和 mirror 的信息
      i-thd001y0|i-thd001y0|7008|/home/gpadmin/cloudberrydb/gpAux/gpdemo/datadirs/dbfast4/demoDataDir3|9|3|p
      i-thd001y0|i-thd001y0|7009|/home/gpadmin/cloudberrydb/gpAux/gpdemo/datadirs/dbfast_mirror4/demoDataDir3|10|3|m
      i-thd001y0|i-thd001y0|7010|/home/gpadmin/cloudberrydb/gpAux/gpdemo/datadirs/dbfast5/demoDataDir4|11|4|p
      i-thd001y0|i-thd001y0|7011|/home/gpadmin/cloudberrydb/gpAux/gpdemo/datadirs/dbfast_mirror5/demoDataDir4|12|4|m

4. 执行 ``gpexpand`` 命令两次。

   .. code:: bash

      # 准备阶段
      gpexpand -i expandtest
      # 重分布阶段
      gpexpand -i expandtest

   ==== ==================================================
   参数 描述
   ==== ==================================================
   -i   指定要增加的 segment 文件。
   -c   清理已收集的表信息。
   -a   搜集表的统计信息。
   -d   设置最长执行持续时间，超时将终止，用于重分布阶段。
   ==== ==================================================

   gpexpand 主要分两阶段实现：

   -  第一条 ``gpexpand -i expandtest`` 命令实际上完成了扩容的准备工作：基于输入文件 ``expandtest`` 将必要的 package、tablespace 状态拷贝到 segment 节点，然后启动 segment 节点，将新增的节点加入 ``gp_segemnt_configuration``\ ，并创建相关的状态表 ``gpexpand.status``\ （用于记录 gpexpand 的状态）和 ``gpexpand.status_detail``\ （用于记录每个表的状态）。
   -  第二条 ``gpexpand -i expandtest`` 命令则完成了扩容的数据重分布工作：将对每个表执行 ``alter table $table_name expand table``\ ，该过程会通过进程池加速执行。在重分布阶段，不建议用户执行创建表的操作，因为新建的表将无法重分布在扩容后的集群中。也可能会出现一些语句执行失败的现象，因为有些表处于锁定状态。

   -  若第一条 ``gpexpand -i expandtest`` 执行失败，可能的原因是 ``expandtest`` 文件错误导致执行中断，此时只需通过 ``gpexpand -c`` 清除其中收集的数据，再重新执行 ``gpexpand -i expandtest``\ 。
   -  若第二条 ``gpexpand -i expandtest`` 发生错误，用户需要登陆数据库，检查数据库中表的状态，并进行进一步的数据重分布或者回滚。

5. 扩容后再次查看 test 表的状态。

   .. code:: sql

      -- 查看 test 表的数据分布
      SELECT gp_segment_id, COUNT(*) FROM test GROUP BY gp_segment_id;
      -- 查看元数据状态
      SELECT * FROM gp_distribution_policy;
      SELECT * FROM gp_segment_configuration;
