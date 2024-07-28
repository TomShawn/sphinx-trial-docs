.. raw:: latex

   \newpage

读写外部表时自定义多字符分隔符
==============================

在读写外表数据时，HashData Lightning 支持通过扩展 ``gp_exttable_delimiter`` 来自定义分割字符，从而读写更加丰富的数据格式。

编译和安装
----------

在安装了 HashData Lightning 的服务器下，下载该扩展，然后安装即可使用。

.. code:: bash

   cd gp_exttable_delimiter

   make install

使用示例
--------

读取外部表
~~~~~~~~~~

1. 准备示例文件 ``1.txt``\ ，并开启 gpfdist 提供网络分发能力。

   .. code:: bash

      touch 1.txt
      echo 'aa|@|bb' > 1.txt
      gpfdist -p 8088 -d .

2. 创建 ``gp_exttable_delimiter`` 插件。

   .. code:: sql

      CREATE EXTENSION if not exists gp_exttable_delimiter;
      CREATE TABLE t1 (c1 text, c2 text);

3. 创建外部表。

   .. code:: sql

      CREATE EXTERNAL TABLE t1_ext (LIKE t1)LOCATION ('gpfdist://localhost:8088/1.txt')FORMAT 'CUSTOM' (formatter=delimiter_in, entry_delim='|@|',line_delim=E'\n');

   在以上创建外部表的语句中：

   -  ``FORMAT 'CUSTOM'`` 即表示自定义分隔符。
   -  ``formatter=delimiter_in`` 是 ``gp_exttable_delimiter`` 提供的字符串分割函数，表示读取文件。
   -  ``entry_delim='|@|'`` 指定列与列之间以 ``|@|`` 字符串进行分割。
   -  ``line_delim`` 指定以 ``\n`` 回车字符分割下一行元组。

4. 查询外部表，即可读取相关的内容。

   .. code:: sql

      SELECT * FROM t1_ext;

写入外部表
~~~~~~~~~~

1. 准备待写入的示例文件 ``2.txt``\ 。

   .. code:: bash

      touch 2.txt

2. 创建 ``gp_exttable_delimiter`` 插件。

   .. code:: sql

      CREATE EXTENSION if not exists gp_exttable_delimiter;
      CREATE TABLE t2 (a int,b int);

3. 创建外表并将数据写入 ``2.txt``\ 。

   .. code:: sql

      CREATE WRITABLE EXTERNAL TABLE t2_ext(LIKE t2) LOCATION ('gpfdist://localhost:8088/2.txt')FORMAT 'CUSTOM' (FORMATTER=delimiter_ou_any,entry_delim='|@|',line_delim=E'\n',null='');

      INSERT INTO t2_ext values(1,2);

   在以上创建外部表的语句中：

   -  ``FORMAT 'CUSTOM'`` 即表示自定义分隔符。
   -  ``FORMATTER=delimiter_ou_any`` 是 ``gp_exttable_delimiter`` 提供的字符串分割函数，表示写入数据到文件。
   -  ``entry_delim='|@|'`` 指定列与列之间以 ``|@|`` 字符串进行分割。
   -  ``line_delim=E'\n'`` 指定以 ``\n`` 回车字符分割下一行元组。

4. 可在文件中看到写入的数据。

   .. code:: bash

      cat 2.txt
