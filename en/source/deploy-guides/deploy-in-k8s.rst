在 Kubernetes 上部署
====================

容器化部署架构
--------------

你可以在 Kubernetes 上基于容器化引擎技术部署 HashData Lightning。HashData Lightning 支持在不同的容器化平台上部署，包括青云、道客和 Amazon 云服务等。本文档介绍如何在 Kubernetes 上部署 HashData Lightning 组件和节点，容器化部署的适用场景、使用限制以及相关问题。

在传统物理机上部署数据库，常常伴随着高昂的运维成本，同时高可用性和扩展性也是主要痛点。容器化部署方案可以很好地解决传统物理机部署的痛点。HashData Lightning 适配 Kubernetes 容器化部署，相较于物理机部署的数据库，容器化版本的云莓数据库独享以下特性：

-  Master/Segment 节点无主从架构，通过 Kubernetes 容器服务实现各节点高可用功能。
-  FTS 集群独立部署，用于维护数据库集群的元数据信息。
-  ETCD 集群独立部署，用于存放数据库集群状态的元数据信息。
-  Operator 集群独立部署，用于管理各个数据库节点的容器启停和故障恢复。
-  通过共享存储挂载数据库节点的底层数据盘，通过共享存储多副本以保证数据可靠性，并支持数据异地灾备。

HashData Lightning 容器化部署的架构如下图所示：

.. image:: /images/k8s-deploy-architecture.png


典型使用场景
------------

-  **云原生部署场景：** 在 SaaS 应用场景中，在传统物理机上部署数据库不是理想的选择。相较于基于虚拟机部署模式，更轻量级的 Kubernetes 容器化技术是目前业界的主流部署方案。基于 Kubernetes 容器引擎技术部署 HashData Lightning ，可以充分利用云上的弹性能力、丰富的存储类型，支持降低 SaaS 业务成本、动态扩容、高可靠性等需求，并可以在 SaaS 应用场景下给用户提供不同的多租户隔离模式。
-  **私有化部署场景：** 在私有化应用场景中，使用 HashData Lightning 容器化版本部署的用户，可以充分享受 Kubernetes 容器化引擎技术带来的弹性伸缩和分布式部署带来的优势，实现数据库的快速部署、按需伸缩、异常自动恢复，支持异地存储备份等，大幅减少用户对数据库日常运维的投入成本。
-  **开源 & PoC 测试部署场景：** 在开源或 PoC 测试场景中，使用 HashData Lightning 容器化版本部署的用户，可以高效快速地搭建数据库最小化部署场景，用于测试或应用原型验证。并可以进一步根据验证测试的不同场景快速高效地对计算或存储节点进行扩缩容，用于匹配不同测试或同一个测试不同阶段对数据库计算或存储能力的不同需求。在测试或原型验证过程中遇到数据库节点宕机时，可自动恢复，无需用户手动介入。

推荐的部署配置
--------------

部署组件列表
~~~~~~~~~~~~

.. table:: 
   :align: left

   +------------+------------------+------------------------------------+
   | 组件缩写   | 子组件名称       | 组件说明                           |
   +============+==================+====================================+
   | 计算集群   | Master 节点      | 保存元数据，负责管理会话，SQL      |
   |            |                  | 解析及执行计 划、分发 SQL，并返回  |
   |            |                  | SQL 执行结果。                     |
   +            +------------------+------------------------------------+
   |            | Segment 计算节点 | 保存用户数据，以及 SQL 执行。      |
   +            +------------------+------------------------------------+
   |            | FTS 节点         | 维护数据库集群元数据               |
   |            |                  | 信息，实现数据库节点故障自动恢复。 |
   +            +------------------+------------------------------------+
   |            | ETCD 元数据节点  | 保存数据库集群元数据信息。         |
   +------------+------------------+------------------------------------+
   | 容器化服务 | Operator 组件    | 实现数据库                         |
   |            |                  | 容器化节点管理，数据盘挂载等功能。 |
   +            +------------------+------------------------------------+
   |            | 容器镜像仓库     | 用于存放云莓数据库所需的镜像文件。 |
   +            +------------------+------------------------------------+
   |            | CRD 配置         | CRD (Custom Resource Definition)   |
   |            |                  | 配置，用于自                       |
   |            |                  | 定义不同数据库节点的规格配置信息。 |
   +            +------------------+------------------------------------+
   |            | 存储层           | 挂载共享存储，例如共享块存储，NFS  |
   |            |                  | 等。                               |
   +------------+------------------+------------------------------------+

