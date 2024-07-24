使用 Web Platform 查看集群监控数据
===================================

:ref:`HashData Lightning Web Platform <components/web-platform:hashdata lightning web platform 使用说明>` 是一个部署和管理 HashData Lightning 集群的控制台工具，提供简单直观的用户界面，为用户提供集群以及数据库的监控面板和数据，帮助用户更好地查看集群和数据库的当前状况：

-  :ref:`manage-system/web-platform-monitoring/web-platform-view-cluster-overview:查看集群概览信息`
-  :ref:`manage-system/web-platform-monitoring/web-platform-view-cluster-status:查看集群运行详情`
-  :ref:`manage-system/web-platform-monitoring/web-platform-view-db-object-info:查看数据库对象信息`
-  :ref:`manage-system/web-platform-monitoring/web-platform-sql-monitor-info:查看 sql 监控信息`
-  :ref:`manage-system/web-platform-monitoring/web-platform-storage-overview:查看存储概览信息`

.. attention::

   对于当前版本，你有两种方式访问 Web Platform 面板：
   
   -  如果你的 HashData Lightning 集群是通过\ :ref:`可视化方法部署 <deploy-guides/physical-deploy/visualized-deploy:可视化部署>`\ 的，Web Platform 面板已经内置在集群中，你只需在浏览器里访问 ``http://<IP>:7788/`` 即可，其中 ``<IP>`` 为任一节点的 IP 地址。

   -  如果你的 HashData Lightning 集群是通过\ :ref:`手动方法部署 <deploy-guides/physical-deploy/manual-deploy/deploy-multi-nodes:部署多计算节点>`\ 的，你需要先单独安装 Web Platform 组件，参考\ :ref:`components/web-platform:在已有 hashdata lightning 集群上安装 web platform`\ 。安装后，再在浏览器里访问 ``http://<IP>:7788/`` 以访问 Web Platform 面板。


.. toctree::
   :maxdepth: 0
   :titlesonly:
   :hidden:

   web-platform-view-cluster-overview
   web-platform-view-cluster-status
   web-platform-view-db-object-info
   web-platform-sql-monitor-info
   web-platform-storage-overview