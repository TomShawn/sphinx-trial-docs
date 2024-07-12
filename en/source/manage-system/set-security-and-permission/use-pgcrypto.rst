使用 pgcrypto 加密数据
======================

``pgcrypto`` 是 HashData Lightning 的加密模块，提供加密功能。

该模块是“受信任的”，也就是说，当前数据库拥有 ``CREATE`` 权限的非超级用户可以安装 ``pgcrypto`` 模块。

.. code:: sql

   CREATE extension pgcrypto;

OpenSSL 相关的算法支持说明
--------------------------

构建 ``pgcrypto`` 可以选择 OpenSSL（最低版本为 1.0.1），即带上 ``--with-openssl`` 选项。选择 OpenSSL 所构建出的 HashData Lightning，与不选择 OpenSSL 所构建出的 HashData Lightning，两者的加密算法支持不完全相同。

例如，构建时带上 ``--with-openssl`` 选项的 ``pgcrypto`` 支持 DES/3DES/CAST5 算法，但不支持 SM3/SM4 算法。构件时不带 ``--with-openssl`` 选项的 ``pgcrypto`` 支持 SM3/SM4 算法，但不支持 DES/3DES/CAST5 算法。是否带 OpenSSL 的详细算法支持情况见下表： 

.. table:: 
   :align: left

   ================== ============ ============
   加密算法           不带 OpenSSL 带有 OpenSSL
   ================== ============ ============
   MD5                支持         支持
   SHA1               支持         支持
   SHA224/256/384/512 支持         支持
   其他摘要算法       不支持       支持
   Blowfish           支持         支持
   AES                支持         支持
   DES/3DES/CAST5     不支持       支持
   行加密             支持         支持
   PGP 对称加密       支持         支持
   PGP 公共秘钥加密   支持         支持
   SM3                支持         不支持
   SM4                支持         不支持
   ================== ============ ============

一般散列函数
------------

``digest()``
~~~~~~~~~~~~

::

   digest(data text, type text) returns bytea
   digest(data bytea, type text) returns bytea

该函数计算返回 ``data`` 的二进制哈希值。\ ``type`` 是要使用的算法。标准算法为 ``md5``\ 、\ ``sha1``\ 、\ ``sha224``\ 、\ ``sha256``\ 、\ ``sha384`` 和 ``sha512``\ 。此外，OpenSSL 支持的任何摘要算法都会自动拾取。

如果你编译的是非 OpenSSL 版本的 ``pgcrypto``\ ，那么 ``type`` 将可选 ``sm3``\ 。

如果你希望结果为十六进制字符串，请在使用 ``encode()``\ 。例如：

.. code:: none

   CREATE OR REPLACE FUNCTION sha1(bytea) returns text AS $$
       SELECT encode(digest($1, 'sha1'), 'hex')
   $$ LANGUAGE SQL STRICT IMMUTABLE;

``hmac()``
~~~~~~~~~~

.. code:: sql

   hmac(data text, key text, type text) returns bytea
   hmac(data bytea, key bytea, type text) returns bytea

使用 ``key`` 密钥计算 ``data`` 的 MAC 值。\ ``type`` 与 ``digest()`` 中的标准算法相同。

这类似于 ``digest()``\ ，但是你只能在知道密钥的情况下重新计算哈希值。这可以防止有人更改数据并更改哈希值以匹配密钥。

如果密钥大于哈希单块的大小，该密钥将先进行散列，得到的哈希值结果将用作密钥。

密码散列函数
------------

函数 ``crypt()`` 和 ``gen_salt()`` 专门用于散列密码。\ ``crypt()`` 进行散列，\ ``gen_salt()`` 为其准备算法参数。

``crypt()`` 中的算法与通常的 MD5 或 SHA1 散列算法有以下不同：

-  ``crypt()`` 中的算法很慢。由于批次处理的数据量很小，这是使暴力破解密码变得困难的唯一方法。
-  ``crypt()`` 中的算法使用一个随机值，称为“盐值”，这样拥有相同密码的用户将拥有不同的加密密码。这也是对碰撞算法的额外防御。
-  ``crypt()`` 中的算法在结果中包含算法类型，因此使用不同算法散列的密码可以共存。
-  ``crypt()`` 中的部分算法是自适应的。也就是说，当计算机变得更快时，你可以将算法调得更慢，而不会引入与现有密码的不兼容。