容器节点数
~~~~~~~~~~

.. table:: 
   :align: left

   +----------------+----------------+----------------+----------------+
   | 组件           | 最小化部       | 生产部署容器   | 备注           |
   |                | 署容器节点数量 | 的建议节点数量 |                |
   +================+================+================+================+
   | Master 节点    | 1              | 1              | Master         |
   |                |                |                | 节点暂时只     |
   |                |                |                | 支持单节点部署 |
   |                |                |                | ，高可用功能由 |
   |                |                |                | Kubernetes     |
   |                |                |                | 机制原生支持。 |
   +----------------+----------------+----------------+----------------+
   | Segment        | 1              | 3              | Segment        |
   | 计算节点       |                |                | 节             |
   |                |                |                | 点高可用功能由 |
   |                |                |                | Kubernetes     |
   |                |                |                | 机制原生支持， |
   |                |                |                | 支持横向扩容。 |
   +----------------+----------------+----------------+----------------+
   | FTS 节点       | 1              | 2              | FTS            |
   |                |                |                | 集群支持多节点 |
   |                |                |                | 部署，节点高可 |
   |                |                |                | 用功能由应用和 |
   |                |                |                | Kubernetes     |
   |                |                |                | 机制原生支持， |
   |                |                |                | 支持横向扩容。 |
   +----------------+----------------+----------------+----------------+
   | ETCD           | 2              | 3              | ETCD           |
   | 元数据节点     |                |                | 集群支持多节点 |
   |                |                |                | 部署，节点高可 |
   |                |                |                | 用功能由应用和 |
   |                |                |                | Kubernetes     |
   |                |                |                | 机制原生支持， |
   |                |                |                | 支持横向扩容。 |
   +----------------+----------------+----------------+----------------+
   | Operator 组件  | 1              | 2              | Operator       |
   |                |                |                | 集群支持多节点 |
   |                |                |                | 部署，节点高可 |
   |                |                |                | 用功能由应用和 |
   |                |                |                | Kubernetes     |
   |                |                |                | 机制原生支持， |
   |                |                |                | 支持横向扩容。 |
   +----------------+----------------+----------------+----------------+

如需指定容器节点实例数量，可以通过 CRD 配置文件中相关服务的 ``replicas`` 项进行配置。以下示例配置 Segment 计算节点为 3 个实例：

.. code:: yaml

   segments:
       replicas: 3

节点配置规格
~~~~~~~~~~~~

若要自定义容器的规格配置，你可以在 Kubernetes 容器化部署环境中通过 CRD 配置文件进行配置，并同时你可以在容器运行时动态调整配置。

推荐参考下表提供的规格来配置 HashData Lightning 节点：

.. table:: 
   :align: left

   +--------------+--------------+-------+--------------+--------------+
   | 节点类型     | CPU          | 内存  | 网络         | 数据盘       |
   +==============+==============+=======+==============+==============+
   | Ma           | 2 \* Intel   | 512GB | 10Gbps       | 4T SAS HDD   |
   | ster/Segment | Silver 5220R |       | 光交换以太网 |              |
   | 节点         | 24 Core \* 2 |       |              |              |
   |              | 物理线       |       |              |              |
   |              | 程（双线程为 |       |              |              |
   |              | 96 Core）    |       |              |              |
   +--------------+--------------+-------+--------------+--------------+
   | FTS/E        | Intel Silver | 4GB   | 10Gbps       | 100G SAS HDD |
   | TCD/Operator | 5220R 2 Core |       | 光交换以太网 |              |
   | 节点         | 物理线程     |       |              |              |
   +--------------+--------------+-------+--------------+--------------+

