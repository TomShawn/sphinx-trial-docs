使用 Anon 脱敏数据
==================

Anon 是 HashData Lightning 的插件，是基于 `PostgreSQL Anonymizer <https://postgresql-anonymizer.readthedocs.io/en/stable/>`__ 改造的，可以为 HashData Lightning 提供数据脱敏功能，从而起到防止敏感数据外泄的作用。

数据脱敏又称数据漂白，是指人们将数据中的敏感信息去除。这些敏感信息包括个人的姓名、电话、住址、身份证号码等。Anon 通过 PG 提供的 `SECURITY LABEL <https://www.postgresql.org/docs/current/sql-security-label.html>`__ 功能来指定脱敏规则，并将这些脱敏规则应用到指定的数据库对象上，从而达到数据脱敏的功能。比如原始的电话号码为 ``0609110911``，经过数据脱敏后变成了 ``06******11``\ 。

实现原理
--------

Anon 主要使用 PG 的 SECURITY LABEL 功能来存储脱敏规则，并且会在一个新的命名空间下为原命名空间下的表创建对应的视图。切换到需要对其隐藏敏感数据的用户后，所使用的实际上不是原命名空间的表而是新的命名空间下的同名的视图，由此便实现了对指定的数据库对象应用脱敏规则的功能。

安装 Anon
---------

1. 使用 gppkg 包进行安装。

   .. code:: bash

      # 安装
      gppkg -i anon-*.gppkg

      # 卸载
      gppkg -r anon*

2. 验证。安装完成之后，通过 ``psql`` 创建扩展成功，即表示安装成功。

   .. code:: bash

      # 命令
      psql postgres -c "ALTER DATABASE postgres SET session_preload_libraries = 'anon';"
      psql postgres -c "CREATE EXTENSION IF NOT EXISTS anon CASCADE;"

      # 期待的结果
      NOTICE:  installing required extension "pgcrypto"
      WARNING:  referential integrity (FOREIGN KEY) constraints are not supported in HashData Lightning, will not be enforced
      CREATE EXTENSION

使用指南
--------

Anon 提供的主要功能为动态脱敏，下面简单介绍如何使用动态脱敏并列出可以使用的脱敏函数。

.. warning:: 

   Anon 还提供了静态脱敏的功能，但这个功能十分“危险”，因为它会直接将脱敏后的数据更新到数据库中，从而造成原始数据的丢失。因此不建议在生产环境中使用这一功能。

   但这一功能便于在测试场景使用，现有的许多测试都用到了静态脱敏。相关函数为 ``anon.anonymize_database()``\ ，\ ``anon.anonymize_table()``\ ，\ ``anon.anonymize_column()``\ 。

动态脱敏
~~~~~~~~

动态脱敏是为指定的用户隐藏敏感信息，通过一个例子来具体说明。

1. 指定连接开始时要加载的共享库。注意：设置完这个参数后要新开一个连接才会生效。

   .. code:: sql

      ALTER DATABASE :DBNAME SET session_preload_libraries = 'anon';

2. 创建扩展并初始化。

   .. code:: sql

      CREATE EXTENSION IF NOT EXISTS pgcrypto;
      CREATE EXTENSION IF NOT EXISTS anon CASCADE;
      SELECT anon.init();

3. 创建测试使用的表。

   .. code:: sql

      CREATE TABLE people ( id TEXT, firstname TEXT, lastname TEXT, phone TEXT); 
      INSERT INTO people VALUES ('T1','Sarah', 'Conor','0609110911');

4. 为 people 列指定脱敏规则。

   .. code:: sql

      SECURITY LABEL FOR anon ON COLUMN people.lastname IS 'MASKED WITH FUNCTION anon.fake_last_name()';
      SECURITY LABEL FOR anon ON COLUMN people.phone IS 'MASKED WITH FUNCTION anon.partial(phone,2,$$******$$,2)';

5. 创建新的用户，并将其指定为 "MASKED"。

   .. code:: sql

      CREATE ROLE skynet LOGIN;
      alter ROLE skynet with password '123456';
      SECURITY LABEL FOR anon ON ROLE skynet IS 'MASKED';

6. 开始动态脱敏。

   .. code:: sql

      SELECT anon.start_dynamic_masking();

7. 切换到新用户后查看脱敏后的数据

   .. code:: none

      \c - skynet
      SELECT * FROM people;

      -- 测试结果如下
      dynamic_masking=> SELECT * FROM people;
      id | firstname | lastname |   phone
      ----+-----------+----------+------------
      T1 | Sarah     | Watsica  | 06******11
      (1 row)

