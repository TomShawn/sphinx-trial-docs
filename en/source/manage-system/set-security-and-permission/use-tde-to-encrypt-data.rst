透明数据加密
============

为了满足保护用户数据安全的需求，HashData Lightning 推出透明数据加密 TDE (Transparent Data Encryption) 功能。透明数据加密是数据库用于加密数据文件的一种技术。从字面上来说，可以分为三部分，数据，加密，透明。数据指的是数据库数据。文件在硬盘上是密文，在内存中是明文。TDE 解决了保护静态数据的问题，也称为静态数据加密。所谓透明是指加密对用户来说是透明的，用户无需更改原有的操作习惯，用户和应用程序都无需关注密钥管理或者加密/解密过程。

.. topic:: 数据加密场景

   在中国，为了保证互联网信息安全，国家要求相关服务开发商需要满足一些数据安全标准，例如：

   -  `《国家密码法》 <http://www.npc.gov.cn/npc/c30834/201910/6f7be7dd5ae5459a8de8baf36296bc74.shtml>`__\ （2020 年 1 月 1 日施行）
   -  `《网络安全等级保护基本要求》 <http://gxxxzx.gxzf.gov.cn/szjcss/wlyxxaq/P020200429546812083554.pdf>`__\ (GB/T 22239-2019) (PDF 地址)

   在国际上，一些相关行业也有监管数据安全标准，例如：

   -  Payment Card Industry Data Security Standard (PCI DSS)
   -  Health Insurance Portability and Accountability Act (HIPAA)
   -  General Data Protection Regulation (GDPR)
   -  California Consumer Protection Act (CCPA)
   -  Sarbanes-Oxley Act (SOX)

前提条件
--------

HashData Lightning 节点上需要安装 `OpenSSL <https://www.openssl.org/source/>`__\ 。通常，Linux 发布版操作系统都内置有 OpenSSL。

实现原理
--------

基本概念
~~~~~~~~

.. list-table::
   :header-rows: 1
   :align: left

   * - 名词
     - 描述
   * - DEK (Data Encryption Key)
     - 存在于数据仓库计算节点内存的数据加密密钥。通过数据库内部随机数函数生成，作为实际加密数据的密码。
   * - DEK 明文
     - 跟 DEK 同义，只能保存在内存中。
   * - Master Key
     - 主密钥，用于加密 DEK。
   * - DEK 密文
     - 使用 Master Key 加密 DEK 明文生成 DEK 密文，持久到统一存储中。

加密算法
~~~~~~~~

密码体制从原理上可分为两类：

-  单钥（对称）体制：加密密钥和解密密钥相同。
-  双钥（非对称）（公钥 ）体制：公钥公开用于加密，私钥私有用于解密。将加密能力与解密能力分开，可实现一对多和多对一。

单钥体制对明文消息的加密有两种方式：

-  流密码：明文消息按字符逐位加密。
-  分组密码：将明文消息分组（含有多个字符），逐组地进行加密。

.. topic:: 密钥类型

   -  流式加密的特性是，密钥长度与明文数据长度一致，而这在数据库中是难以实现的，所以在这不考虑。
   -  公钥加密是最大的优势在于分为公私密钥，公钥是可以公开的，这就降低了密钥管理的问题，但是其加密性能太差，分组加密算法的加密性能是公钥加密的几百倍，所以在此也不考虑。
   -  分组加密是目前主流的加密算法，性能最优，应用最广。

HashData Lightning 支持的分组加密算法有 AES 和 SM4 两种。

AES 加密算法
^^^^^^^^^^^^

国际公认的分组加密算法是 AES (Advanced Encryption Standard)。分组加密算法，首先需要分组，AES 的加密长度为 128 bits，也就是 16 bytes。AES 拥有 3 种密钥长度，128、192 以及 256。AES 拥有 5 种加密模式：

-  ECB mode：Electronic Code Book mode，电子密码本模式
-  CBC mode：Cipher Block Chaining mode，密码分组链表模式
-  CFB mode：Cipher Feedback mode，密文反馈模式
-  OFB mode：Output Feedback mode，输出反馈模式
-  CTR mode：Counter mode，计数器模式

国密算法
^^^^^^^^

