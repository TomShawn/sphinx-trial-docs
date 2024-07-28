.. raw:: latex

   \newpage

使用 Web Platform 查看和操作数据库对象
======================================

HashData Lightning Web Platform （下称 Web Platform）是一个部署和管理 HashData Lightning 集群的控制台工具，提供简单直观的用户界面，帮助用户通过界面操作进行集群操作。你可以使用 Web Platform 查看和操作数据库对象。

**工作表**\ 是 Web Platform 中的界面组件，它类似于终端会话或工作窗口，提供了灵活、高效的交互界面，用于与数据库进行交互。在一个工作表中，用户可以查看数据库对象、使用内置的 SQL 编辑器编写和执行 SQL 语句等。每个工作表独立运行，不同的工作表可以用于不同的数据库操作或查询任务。

.. attention::

   对于当前版本，你有两种方式访问 Web Platform 面板：
   
   -  如果你的 HashData Lightning 集群是通过\ :ref:`可视化方法部署 <deploy-guides/physical-deploy/visualized-deploy:可视化部署>`\ 的，Web Platform 面板已经内置在集群中，你只需在浏览器里访问 ``http://<IP>:7788/`` 即可，其中 ``<IP>`` 为任一节点的 IP 地址。

   -  如果你的 HashData Lightning 集群是通过\ :ref:`手动方法部署 <deploy-guides/physical-deploy/manual-deploy/deploy-multi-nodes:部署多计算节点>`\ 的，你需要先单独安装 Web Platform 组件，参考\ :ref:`components/web-platform:在已有 hashdata lightning 集群上安装 web platform`\ 。安装后，再在浏览器里访问 ``http://<IP>:7788/`` 以访问 Web Platform 面板。

访问工作表
----------

要访问\ **工作表**\ 页面，你需要：

1. 在浏览器中通过 ``http://<集群节点 IP>:7788/`` 访问 Web Platform 面板。
2. 在左侧导航点击\ **工作表**\ ，即可进入该页面。

操作工作表
----------

**在操作工作表前，你需要先开启远程连接，以连接到目标数据库**\ 。即在安装部署时，勾选“允许远程连接数据库”，否则无法连接到数据库并使用工作表进行数据操作。

查看工作表列表
~~~~~~~~~~~~~~

你可以查看创建的工作表列表，并按照最近修改时间进行排序。

.. image:: /images/web-platform-worksheets.png

创建工作表
~~~~~~~~~~

要创建一个工作表，点击页面右上角的\ **创建工作表**\ 。

查看工作表详情
~~~~~~~~~~~~~~

点击工作表列表中的标题，即跳转到对应工作表的详情页面。

一个工作表目前包括两个主要部分，在左侧展示数据库对象的树状目录，在右侧展示 SQL 查询编辑器。

.. image:: /images/web-platform-sql-editor.png

查看数据库中的表对象
~~~~~~~~~~~~~~~~~~~~

查看数据库层级列表
^^^^^^^^^^^^^^^^^^

1. 打开目标工作表的详情界面。
2. 在左侧目录中，点击 **Database** 以切换至该标签，以查看数据库对象。
3. 点击某个特定数据库，会自动展开该数据库下的所有 Schema。
4. 点击某个特定数据库下特定的 Schema，列表会展示该 Schema 下的表对象（默认显示 1000 个，可通过搜索功能查找其他表）。
5. 选中某张表，会显示该表的列结构信息。

搜索表对象
^^^^^^^^^^

1. 打开目标工作表的详情界面。
2. 在左侧目录中，点击 **Database** 以切换至该标签，此时左侧会显示数据库下来选项菜单和搜索框。
3. 在下拉菜单中选择目标数据库，并在搜索栏中输入名字，即可以模糊匹配该数据库中对应的表对象。

在网页编辑器中执行 SQL 语句
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Web Platform 在工作表中提供了 SQL 查询编辑器。在选择数据库后，你可以在编辑器中编写 SQL 语句，并执行 SQL 语句。

按钮图标说明
^^^^^^^^^^^^

格式化 SQL 语句
^^^^^^^^^^^^^^^

你可以在编辑区对输入的 SQL 语句进行格式化操作，点击右上角的 |icon1| 图标：

搜索和替换
^^^^^^^^^^

在编辑区写 SQL 语句时，要对语句内容进行搜索和替换，可点击右上角的 |icon2| 图标，输入搜索字符串进行搜索：

在搜索区域，你可以点击相应的按钮进行以下操作：

-  查找下一个字符
-  区分大小写
-  字符串替换
-  替换下一个
-  替换所有

执行 SQL 语句
^^^^^^^^^^^^^

-  点击 |icon3| 图标，等待 SQL 语句执行完成，显示执行结果。
-  对于正在执行中的 SQL，即使关闭 tab 后重新打开，仍然显示正在执行的状态。
-  执行结果默认显示 1000 条。点击 |icon4| 按钮，将以 CSV 文件格式导出所有的执行结果：
-  如果执行结果报错，会显示详细信息。
-  支持多条语句同时执行，显示最后一条语句的执行结果。

登出和语言设置
--------------

-  登出：点击页面右上角的用户头像 |icon5|，选择退出登录。
-  切换语言：点击页面右上角语言切换按钮 |icon6|，目前支持中英文切换。

.. |icon1| image:: /images/icons/web-platform-formatting.png
.. |icon2| image:: /images/icons/web-platform-search-replace.png
.. |icon3| image:: /images/icons/web-platform-execute.png
.. |icon4| image:: /images/icons/web-platform-download-result.png
.. |icon5| image:: /images/icons/web-platform-logout.png
.. |icon6| image:: /images/icons/web-platform-languages.png