.. attention:: 

   如果脱敏时指定了某个函数，例如 ``anon.fake_last_name()``\ ，在查询数据时，必须先关闭 ORCA 优化器。

   .. code-block:: 

      set optimizer to off;

   因为函数 ``fake_last_name`` 会去查询一个数据表，而这在目前是不支持的。如果你自定义的脱敏函数也存在同样的行为，在查询的时候也需要关闭 ORCA 优化器。

可以看到，除去创建扩展并初始化这样的通用操作外，动态脱敏的基本步骤为：为想要脱敏的数据库对象比如某一列指定脱敏规则，将某一用户指定为 "MASKED"，开始动态脱敏。最后该用户登录时扫出来的数据就是脱敏后的数据。

脱敏函数
~~~~~~~~

Anon 提供了以下几类脱敏函数，针对不同的类型可以采用不同的脱敏函数。

Destruction
^^^^^^^^^^^

在许多情况下，隐藏某列内容的最好的办法就是用一个静态的值来替换该列所有的值。例如，可以用单词 "CONFIDENTIAL" 替换一整列。

.. code:: sql

   SECURITY LABEL FOR anon
     ON COLUMN users.address
     IS 'MASKED WITH VALUE ''CONFIDENTIAL'' ';

Adding Noise
^^^^^^^^^^^^

这一系列函数的做法是在原来的值的基础上\ **偏差**\ 一定的比例或者值，比如说在 salary 这列上添加 +/-10% 的偏差。

-  ``anon.noise(original_value,ratio)``\ ：\ ``original_value`` 可以是 integer、 bigint 或是 double precision 类型。
-  ``anon.dnoise(original_value, interval)``\ ：\ ``original_value`` 可以是 date、timestamp 或是 time 类型。

注意：用户可能会多次尝试通过这种方式，然后取平均值试出原始值。

Randomization
^^^^^^^^^^^^^

Anon 提供了大量的函数来生成完全随机的数据。

Basic Random values
'''''''''''''''''''

====================== ======================================
函数                   说明
====================== ======================================
anon.random_date()     返回一个 date。
anon.random_string(n)  返回一个包含 n 个字符的 TEXT 值。
anon.random_zip()      返回一个五位的 code。
anon.random_phone(p)   返回一个以 p 作为前缀的八位电话号码。
anon.random_hash(seed) 给定种子，返回一个随机字符串的哈希值。
====================== ======================================

Random between
''''''''''''''

================================= ==================================
函数                              说明
================================= ==================================
anon.random_date_between(d1,d2)   返回一个 d1 和 d2 之间的 date。
anon.random_int_between(i1,i2)    返回一个 i1 和 i2 之间的 integer。
anon.random_bigint_between(b1,b2) 返回一个 b1 和 b2 之间的 bigint。
================================= ==================================

注意，这些函数返回的值包括了上下界，比如说
``anon.random_int_between(1,3)`` 可以返回 1、2、3。

Random in Array
'''''''''''''''

.. list-table::
   :header-rows: 1
   :align: left

   * - 函数
     - 说明
   * - ``random_in``
     - 函数返回给定的数组中的一个元素，例如 ``anon.random_in(ARRAY[1,2,3])`` 返回 ``1`` 和 ``3`` 之间的一个 int。


Random in Enum
''''''''''''''

.. list-table::
   :header-rows: 1
   :align: left

   * - 函数
     - 说明
   * - ``anon.random_in_enum(variable_of_an_enum_type)``
     - 返回指定的枚举类型的取值范围中的任意一个值。

Random in Range
'''''''''''''''

.. list-table::
   :header-rows: 1
   :align: left

   * - 函数
     - 说明
   * - ``anon.random_in_int4range('[5,6)')``
     - 返回类型为 INT 的 5。
   * - ``anon.random_in_int8range('(6,7]')``
     - 返回类型为 BITINT 的 7。
   * - ``anon.random_in_numrange('[0.1,0.9]')``
     - 返回一个 0.1 到 0.9 之间的 NUMERIC 值。
   * - ``anon.random_in_daterange('[2001-01-01,2001-12-31)')``
     - 返回 2001 年的一个日期。
   * - ``anon.random_in_tsrange('[2022-10-01,2022-10-31]')``
     - 返回 2022 年 10 月的一个 timestamp。
   * - ``anon.random_in_tstzrange('[2022-10-01,2022-10-31]')``
     - 返回 2022 年 10 月的一个带时区的 timestamp。

