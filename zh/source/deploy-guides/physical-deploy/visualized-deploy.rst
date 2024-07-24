可视化部署
==========

HashData Lightning Web Platform 是一个部署和管理 HashData Lightning 集群的控制台工具，提供简单直观的用户界面。相较于手动部署的方式，可视化部署更为简单直观，你只需要按照界面提示进行操作即可，无需理解复杂的命令和配置文件，从而使部署更加高效。你可以使用 HashData Lightning Web Platform 部署 HashData Lightning。

部署集群
--------

本节介绍如何使用 HashData Lightning Web Platform 在物理机上部署 HashData Lightning。

如果你已有一套通过手动方式部署的 HashData Lightning 集群（v1.5.4 及以上版本），并希望在集群中使用 Web Platform 的监控面板等功能，可以参考\ :ref:`deploy-guides/physical-deploy/web-platform-independent-deploy:在已有 hashdata lightning 集群上安装 web platform`\ 。

软硬件配置需求
~~~~~~~~~~~~~~

HashData Lightning 支持在以下操作系统及 CPU 架构上部署，详情见下表：

.. list-table::
   :header-rows: 1
   :align: left

   * - 操作系统
     - 支持的 CPU 架构
   * - RHEL/CentOS 7.6+
     - x86_64 和 AArch64
   * - Kylin V10 SP1 或 SP2
     - x86_64 和 AArch64

安装步骤
~~~~~~~~

在服务端安装 HashData Lightning，包括 4 个步骤：准备工作、安装数据库 RPM 包、数据库部署、安装后设置。

第 1 步：准备工作
^^^^^^^^^^^^^^^^^

1. 在进行安装操作前，先查看并确认服务器基本信息，以便更好地规划部署集群。

   .. list-table::
      :header-rows: 1
      :align: left

      * - **步骤**
        - **执行的命令**
        - **用途**
      * - 1
        - ``free -h``
        - 查看操作系统内存信息。
      * - 2
        - ``df -h``
        - 查看磁盘空间。
      * - 3
        - ``lscpu``
        - 查看 CPU 数量信息。
      * - 4
        - ``cat/etc/system-release``
        - 查看操作系统版本信息。
      * - 5
        - ``uname -a``
        - 以如下次序输出所有内核信息（其中若 ``-p`` 和 ``-i`` 的探测结果不可知则被省略）：内核名称、网络节点上的主机名、内核发行号、内核版本、主机的硬件架构名称、处理器类型、硬件平台、操作系统名称。
      * - 6
        - ``tail -11 /proc/cpuinfo``
        - 查看 CPU 信息。
      * - 7
        - ``rpm -iq cloudberry-db``
        - 检查之前是否安装过 HashData Lightning 软件包。详情参见本文\ :ref:`deploy-guides/physical-deploy/visualized-deploy:故障排查`\ 部分。

2. 在每台节点服务器上创建 ``gpadmin`` 管理用户。参考以下示例，创建用户组和用户名 ``gpadmin``\ ，将用户组和用户名的标识号设为 ``520``\ ，创建并指定主目录 ``/home/gpadmin/``\ 。

   .. code:: bash

      groupadd -g 520 gpadmin  # 添加用户组 gpadmin
      useradd -g 520 -u 520 -m -d /home/gpadmin/ -s /bin/bash gpadmin  # 添加用户名 gpadmin 并创建主目录。
      passwd gpadmin  # 为 gpadmin 设置密码。

3. 在准备安装 HashData Lightning 的机器上进行如下配置：

   1. 关闭防火墙，如果不关闭防火墙则无法使用可视化部署：

      .. code:: shell

         sudo systemctl stop firewalld.service
         sudo systemctl disable firewalld.service

   2. 关闭 SELinux。你可以编辑 ``/etc/selinux/config``\ ，将 SELINUX 的值设为 ``disabled``\ ：

      .. code:: shell

         sudo sed s/^SELINUX=.*$/SELINUX=disabled/ -i /etc/selinux/config
         sudo setenforce 0

4. 参考\ :ref:`设置系统参数 <deploy-guides/physical-deploy/manual-deploy/prepare-to-deploy:设置系统参数>`，在每台服务器上设置系统参数。

5. 永久禁用 IPv6:

   要永久禁用 IPv6，您需要编辑 ``/etc/sysctl.conf`` 文件（或在 ``/etc/sysctl.d/`` 目录中创建一个新的配置文件），然后添加以下行：

   ::

      net.ipv6.conf.all.disable_ipv6 = 1
      net.ipv6.conf.default.disable_ipv6 = 1

   之后，运行 ``sudo sysctl -p`` 来应用更改，或重启您的系统。