你可以通过 CRD 配置文件中的 ``resources`` 配置项指定容器的规格存储配置，其中 ``limits`` 配置项为资源使用上限，\ ``requests`` 配置项为资源使用下限。

.. code:: yaml

   resources:
     limits:
       cpu: "16"
       memory: 128Gi
     requests:
       cpu: "2"
       memory: 4Gi

存储配置
~~~~~~~~

在高负载下，为避免数据盘影响操作系统正常的 I/O 响应，云莓数据库的系统盘和数据盘会在容器启动时自动挂载到不同的存储介质。

-  云莓数据库容器化部署默认使用宿主机的本地磁盘为系统盘，用于保存容器的系统文件和日志，磁盘使用量一般较小。建议保证 Kubernetes 宿主机预留部分的磁盘容量（推荐预留 100 GB）给云莓数据库节点作为系统盘使用。

-  云莓数据库容器化部署默认将共享存储作为节点的数据盘挂载到 ``/data0`` 数据盘目录中。你可以通过 CRD 配置文件中的 ``storage`` 配置项指定共享存储配置。以道客环境部署云莓数据库为例，\ ``hwameistor-storage-lvm-hdd`` 为道客平台在 Kubernetes 环境中预定义提供的共享存储，存储大小指定为 100 GB：

   .. code:: yaml

      resources:
        requests:
          storage: 100Gi
      storageClassName: hwameistor-storage-lvm-hdd

数据交换网络配置
~~~~~~~~~~~~~~~~

-  云莓数据库的业务数据传输使用数据交换网络，对于网络性能和吞吐性能要求较高。云莓数据库基于 Kubernetes 容器化生产环境，建议所在数据中心的网络带宽不低于 100 GB。
-  Kubernetes 管理控制台与数据库主机应当在数据交换网络中连通。如果管理控制台与数据库主机的网络访问关系中有防火墙设备，应当确保 TCP 空闲连接能够保持 12 小时以上。
-  数据库主机之间，以及 Kubernetes 管理控制台主机之间，应当在数据交换网络中连通，且不应当限制 TCP 空闲连接时间。
-  数据库客户端、访问数据库的应用程序应当与数据库主节点在数据交换网络中连通。 应当确保 TCP 空闲连接能够保持 12 小时以上。

所需客户端工具
~~~~~~~~~~~~~~

容器化部署 HashData Lightning 前，确保下列客户端工具已安装：

.. table:: 
   :align: left

   +------------+--------------------------------------------------------+
   | 客户端工具 | 描述                                                   |
   +============+========================================================+
   | kubectl    | kubectl 为 kubernetes 命令行工具，方便用户管理         |
   |            | Kubernetes 容器化集群各种功能。                        |
   +------------+--------------------------------------------------------+
   | helm       | helm 用于管理 Kubernetes 部署应用程序, 并通过 Helm     |
   |            | Charts 定义、安装和升级 Kubernetes 应用程序。          |
   +------------+--------------------------------------------------------+
   | etcdctl    | etcdctl 为 etcd 服务命令行客户端，提供管理命令用于对   |
   |            | ETCD 集群进行服务测试和修改数据库内容。注意，确保      |
   |            | etcdctl 的版本不低于 3.3.25。                          |
   +------------+--------------------------------------------------------+

部署流程
--------

HashData Lightning 支持在不同的容器化平台上部署，包括青云，道客和 Amazon 云服务等。以下内容以在道客平台上部署标准商业化发布版本为例。

前置准备
~~~~~~~~

在部署数据库前，确保你的 Kubernetes 容器化环境中已安装 Operator 组件和 ETCD 元数据集群。

第 1 步：准备数据库容器镜像
~~~~~~~~~~~~~~~~~~~~~~~~~~~

确保以下部署镜像和配置包已经上传至道客镜像仓库中，上传地址为 ``release.daocloud.io``\ 。