Faking
^^^^^^

Faking 也是生成随机的内容，但是与 Randomization 不同的是，Faking 生成的是看上去合理的数据。在使用这一系列的函数之前，必须先调用 ``anon.init()`` 函数来导入随机数据集。

这一类型的函数包括：

-  ``anon.fake_address()``
-  ``anon.fake_city()``
-  ``anon.fake_country()``
-  ``anon.fake_company()``
-  ``anon.fake_email()``
-  ``anon.fake_first_name()``
-  ``anon.fake_iban()``
-  ``anon.fake_last_name()``
-  ``anon.fake_postcode()``
-  ``anon.fake_siret()``

对于类型为 TEXT 和 VARCHAR 的列，还可以使用经典的 `Lorem Ipsum <https://lipsum.com/>`__ 生成器：

.. list-table::
   :header-rows: 1
   :align: left

   * - 函数
     - 说明
   * - ``anon.lorem_ipsum(5)``
     - 返回 5 段文字。
   * - ``anon.lorem_ipsum(2)``
     - 返回 2 段文字。
   * - ``anon.lorem_ipsum(paragraphs := 4)``
     - 返回 4 段文字。
   * - ``anon.lorem_ipsum(words := 20)``
     - 返回 20 个单词。
   * - ``anon.lorem_ipsum(characters := 7)``
     - 返回 7 个字符。
   * - ``anon.lorem_ipsum(characters := LENGTH(table.column))``
     - 返回和原始字符串同样长度的字符串。

Pseudonymization
^^^^^^^^^^^^^^^^

Pseudoymization 和 Faking 类似，但是 Pseudoymization 生成的是确定的值，也就是说给定 seed 和 salt，每次都会生成相同的值。在使用这一类函数之前同样也需要调用 ``anon.init()`` 函数。

-  ``anon.pseudo_first_name('seed','salt')``
-  ``anon.pseudo_last_name('seed','salt')``
-  ``anon.pseudo_email('seed','salt')``
-  ``anon.pseudo_city('seed','salt')``
-  ``anon.pseudo_country('seed','salt')``
-  ``anon.pseudo_company('seed','salt')``
-  ``anon.pseudo_iban('seed','salt')``
-  ``anon.pseudo_siret('seed','salt')``

以上函数的第二个参数 ``salt`` 是可选的，如果没有给定 ``salt`` 则会随机选择一个 ``salt``。

Generic Hashing
^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :align: left

   * - 函数
     - 说明
   * - ``anon.hash(value)``
     - 基于 salt 和哈希算法返回给定 value 的哈希值。
   * - ``anon.digest(value, salt, algorithm)``
     - 选择 salt 和从预先定义的链表中选取哈希算法。


扩展初始化时会生成一个随机的 salt，默认的哈希算法为 sha512。可以通过以下两个函数来改变这两个值。

-  ``anon.set_secret_salt(value)``
-  ``anon.set_algorithm(value)`` 可能的值为：md5、sha1、sha224、sha256、sha384 或者 sha512。

注意：salt 和所使用的哈希算法都应该按照与原始数据集相同的安全级别保存起来，否则可能会被攻击者通过这些值计算出原始数据。通常来说，更推荐使用 ``anon.hash()``\ ，因为 salt 不会直接出现在脱敏规则中。

Partial Scrambling
^^^^^^^^^^^^^^^^^^

Partial Scambling 会忽略数据的一部分，比如信用卡号码可以用 ``40XX XXXX XXXX XX96`` 替代。

======================================= =======================
函数                                    说明
======================================= =======================
anon.partial('abcdefgh',1,'xxxx',3)     会返回 'axxxxfgh'。
anon.partial_email('daamien@gmail.com') 会变成 'da*@gm**.com'。
======================================= =======================

Generalization
^^^^^^^^^^^^^^

Generalization 指的是使用一个范围去替代原本精确的值。比如林千歌的实际年龄是 21 岁，可以说林千歌的年龄在 20 岁到 30 岁之间。Generalization 会让列的数据类型发生改变，因此不能将相关的函数和动态脱敏一起使用。相关的函数如下：

-  ``generalize_int4range(value, step)``
-  ``generalize_int8range(value, step)``
-  ``generalize_numrange(value, step)``

Value 是要被泛化的数据，而 step 是每一个范围的大小。