6. 为服务器之间配置免密。在 ``gpadmin`` 账户下开启对本机及其他节点的免密登录操作。检查命令为 ``ssh ip``\ ，例如 ``ssh 192.168.48.58``\ ，如果设置成功则不用输密码。

7. 为 ``gpadmin`` 用户开启免密执行 ``sudo`` 的权限。

   .. note:: 在执行 ``su - gpadmin`` 切换到 ``gpadmin`` 用户后，如果无法执行 ``ifconfig`` 命令，你需要先配置 ``ifconfig`` 的环境变量。假设 ``ifconfig`` 文件在 ``/usr/sbin`` 目录下，你需要在 ``~/.bashrc`` 文件中添加一行 ``export PATH=/usr/sbin:$PATH``\ ，再执行 ``source ~/.bashrc`` 使其生效。

8. 复制 RPM 包。将 RPM 包复制到要安装 HashData Lightning 的每台节点服务器上。

第 2 步：安装数据库 RPM 包
^^^^^^^^^^^^^^^^^^^^^^^^^^

在每一台节点机器上，执行下述命令安装数据库 RPM 包，系统依赖库会自动安装。示例如下：

.. code:: shell

   cd /home/gpadmin
   sudo yum install hashdata-lightning-1.5.4-1.el7.x86_64-75889-release.rpm
   sudo chown -R gpadmin:gpadmin /usr/local
   sudo chown -R gpadmin:gpadmin /usr/local/cloudberry*

.. note:: 你需要将文件名 ``hashdata-lightning-1.5.4-1.el7.x86_64-75889-release.rpm`` 替换成实际的 RPM 包名。

第 3 步：可视化自动部署数据库
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

使用图形化界面来部署 HashData Lightning。图形化部署工具默认访问数据库节点服务器的 ``7788`` 端口。安装完成之后，所有节点的 ``7788`` 端口会默认打开。

访问部署界面
''''''''''''

1. 访问图形化部署界面。打开浏览器（不支持 IE 系列浏览器）访问以下链接，即可打开图形化部署界面。其中 ``<IP>`` 为 任意节点服务器的 IP 地址：

   ::

      http://<IP>:7788/

2. 在界面中填写超级用户密码，以登录部署节点，如下图所示。要查看超级用户密码，可执行 ``find / -path "*/cloudberry-*/cloudberryUI/resources/users.json" 2>/dev/null | xargs cat | grep -A1 '"username": "gpmon",'`` 命令。

   默认安装目录是 ``/usr/local``\ ，可以通过命令\ ``cat /usr/local/cloudberry-db/cloudberryUI/resources/users.json`` 查看 ``gpmon`` 账户的用户名和密码。

   .. image:: /images/web-platform-deploy-login.png

成功登录后，首先你需要选择单节点部署或者多节点部署，即在单个节点服务器上部署 HashData Lightning，还是在多台节点服务器上部署。

.. note:: 你不能使用同一个 IP 地址和同一个用户同时登录，否则会提示报错。

单节点部署
''''''''''

单节点部署模式主要用于研发测试场景，不支持高可用功能，不适用于生产环境。

单节点部署模式为非分布式部署，所有服务都部署在同一台物理机上，只需要一个节点。部署方法如下：

1. 登录后，选择\ **在本机初始化一个单节点数据库（约 2 分钟）**\ ，然后点击\ **下一步**\ 。

2. 设置单节点的配置项。示例如下图：

   .. image:: /images/web-platform-deploy-single-node.png

3. 点击\ **执行部署**\ ，等待部署完成。

   部署完成后，会显示以下页面：

   .. image:: /images/web-platform-welcome.png

多节点部署
''''''''''

1. 登录后，选择\ **添加多个节点并初始化数据集群**\ ，然后点击\ **下一步**\ 。

2. 添加节点。你可以选择“一键添加”功能快速添加节点，也可以选择手动添加节点。

   -  快速添加节点：部署工具会自动检测已安装 RPM 包的所有节点，并在界面左上角显示\ **一键添加**\ 。点击\ **一键添加**\ ，部署工具会自动添加这些节点。

   -  手动添加节点：你也可以在文本框中输入待添加节点的主机名或者 IP 地址，例如 ``i-uv2qw6ad`` 或者 ``192.168.176.29``\ ，再点击\ **添加节点**\ 按钮。如下图所示：

      .. note:: 

         -  确保你所添加的节点可被找到，并且不重复。否则部署工具会在界面顶部报错，提示未找到主机名，或者待添加的节点已存在。

         -  在多节点部署模式下，如果你只添加了一个节点，那么\ **下一步**\ 按钮将不可用。