国密即国家密码局认定的国产密码算法。主要有 SM1、SM2、SM3、SM4。密钥长度和分组长度均为 128 位。

-  SM1 为对称加密。其加密强度与 AES 相当。该算法不公开，调用该算法时，需要通过加密芯片的接口进行调用。
-  SM2 为非对称加密，基于 ECC。该算法已公开。由于该算法基于 ECC，因此它的签名速度与秘钥生成速度都快于 RSA。ECC 256 位（SM2 采用的就是 ECC 256 位的一种）安全强度比 RSA 2048 位高，运算速度也快于 RSA。
-  SM3 消息摘要。可以用 MD5 作为对比理解。该算法已公开。校验结果为 256 位。
-  SM4 无线局域网标准的分组数据算法。对称加密，密钥长度和分组长度均为 128 位。

透明数据加密功能实现
~~~~~~~~~~~~~~~~~~~~

透明数据加密功能主要由两大模块组成，密钥管理模块和存储层加密模块。

密钥管理模块
^^^^^^^^^^^^

密钥管理模块分为两层体系结构。我们使用加密算法对数据进行加密，而加密算法要利用到密钥。为了减少密钥更换带来的重复加解密的开销，业界大多采用多层密钥管理的结构。

**两层密钥结构：** 两层密钥结构中包含主密钥 (master key) 和数据加密密钥 (data encryption key, DEK)。Master key 用来加密 DEK，而且是保存在数据库之外。DEK 明文用来加密数据库数据，可以使用 master key 加密后生成 DEK 密文，保存在数据库本地。

使用方法
--------

HashData Lightning 提供透明数据加密功能，用户在部署 HashData Lightning 时开启 TDE 功能即可，此后的数据加密操作对于用户来说是透明，不需要额外关注。

想要在部署 HashData Lightning 时开启 TDE，使用 ``gpinitsystem`` 进行初始化数据库时候，用户需要指定 ``-T`` 参数。HashData Lightning 支持 AES 和 SM4 两种加密算法，开启的方法如下：

-  开启 TDE 特性，并指定加密算法为 AES：

   .. code:: shell

      gpinitsystem -c gpinitsystem_config -T AES256

-  开启 TDE 特性，并指定加密算法为 SM4：

   .. code:: shell

      gpinitsystem -c gpinitsystem_config -T SM4

验证方法
--------

透明数据加密功能是指加密对用户来说是透明的，打开或者关闭该特性，读写操作感觉不出来差异的。密钥文件是十分重要的数据，如果丢失密钥文件，那么启动数据库失败。因为数据库启动完成之后，会加载密钥到内存上。所以需要启动停止数据库透明数据加密功能。密钥文件路径放在 master 节点上。

先找到 master 节点的数据目录，例如：

.. code:: shell

   COORDINATOR_DATA_DIRECTORY=/home/gpadmin/work/data0/master/gpseg-1

然后再找密钥文件

.. code:: shell

   [gpadmin@i-uetggb33 gpseg-1]$ pwd
   /home/gpadmin/work/data0/master/gpseg-1
   [gpadmin@i-uetggb33 gpseg-1]$ ls -l pg_cryptokeys/live/
   total 8
   -rw------- 1 gpadmin gpadmin 48 Apr 12 10:26 relation.wkey
   -rw------- 1 gpadmin gpadmin 48 Apr 12 10:26 wal.wkey

其中 ``relation.wkey`` 是用来加密数据文件的密钥，\ ``wal.wkey`` 是用来加密 wal 日志的密钥。现在只有 ``relation.wkey`` 有作用，wal 日志还没有加密。

验证过程
~~~~~~~~

1. 创建表，并写入数据

   .. code-block:: sql

      postgres=# create table ao2 (id int) with(appendonly=true);
      NOTICE:  Table doesn't have 'DISTRIBUTED BY' clause -- Using column named 'id' as the Cloudberry Database data distribution key for this table.
      HINT:  The 'DISTRIBUTED BY' clause determines the distribution of data. Make sure column(s) chosen are the optimal data distribution key to minimize skew.

      CREATE TABLE
      postgres=# insert into ao2 select generate_series(1,10);
      INSERT 0 10