下表列出了 ``crypto`` 函数支持的算法：

.. table:: 
   :align: left

   +------+--------------+--------------+------------+----------+------------------------+
   | 算法 | 密码最大长度 | 是否为自适应 | 盐值比特数 | 输出长度 | 描述                   |
   +======+==============+==============+============+==========+========================+
   | bf   | 72           | yes          | 128        | 60       | 基于 Blowfish，2a 变体 |
   +------+--------------+--------------+------------+----------+------------------------+
   | md5  | 无限制       | no           | 48         | 34       | 基于 MD5 的加密        |
   +------+--------------+--------------+------------+----------+------------------------+
   | xdes | 8            | yes          | 24         | 20       | DES 的扩展             |
   +------+--------------+--------------+------------+----------+------------------------+
   | des  | 8            | no           | 12         | 13       | 原始 UNIX 加密算法     |
   +------+--------------+--------------+------------+----------+------------------------+

``crypt()``
~~~~~~~~~~~

.. code:: sql

   crypt(password text, salt text) returns text

该函数计算 ``password`` 的 crypt(3) 样式哈希。存储新密码时，你需要使用 ``gen_salt()`` 生成新的 ``salt`` 值。要检查密码，将存储的哈希值作为 ``salt`` 传递，并测试结果是否与存储的值匹配。

设置新密码示例：

.. code:: sql

   UPDATE ... SET pswhash = crypt('new password', gen_salt('md5'));

认证示例：

.. code:: sql

   SELECT (pswhash = crypt('entered password', pswhash)) AS pswmatch FROM ... ;

如果输入的密码正确，则返回 ``true``\ 。

``gen_salt()``
~~~~~~~~~~~~~~

.. code:: sql

   gen_salt(type text [, iter_count integer ]) returns text

该函数生成一个新的随机盐值用于 ``crypt()``\ 。盐值还告诉 ``crypt()``
使用哪个算法。

``type`` 参数指定散列算法。可接受的算法类型有 ``des``\ 、\ ``xdes``\ 、\ ``md5`` 和 ``bf``\ 。

对于有迭代计数的算法，\ ``iter_count`` 参数允许用户指定迭代计数。计数越高，散列密码所需的时间就越长，因此破解密码所需的时间就越长。尽管计数过高，计算散列的时间可能需要几年——这有点不切实际。如果省略 ``iter_count`` 参数，则使用默认的迭代计数。\ ``iter_count`` 所允许的值取决于算法，如下表所示。

.. table:: 
   :align: left

   ==== ====== ====== ========
   算法 默认值 最小值 最大值
   ==== ====== ====== ========
   xdes 725    1      16777215
   bf   6      4      31
   ==== ====== ====== ========

对于 ``xdes``\ ，还有一个额外的限制，即迭代计数必须是奇数。

要选择合适的迭代次数，请考虑原始 DES crypt 在当时的硬件上设计为每秒 4 哈希值的速度。低于每秒 4 个哈希值可能会降低可用性。快于每秒 100 个哈希值可能太快了。

下表罗列了不同散列算法的相对缓慢程度。输入为 8 字符，尝试所有字符组合所需的时间（假设 8 字符中仅包含小写字母，或只包含大小写字母和数字）。在 ``crypt-bf`` 的条目中，斜杠后的数字是 ``gen_salt`` 的 ``iter_count`` 参数。

.. list-table:: 哈希算法比较
   :header-rows: 1
   :align: left

   * - 算法
     - 哈希/秒
     - 仅使用小写字母 ``[a-z]``
     - 使用大小写字母加数字 ``[A-Za-z0-9]``
     - 相对于 md5 哈希速度的倍数
   * - ``crypt-bf/8``
     - 1792
     - 4 年
     - 3927 年
     - 100k
   * - ``crypt-bf/7``
     - 3648
     - 2 年
     - 1929 年
     - 50k
   * - ``crypt-bf/6``
     - 7168
     - 1 年
     - 982 年
     - 25k
   * - ``crypt-bf/5``
     - 13504
     - 188 年
     - 521 年
     - 12.5k
   * - ``crypt-md5``
     - 171584
     - 15 天
     - 41 年
     - 1k
   * - ``crypt-des``
     - 23221568
     - 157.5 分钟
     - 108 天
     - 7
   * - ``sha1``
     - 37774272
     - 90 分钟
     - 68 天
     - 4
   * - ``md5 (hash)``
     - 150085504
     - 22.5 分钟
     - 17 天
     - 1