.. table:: 
    :align: left

    +-------------------------------+------------------------------------------------------------------------------------------------------------+
    | 组件名                        | 版本镜像名                                                                                                 |
    +===============================+============================================================================================================+
    | HashData Lightning 数据库镜像 | release.daocloud.io/lvyiwei/cbdb:devel-devtoolset-10-cbdb-docker-k8s-centos-20230424-1X-STABLE-K8S-RELEASE |
    +-------------------------------+------------------------------------------------------------------------------------------------------------+
    | Operator 组件镜像             | release.daocloud.io/lvyiwei/operator:devel-devtoolset-10-operator-docker-k8s-centos-20230412-test          |
    +-------------------------------+------------------------------------------------------------------------------------------------------------+
    | ETCD 组件镜像                 | release.daocloud.io/lvyiwei/etcd:v3.5.6                                                                    |
    |                               | 建议使用 3.3.25 以上的版本                                                                                 |
    +-------------------------------+------------------------------------------------------------------------------------------------------------+
    | 容器化服务配置文件            | release.daocloud.io/lvyiwei/computing                                                                      |
    +-------------------------------+------------------------------------------------------------------------------------------------------------+

第 2 步：安装 Kubernetes 容器化服务
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

你需要使用 Helm Chart 来将所有的 Kubernetes 相关配置文件统一打包下载并部署到 Kubernetes 应用容器化环境中。

1. 在 Helm 客户端中，使用以下命令下载并解压 HashData Lightning 容器化服务的所有配置文件：

   .. code:: shell

      helm pull oci://release.daocloud.io/lvyiwei/computing --version 0.1.0
      tar xvf computing-cbdb-0.1.0.tgz
      cd computing

2. 编辑文件夹中的 ``.yaml`` 配置文件，参考以下示例，配置 Operator 组件和 ETCD 元数据服务的 Helm Chart 配置信息：

   .. code:: yaml

      replicas: 1

      image:
        repository: release.daocloud.io/lvyiwei
        tag: "devel-devtoolset-10-operator-docker-k8s-centos-20230412-test"
      etcd:
        version: "v3.5.6"

      dnsService: kube-system/coredns
      storage:
        name: hwameistor-storage-lvm-hdd

3. 在 Helm 客户端中，执行以下命令安装 Operator 组件和 ETCD 服务。完成后，Operator 组件和 ETCD 元数据服务集群会自动拉起并开始服务：

   .. code:: shell

      helm install hdop -n hashdata --create-namespace . --debug

第 3 步：创建数据库计算集群
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. 创建计算集群的 CRD 配置文件 ``computing-cluster.yaml``\ 。以下为 HashData Lightning 的标准示例配置，你可以根据实际需求自定义相关的节点规格配置：

   .. code:: yaml

      # computing-cluster.yaml
      apiVersion: computing.hashdata.xyz/v1alpha1
      kind: ComputingCluster
      metadata:
        name: cbdb
        namespace: hashdata
        annotations:
          computing.hashdata.xyz/dbtype: "cbdb"
      spec:
        version: "devel-devtoolset-10-cbdb-docker-k8s-centos-20230424-1X-STABLE-K8S-RELEASE"
        master:
          podTemplate:
            spec:
              affinity: {}
              containers:
              - name: cbdb-master
                resources:
                  limits:
                    cpu: "2"
                    memory: 2Gi
                  requests:
                    cpu: "1"
                    memory: 2Gi
          volumeClaimTemplate:
            apiVersion: v1
            kind: PersistentVolumeClaim
            metadata:
              name: persistent-storage
            spec:
              accessModes:
              - ReadWriteOnce
              resources:
                requests:
                  storage: 10Gi
              storageClassName: hwameistor-storage-lvm-hdd
        segments:
          replicas: 3
          podTemplate:
            spec:
              containers:
              - name: cbdb-segment
                resources:
                  limits:
                    cpu: "2"
                    memory: 2Gi
                  requests:
                    cpu: "1"
                    memory: 2Gi
              affinity: {}
          volumeClaimTemplate:
            apiVersion: v1
            kind: PersistentVolumeClaim
            metadata:
              name: persistent-storage
            spec:
              accessModes:
              - ReadWriteOnce
              resources:
                requests:
                  storage: 10Gi
              storageClassName: hwameistor-storage-lvm-hdd
        ftss:
          replicas: 1
          podTemplate:
            spec:
              affinity: {}
              containers:
              - name: fts
                resources:
                  limits:
                    cpu: "2"
                    memory: 2Gi
                  requests:
                    cpu: "1"
                    memory: 2Gi
          volumeClaimTemplate:
            apiVersion: v1
            kind: PersistentVolumeClaim
            metadata:
              name: persistent-storage
            spec:
              accessModes:
              - ReadWriteOnce
              resources:
                requests:
                  storage: 2Gi
              storageClassName: hwameistor-storage-lvm-hdd