2. 先停止运行数据库 ``gpstop -a``\ ，再制造密钥文件丢失的场景：

   .. code:: shell

      cd /home/gpadmin/work/data0/master/gpseg-1/pg_cryptokeys/
      # 把密钥文件移走其他目录
      mv live backup

3. 尝试启动数据库 ``gpstart -a``\ 。

   由于没有密钥文件，启动数据库失败，无法读取数据库，保护了数据。观察 master 节点数据库日志，会发现以下错误日志，找到 encryption keys。丢失了密钥文件，这是一个十分严重的系统错误，我们不应该让数据库启动成功。

   .. code:: shell

      2024-04-12 10:46:04.703250 CST,,,p24962,th-1601394560,,,,0,,,seg-1,,,,,"FATAL","XX000","cluster has no data encryption keys",,,,,,,0,,"kmgr.c",298,"Stack trace:
      1    0x7fd399ee8a28 libpostgres.so errstart + 0x3b4
      2    0x7fd399ee8672 libpostgres.so errstart_cold + 0x20
      3    0x7fd399f8eb1e libpostgres.so InitializeKmgr + 0x222
      4    0x7fd399c27bf1 libpostgres.so PostmasterMain + 0x12ef
      5    0x40280b postgres <symbol not found> (main.c:289)
      6    0x7fd398abe555 libc.so.6 __libc_start_main + 0xf5
      7    0x402289 postgres <symbol not found> + 0x402289
      "

4. 恢复密钥文件

   .. code:: shell

      cd /home/gpadmin/work/data0/master/gpseg-1/pg_cryptokeys/
      #把密钥文件移走其他目录
      mv backup live

5. 尝试启动数据库 ``gpstart -a``\ ，启动成功，读取数据成功。

   .. code:: shell

      postgres=# select * from ao2 order by id;
      id
      ----
        1
        2
        3
        4
        5
        6
        7
        8
        9
      10
      (10 rows)

性能评测
--------

开启 TDE 加密功能后，可提高静态数据的安全性，但同时会影响访问加密数据库的读写性能，请结合实际情况选择开启 TDE 加密功能。下面是 TPC-H 的性能测试数据，SM4 算法是国密算法，对性能损耗较大，建议使用 AES256。

测试环境
~~~~~~~~

华为云 ECS 主机，计算节点 16 核 CPU / 32G 内存 / 200G SSD，部署 3 个 segment 节点。

测试数据
~~~~~~~~

.. table:: 
   :align: left

   ======== ========== ======== ======== ============= ==========
   加密算法 数据集大小 存储类型 压缩类型 查询时长 (秒) 性能损耗
   ======== ========== ======== ======== ============= ==========
   无       5G         AO       无       648           0%（基准）
   AES      5G         AO       无       658           1.5%
   SM4      5G         AO       无       2079          220.8%
   ======== ========== ======== ======== ============= ==========

.. table:: 
   :align: left

   ======== ========== ======== ======== ============= ==========
   加密算法 数据集大小 存储类型 压缩类型 查询时长 (秒) 性能损耗
   ======== ========== ======== ======== ============= ==========
   无       5G         AO       zstd     663           0%（基准）
   AES      5G         AO       zstd     665           0.3%
   SM4      5G         AO       zstd     4000          503%
   ======== ========== ======== ======== ============= ==========

.. table:: 
   :align: left

   ======== ========== ======== ======== ============= ==========
   加密算法 数据集大小 存储类型 压缩类型 查询时长 (秒) 性能损耗
   ======== ========== ======== ======== ============= ==========
   无       10G        AO       无       1160          0%（基准）
   AES256   10G        AO       无       1212          4.48%
   SM4      10G        AO       无       4000          244%
   ======== ========== ======== ======== ============= ==========

.. table:: 
   :align: left

   ======== ========== ======== ======== ============= ========
   加密算法 数据集大小 存储类型 压缩类型 查询时长 (秒) 性能损耗
   ======== ========== ======== ======== ============= ========
   无       5G         AOCS     无       552           0%
   AES      5G         AOCS     无       570           3.2%
   SM4      5G         AOCS     无       3578          548%
   ======== ========== ======== ======== ============= ========