.. attention:: 

   -  使用的处理器为 Intel Mobile Core i3。
   -  ``crypt-des`` 和 ``crypt-md5`` 算法的数字取自 John the Ripper v1.6.38 ``-test`` 输出。
   -  ``md5`` hash 数来自 mdcrack 1.2。
   -  ``sha1`` 数字来自 lcrack-20031130-beta。
   -  ``crypt-bf`` 数字是使用一个简单程序来获取的，该程序循环超过 1000 个 8 字符的密码。这样就可以显示不同迭代次数的速度。

请注意，“尝试所有组合”不是一个现实的做法。通常，密码破解是在字典的帮助下完成的，字典中包含常规单词和一些字符集特有的字符。因此，即使是有点像单词的密码，也可能比上述数字显示的密码破解起来要快得多。而 6 个字符的非单词密码可能无法破解，或者没有。

PGP 加密函数
------------

PGP 加密函数实现了 OpenPGP (`RFC4880 <https://tools.ietf.org/html/rfc4880>`__) 标准的加密部分,支持对称密钥和公钥加密。

加密的 PGP 消息由两个部分或“数据包”组成：

-  包含会话密钥的数据包 - 对称密钥或公钥加密。
-  包含用会话密钥加密的数据的数据包。

使用对称密钥（即密码）加密时：

-  给定的密码使用 ``String2Key``\ (S2K) 算法进行散列，这与 ``crypt()`` 算法非常相似（故意缓慢且带有随机盐值）但它会生成一个全长二进制密钥。
-  如果请求单独的会话密钥，HashData Lightning 将生成一个新的随机密钥。否则，S2K 密钥将直接用作会话密钥。
-  如果要直接使用 S2K 密钥，则只有 S2K 设置将被放入会话密钥包中。否则，会话密钥将使用 S2K 密钥加密并放入会话密钥包中。

使用公钥加密时：

-  HashData Lightning 生成一个新的随机会话密钥。
-  HashData Lightning 使用公钥加密并放入会话密钥包中。

在任何一种情况下，要加密的数据都按以下方式处理：

-  可选的数据操作：压缩、转换为 UTF-8 并/或转换换行符。
-  数据以随机字节块为前缀，这相当于使用随机 IV。
-  附加一个 SHA1 哈希值作为随机前缀。
-  所有使用会话密钥加密的数据会被封包。

``pgp_sym_encrypt()``
~~~~~~~~~~~~~~~~~~~~~

.. code:: sql

   pgp_sym_encrypt(data text, psw text [, options text ]) returns bytea
   pgp_sym_encrypt_bytea(data bytea, psw text [, options text ]) returns bytea

使用对称 PGP 密钥 ``psw`` 加密 ``data``\ 。\ ``options`` 参数可以包含选项设置，如下所述。

``pgp_sym_decrypt()``
~~~~~~~~~~~~~~~~~~~~~

.. code:: sql

   pgp_sym_decrypt(msg bytea, psw text [, options text ]) returns text
   pgp_sym_decrypt_bytea(msg bytea, psw text [, options text ]) returns bytea

解密对称密钥加密的 PGP 消息。

你不能使用 ``pgp_sym_decrypt`` 解密 ``bytea`` 数据，这是为了避免输出无效的字符数据。你可以使用 ``pgp_sym_decrypt_bytea`` 解密原始文本数据。

如下所述，\ ``options`` 参数可以包含选项设置。

``pgp_pub_encrypt()``
~~~~~~~~~~~~~~~~~~~~~

.. code:: sql

   pgp_pub_encrypt(data text, key bytea [, options text ]) returns bytea
   pgp_pub_encrypt_bytea(data bytea, key bytea [, options text ]) returns bytea

使用公共 PGP 密钥 ``key`` 加密 ``data``\ 。给此函数一个密钥将产生错误。

如下所述，\ ``options`` 参数可以包含选项设置。

``pgp_pub_decrypt()``
~~~~~~~~~~~~~~~~~~~~~

