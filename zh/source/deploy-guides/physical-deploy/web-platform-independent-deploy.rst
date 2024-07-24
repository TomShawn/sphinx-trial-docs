在已有 HashData Lightning 集群上安装 Web Platform
==================================================

如果你有一套通过手动方法部署好的 HashData Lightning 集群，并希望在集群中使用 Web Platform 的监控面板等功能，你可以在集群上独立安装 Web Platform。

适用版本：HashData Lightning v1.5.4 及以上。

第 1 步：安装 Web Platform 组件
--------------------------------

1. 通过 HashData 技术支持人员获取 ``web-platform`` 安装包。假设安装包名为 ``perfmon_cbuiserver-centos7-x86_64-1.6.0-79727.tar.gz``。
2. 解压安装包：

   .. code-block:: bash

      tar -zxvf perfmon_cbuiserver-centos7-x86_64-1.6.0-79727.tar.gz

3. 执行安装命令：

   .. code-block:: bash

      # 如果不存在 GPHOME，需设置。
      echo $GPHOME

      cd perfmon_cbuiserver

      # wp_install.sh 会把之前安装的 web-platform 相关的东西备份，并拷贝新的包到 gphome 目录下。
      ./wp_install.sh

第 2 步：安装 gpperfmon 组件
------------------------------

1. 检查 ``gpperfmon`` 数据库是否存在。

.. code-block:: shell

   psql -l

2. 如果 ``psql -l`` 结果中有 ``gpperfmon``\ ，则需要删除原有的 ``gpperfmon``。如果列表中没有，则跳过本步，直接执行下一步。

   .. code-block:: bash

      gpconfig -c perfmon.enable -v off
      gpstop -ari
      dropdb gpperfmon

3. 安装 ``gpperfmon_install``。

   .. code-block:: bash

      # 以下 5432 是 PGPORT 端口，123456 是密码
      gpperfmon_install --port 5432 --enable --password 123456
      gpstop -ari

   .. tip:: 

      -  若提示类似于 ``gpperfmon.conf already exists /data202407101158339957/master/gpseg-1/gpperfmon/conf/gpperfmon.conf`` 的报错，则删除该文件重试。
      -  若提示 ``error on command: createdb gpperfmon``\ ，则执行 ``dropdb gpperfmon``\ 。

4. 重启 ``cbuiserver``。

   .. code-block:: bash

      pkill cbuiserver
      /user/local/cloudberry-db/cbuiserver &

Web Platform 安装常见问题说明
-----------------------------

若出现以下页面，请检查是否安装了 ``gpperfmon``\ ， 以及 ``gpperfmon`` 是否安装成功。

.. image:: /images/web-platform-deploy-gpperfmon.png

1. 检查 ``gpperfmon`` 数据库是否已安装。

   .. code-block:: shell

      psql -l

2. 查看相关进程是否正常运行。

   .. code-block:: shell

      ps -ef | grep gpmmon
      ps -ef | grep gpsmon

3. 查看 ``perfmon.enable`` 参数的值是否为 ``on``\ 。

   .. code-block:: shell

      gpconfig -s perfmon.enable

若日志中提示如下所示的错误类型，则检查 ``gpperfmon`` 安装过程是否出错。

.. code-block:: 

   failed to initialize database, got error failed to connect to host=10.13.9.62 user=gpmon database=gpperfmon: server error (FATAL: no pg_hba.conf entry for host "10.13.9.62", user "gpmon", database "gpperfmon", no encryption (SQLSTATE 28000))