2. 在 kubectl 客户端中，使用以下命令创建云莓数据库的计算集群。所有的节点容器会自动拉起。

   .. code:: shell

      kubectl -n hashdata apply -f computing-cluster.yaml

3. 在 kubectl 客户端中，使用以下命令验证云莓数据库的集群节点是否正常启动。

   ::

      kubectl -n hashdata get pods

   .. image:: /images/k8s-deploy-command1.png

第 4 步：测试验证数据库容器化部署
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. 在 kubectl 客户端中，参考以下命令（以 ``5432`` 端口为例）转发数据。

   .. code:: shell

      kubectl -n hashdata port-forward pods/cc1-master-0 5432:5432

2. 使用客户端安装 psql 工具（如果已安装可跳过）。

   .. code:: shell

      yum install postgresql -y

3. 检查 HashData Lightning 集群状态。

   .. code:: shell

      psql -h cbdb-master-0 -p 5432 -d postgres -U gpadmi
      postgres=# select * from gp_segment_configuration;
      dbid | content | role | preferred_role | mode | status | port |    hostname    |    address     |          datadir          
      ------+---------+------+----------------+------+--------+------+----------------+----------------+---------------------------
          1 |      -1 | p    | p              | n    | u      | 5432 | cbdb-master-0  | cbdb-master-0  | /data0/data/master/gpseg
          2 |       0 | p    | p              | n    | u      | 6000 | cbdb-segment-0 | cbdb-segment-0 | /data0/data/primary/gpseg
          3 |       1 | p    | p              | n    | u      | 6000 | cbdb-segment-1 | cbdb-segment-1 | /data0/data/primary/gpseg
          4 |       2 | p    | p              | n    | u      | 6000 | cbdb-segment-2 | cbdb-segment-2 | /data0/data/primary/gpseg

扩容数据库的计算集群
--------------------

**当前该功能为实验特性，不建议在生产环境中使用。**

1. 在 kubectl 客户端中，执行以下命令开始编辑 CRD 配置文件。

   ::

      kubectl edit cc cbdb -n hashdata

2. 在配置文件中，编辑 ``segments`` 部分下 ``replicas`` 配置项目的实例数。以下示例将 ``3`` 改为 ``4`` 即完成了计算节点的实例扩容。保存配置并退出。

   .. code:: yaml

      segments:
        podTemplate:
          spec:
            affinity: {}
            containers:
            - name: cc-segment
          replicas: ~~3~~ 4

   .. image:: /images/k8s-deploy-command2.png

3. 在 kubectl 客户端中，执行以下命令确认计算集群扩容是否完成。

   ::

      kubectl get pods -n test -n hashdata

   .. image:: /images/k8s-deploy-command3.png

4. 检查数据库集群信息，确认新扩容的 segment 节点已经被识别并加载入数据库集群中。

   .. image:: /images/k8s-deploy-command4.png

删除数据库计算集群
------------------

要删除数据库集群的所有节点，在 kubectl 客户端中执行以下命令。

::

   kubectl -n hashdata delete cc cbdb