.. code:: sql

   pgp_pub_decrypt(msg bytea, key bytea [, psw text [, options text ]]) returns text
   pgp_pub_decrypt_bytea(msg bytea, key bytea [, psw text [, options text ]]) returns bytea

解密公钥加密的消息。\ ``key`` 必须是与用于加密的公钥相对应的密钥。如果密钥受密码保护，则必须以 ``psw`` 提供密码。如果没有密码，任需填充参数，提供空密码即可。

你不能使用 ``pgp_pub_decrypt`` 解密 ``bytea`` 数据，这是为了避免输出无效的字符数据。你可以使用 ``pgp_pub_decrypt_bytea`` 解密原始文本数据。

如下所述，\ ``options`` 参数可以包含选项设置。

``pgp_key_id()``
~~~~~~~~~~~~~~~~

.. code:: sql

   pgp_key_id(bytea) returns text

``pgp_key_id`` 提取 PGP 公钥或私钥的密钥 ID。或者，如果给定加密消息，\ ``pgp_key_id`` 会给出用于加密数据的密钥 ID。

该函数可以返回 2 个 特殊的密钥 ID：

-  ``SYMKEY``\ ：消息使用对称密钥加密。
-  ``ANYKEY``\ ：消息是公钥加密的，但密钥 ID 已被删除。因此你需要尝试所有密钥才能查看哪个密钥能解密它。\ ``pgcrypto`` 本身不会生成此类消息。

请注意，不同的密钥可能具有相同的 ID，这很少见，但属正常情况。然后，客户端应用程序应该尝试对每个密钥进行解密，看看哪个适合，就像处理 ``ANYKEY`` 一样。

``armor()``, ``dearmor()``
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sql

   armor(data bytea [ , keys text[], values text[] ]) returns text
   dearmor(data text) returns bytea

这些函数将二进制数据包装或解包为 PGP ASCII-armor 格式，基本上是带有 CRC 和附加格式的 Base64。

如果指定了 ``keys`` 和 ``values`` 数组，HashData Lightning 则会为每个键/值对的 armor 格式添加一个 armor header。两个数组必须是单维的，并且必须具有相同的长度。键和值不能包含任何非 ASCII 字符。

``pgp_armor_headers``
~~~~~~~~~~~~~~~~~~~~~

.. code:: sql

   pgp_armor_headers(data text, key out text, value out text) returns setof record

``pgp_armor_headers()`` 从 ``data`` 中提取 armor 标题。返回值是一组包含键和值两列的行。如果键或值包含任何非 ASCII 字符，它们将被视为 UTF-8。

PGP 函数的选项
~~~~~~~~~~~~~~

PGP 函数选项的命名类似于 GnuPG。选项的值应在等号后给出，用逗号将多个选项分开。例如：

.. code:: sql

   pgp_sym_encrypt(data, psw, 'compress-algo=1, cipher-algo=aes256')

除了 ``convert-crlf`` 外，所有的选项只适用于加密函数。解密函数从 PGP 数据获取参数。

最有趣的选项可能是 ``compress-algo`` 和 ``unicode-mode``\ 。其它的选项应该有合理的默认值。

以下为 PGP 函数的选项：

``cipher-algo``
^^^^^^^^^^^^^^^

-  使用哪种密码算法。
-  可选值：bf、aes128、aes192、aes256、3des、cast5
-  默认值：aes128
-  适用于：pgp_sym_encrypt、pgp_pub_encrypt

``compress-algo``
^^^^^^^^^^^^^^^^^

-  使用哪种压缩算法。仅当 HashData Lightning 用 zlib 构建时可用。
-  可选值：

   -  ``0``，表示无压缩
   -  ``1``，表示 ZIP 压缩
   -  ``2``，表示 ZLIB 压缩（=ZIP 加上元数据和块 CRC）

-  默认值：0
-  适用于：``pgp_sym_encrypt、pgp_pub_encrypt``

``compress-level``
^^^^^^^^^^^^^^^^^^

-  指定压缩级别。较高的级别能有更好的压缩率，但压缩速度较慢。0
   表示禁用压缩。
-  可选值：\ ``0``、\ ``1``\ -\ ``9``
-  默认值：6
-  适用于：\ ``pgp_sym_encrypt``\ 、\ ``pgp_pub_encrypt``