3. 为集群进行以下配置。完成确认配置后，点击\ **下一步**\ 。

   -  为主节点配置 standby 节点，为数据节点配置 mirror 节点。

   -  **数据镜像**\ 决定了集群数据节点是否包含备份镜像，建议在生产环境中启用，以确保集群高可用。

   -  修改 ``gpmon`` 密码。

   .. image:: /images/web-platform-deploy-multi.png

4. 设置存储路径。注意，当前 HashData Lightning 版本要求所有节点的挂载点必须相同，否则会出现错误提示信息。设置完成后，点击\ **下一步**\ 。

5. 执行部署。检查并确认之前步骤进行的配置，确认无误后，点击右下角的\ **执行部署**\ 。 此时系统会自动部署集群，并显示当前进度。当所有的步骤都执行完成后，集群部署成功。

   集群部署成功后，跳转到完成页面。注意，如果已部署成功，再次登录会提示是否重新部署。

6. 执行 ``psql`` 验证数据库是否正常运行，如果是，则可以继续进行安装后设置。如果提示 ``psql`` 命令不存在，可以尝试重新登录该服务器，进入 ``gpadmin`` 用户再次执行 ``psql``\ 。

第 4 步：安装后设置
^^^^^^^^^^^^^^^^^^^

-  以 ``gpadmin`` 用户执行以下命令：

   .. code:: shell

      sudo chown -R gpadmin:gpadmin /usr/local/cloudberry-db/cloudberryUI/resources

-  你可以通过以下命令分别完成 HashData Lightning 的启动、停止、重启以及状态查看。

   .. list-table::
      :header-rows: 1
      :align: left
      :widths: 8 18

      * - 命令
        - 用途
      * - ``gpstop -a``
        - 停止集群。在此模式下，如果有会话连接，等待会话关闭后再停止集群。
      * - ``gpstop -af``
        - 快速强制关闭集群。
      * - ``gpstop -ar``
        - 重启集群。等待当前正在执行的 SQL 语句结束。在此模式下，如果有会话连接，等待会话关闭后再停止集群。
      * - ``gpstate -s``
        - 查看集群当前状态。


故障排查
--------

-  通过 ``http://<IP>:7788/`` 登录图形界面后，如果提示集群节点没有连接 ``Got a 404 error Response status``\ ，或者卡在收集主机信息的环节，建议确保各节点之间的 SSH 互信已配置好，并执行以下命令重启节点：

   .. image:: /images/web-platform-deploy-collecting-info.png

   .. code:: shell

      su - gpadmin
      cd /usr/local/cloudberry-db
      sudo pkill cbuiserver
      ./cbuiserver

-  如果节点机器在此前进行过可视化部署，你希望在这些机器上重新安装 RPM 包，请在安装前，在每台机器上先执行 ``sudo pkill cbuiserver``\ ，再清空 ``/usr/local/cloudberry-db`` 目录。

   1. 在每台机器上卸载之前的 RPM 包。
   
      .. code-block:: bash

         # 检查是否安装过 HashData Lightning 软件包。
         # 如果有，会返回 <安装包名>，例如 cloudberry-db-1.6.0-1.el8.x86_64。
         rpm -iq cloudberry-db

         # 执行命令删除软件包
         sudo yum remove -y cloudberry-db-1.6.0-1.el8.x86_64

   2. 在每台机器上，执行以下命令清理环境。
   
   .. code-block:: bash

      sudo pkill postgres
      sudo rm -rf /data*
      rm -rf /tmp/.s*
      sudo pkill cbuiserver



后续操作
----------

通过可视化方法部署好一套 HashData Lightning 集群后，你可以通过 Web Platform 界面进行如下操作：

-  :ref:`operate-with-data/view-and-operate-db-objects-using-web-platform:使用 web platform 查看和操作数据库对象`
-  :ref:`components/web-platform:在网页编辑器中执行 sql 语句`
-  :ref:`manage-system/web-platform-monitoring/web-platform-monitoring-index:使用 web platform 查看集群监控数据`