``convert-crlf``
^^^^^^^^^^^^^^^^

-  加密时是否将 ``\n`` 转换为 ``\r\n``\ ，解密时是否将 ``\r\n`` 转换为 ``\n``\ 。RFC4880 指定文本数据应使用 ``\r\n`` 换行符存储。使用 ``convert-crlf`` 选项来获得完全符合 RFC 的行为。
-  可选值：\ ``0``\ 、\ ``1``
-  默认值：\ ``0``
-  适用于：\ ``pgp_sym_encrypt``\ 、\ ``pgp_pub_encrypt``\ 、\ ``pgp_sym_decrypt``\ 、\ ``pgp_pub_decrypt``

``disable-mdc``
^^^^^^^^^^^^^^^

-  不要使用 ``SHA-1`` 来保护数据。使用 ``disable-mdc`` 选项的唯一好处是与早期 PGP 产品兼容，这些产品在 RFC 4880 中添加 SHA-1 保护数据包之前就存在了。 gnupg.org 和 pgp.com 软件都支持得很好。
-  可选值：0、1
-  默认值：0
-  适用于：pgp_sym_encrypt、pgp_pub_encrypt

``sess-key``
^^^^^^^^^^^^

-  使用单独的会话密钥。公钥加密始终使用单独的会话密钥。此选项用于对称密钥加密，默认情况下直接使用 S2K 密钥。
-  值：0、1
-  默认值：0
-  适用于：pgp_sym_encrypt

``s2k-mode``
^^^^^^^^^^^^

-  使用哪个 S2K 算法。
-  可选值：

   -  0，表示不加盐值。使用容易造成危险，请慎用。
   -  1，加盐值，但有固定的迭代计数。
   -  3，可变迭代计数。

-  默认值：3
-  适用于：pgp_sym_encrypt

``s2k-count``
^^^^^^^^^^^^^

-  待使用的 S2K 算法的迭代次数，该选项值必须介于 ``1024`` 和 ``65011712`` 之间。
-  默认值：\ ``65536`` 和 ``253952`` 之间的随机值。
-  适用于：pgp_sym_encrypt，只有 s2k-mode=3

``s2k-digest-algo``
^^^^^^^^^^^^^^^^^^^

-  在 S2K 计算中使用哪种摘要算法。
-  可选值：md5、sha1
-  默认值：sha1
-  适用于：pgp_sym_encrypt

``s2k-cipher-algo``
^^^^^^^^^^^^^^^^^^^

-  使用哪种密码来加密单独的会话密钥。
-  可选值：bf、aes、aes128、aes192、aes256
-  默认值：使用密码算法
-  适用于：pgp_sym_encrypt

``unicode-mode``
^^^^^^^^^^^^^^^^

-  是否将文本数据从数据库内部编码转换为 UTF-8 并返回。如果你的数据库已经是 UTF-8 编码，则不会进行转换，但消息将被标记为 UTF-8。如果没有此选项，则不会进行转换。
-  可选值：0、1
-  默认值：0
-  适用于：pgp_sym_encrypt、pgp_pub_encrypt

使用 GnuPG 生成 PGP 密钥
~~~~~~~~~~~~~~~~~~~~~~~~

-  生成新密钥：

   .. code:: sql

      gpg --gen-key

   首选的密钥类型是 "DSA" 和 "Elgamal"。

   对于 RSA 加密，你必须创建 DSA 或 RSA 签名密钥作为 master，然后使用 ``gpg--edit-key`` 添加 RSA 加密子密钥。

-  列出键：

   .. code:: sql

      gpg --list-secret-keys

-  以 ASCII armor 格式导出公钥：

   .. code:: sql

      gpg -a --export KEYID > public.key

-  以 ASCII armor 格式导出密钥：

   .. code:: sql

      gpg -a --export-secret-keys KEYID > secret.key

在将这些密钥传给 PGP 函数之前，你需要在这些密钥上使用 ``dearmar()``\ 。或者，如果你能处理二进制数据，可以从命令中删除 ``-a``\ 。

更多详细信息，请参阅 ``man gpg``\ 、\ `GNU 隐私手册 <https://www.gnupg.org/gph/en/manual.html>`__\ 和其他 https://www.gnupg.org/ 文档。

PGP 代码的限制
~~~~~~~~~~~~~~

-  不支持签名，即不检查加密子密钥是否属于主密钥。
-  不支持加密密钥作为主密钥。通常不建议将加密密钥作为主密钥。
-  不支持多个子密钥。这似乎是一个问题，因为子密钥是常见的做法。另一方面，你不应该将常规的 GPG 或 PGP 密钥与 ``pgcrypto`` 一起使用，而是创建新的密钥，因为使用场景相当不同。

Raw 加密函数
------------

这些函数只对数据运行密码，它们没有任何 PGP 加密的高级功能，因此主要存在以下问题：

-  直接使用用户密钥作为密码密钥。
-  不提供任何完整性检查，无法查看加密数据是否已被修改。
-  要求用户自己管理所有加密参数，甚至 IV。
-  不处理文本。

因此，随着 PGP 加密的引入，不鼓励使用原始加密函数。

.. code:: sql

   encrypt(data bytea, key bytea, type text) returns bytea
   decrypt(data bytea, key bytea, type text) returns bytea

   encrypt_iv(data bytea, key bytea, iv bytea, type text) returns bytea
   decrypt_iv(data bytea, key bytea, iv bytea, type text) returns bytea

使用 ``type`` 指定的密码方法来加密或解密数据。\ ``type`` 字符串的语法是：

::

   **algorithm** [ - **mode** ] [ /pad: **padding** ]

其中 **algorithm** 是以下其中之一：

-  ``BF``- Blowfish
-  ``AES``- AES（Rijndael-128，-192 或 -256）

   -  如果你编译的是非 OpenSSL 的 ``pgcrypto``\ ，那么 ``sm4`` 将为可选值

**mode** 是以下其中之一：

-  ``CBC``- 下一个区块取决于上一个（默认）
-  ``ECB`` - 每个区块单独加密（安全程度不够，不推荐使用）

``padding`` 是以下其中之一：

-  ``pkcs`` - 数据可以是任意长度（默认）
-  ``无`` - 数据必须是密码块大小的倍数

例如，这些是等价的：

.. code:: sql

   encrypt(data, 'fooz', 'bf')
   encrypt(data, 'fooz', 'bf-cbc/pad:pkcs')

在 ``encrypt_iv`` 和 ``decrypt_iv`` 中，\ ``iv`` 参数是 CBC 模式的初始值；对于 ECB，它被忽略。如果不完全是块大小，它将用零进行剪辑或填充。在没有此参数的函数中，它默认为所有 0。

随机数据函数
------------

.. code:: sql

   gen_random_bytes(count integer) returns bytea

以加密方式返回 ``count`` 强随机字节。一次最多可以提取 1024 个字节，可以避免耗尽随机生成器池。

.. code:: sql

   gen_random_uuid() returns uuid

返回版本 4 的（随机）UUID。（已废弃，此函数内部调用同名\ `核心函数 <https://www.postgresql.org/docs/current/functions-uuid.html>`__\ 。）

注意事项
--------

配置
~~~~

``pgcrypto`` 根据主要 HashData Lightning ``configure`` 脚本的发现进行自我配置。影响它的选项是 ``--with-zlib`` 和 ``--with-openssl``\ 。

当使用 zlib 编译时，PGP 加密函数能够在加密之前压缩数据。

当针对 OpenSSL 3.0.0 及更高版本进行编译时，必须在 ``openssl.cnf`` 配置文件中激活旧版提供程序，以便使用 DES 或 Blowfish 等旧的加密方法。

Null 处理
~~~~~~~~~

按照 SQL 标准，如果任何参数为 NULL，则所有函数都返回 NULL。如果不谨慎使用，可能产生安全风险。

安全限制
~~~~~~~~

所有 ``pgcrypto`` 函数都在数据库服务器内部运行。这意味着所有数据和密码都以明文形式在 ``pgcrypto`` 和客户端应用程序之间移动。因此，你需要：

1. 本地连接或使用 SSL 连接。
2. 信任系统和数据库管理员。

如果不能，那么最好在客户端应用程序中执行加密。

不能抵抗侧信道攻击。例如，\ ``pgcrypto`` 解密功能完成所需的时间因给定大小的密文而异。
