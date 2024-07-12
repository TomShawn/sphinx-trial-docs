日志审计 pgAudit
================

日志审计扩展 pgAudit 通过标准的 PostgreSQL 日志记录功能提供详细的会话或对象审计日志记录。

pgAudit 的目标是为用户提供生成审计日志的能力，这些日志通常需要符合政府、财务或 ISO 认证。审计是对个人或组织账户的官方检查，通常由独立机构进行。

编译和安装
----------

HashData Lightning v1.5.3 中已安装 pgAudit。若需要单独安装，请按以下步骤执行。

使用 PGXS 开发包，可以根据已安装的 PostgreSQL 副本编译 pgAudit。以下说明适用于 RHEL 7。

1. 克隆 pgAudit 扩展：

   .. code:: shell

      git clone https://github.com/pgaudit/pgaudit.git

2. 切换到 pgAudit 目录：

   .. code:: shell

      cd pgaudit

3. 切换到 ``REL_14_STABLE`` 分支：

   .. code:: shell

      git checkout REL_14_STABLE

4. 安装 pgAudit：

   ::

      make install USE_PGXS=1 PG_CONFIG=/usr/pgsql-14/bin/pg_config

5. 使用 pgAudit 时需关掉 ORCA。

   .. code:: sql

      set optimizer = off;

pgAudit 设置
------------

只有超级用户可以修改设置。如果允许普通用户更改设置，会破坏审计日志的目的。

设置可以在全局级别（在 ``postgresql.conf`` 中或使用 ``ALTER SYSTEM ... SET``\ ）、数据库级别（使用 ``ALTER DATABASE ... SET``\ ）或角色级别（使用 ``ALTER ROLE ... SET``\ ）指定。请注意，设置不能通过普通角色继承，并且 ``SET ROLE`` 不会更改用户的 pgAudit 设置。这是角色系统的一个限制，而不是 pgAudit 的固有限制。

pgAudit 扩展必须在 `shared_preload_libraries <http://www.postgresql.org/docs/14/runtime-config-client.html#GUC-SHARED-PRELOAD-LIBRARIES>`__ 中加载。否则，在加载时会引发错误，不能进行审计日志记录。

此外，在将 ``pgaudit.log_class`` 设置为正确的 pgAudit 功能之前，必须先调用 ``CREATE EXTENSION pgaudit``\ 。该扩展安装了事件触发器，为 DDL 添加了额外的审计功能。pgAudit 将在没有安装扩展的情况下工作，但是 DDL 语句将不会包含有关对象类型和名称的信息。

如果需要删除 ``pgaudit`` 扩展并重新创建，必须首先删除 ``pgaudit.log_class`` 的设置，否则将引发错误。

.. _pgauditlog_class:

pgaudit.log_class
~~~~~~~~~~~~~~~~~

指定会话审计日志记录的语句类别。可能的取值为：

-  READ：当源是关系或查询时，为 ``SELECT`` 和 ``COPY``\ 。
-  WRITE：当目标是关系时，为 ``INSERT``\ 、\ ``UPDATE``\ 、\ ``DELETE``\ 、\ ``TRUNCATE`` 和 ``COPY``\ 。
-  FUNCTION：函数调用和 ``DO`` 块。
-  ROLE：与角色和权限相关的语句，即 ``GRANT``\ 、\ ``REVOKE``\ 、\ ``CREATE/ALTER/DROP ROLE``\ 。
-  DDL：不包括在 ``ROLE`` 类别中的所有 ``DDL``\ 。
-  MISC：其他命令，例如 ``DISCARD``\ 、\ ``FETCH``\ 、\ ``CHECKPOINT``\ 、\ ``VACUUM``\ 、\ ``SET``\ 。
-  MISC_SET：其他 ``SET`` 命令，例如 ``SET ROLE``\ 。
-  ALL：以上所有内容。

可以用逗号分隔的列表提供多个类别，并且可以通过在类别前面加上 ``-`` 符号来减去类别。默认值为 none。

.. _pgauditlog_catalog:

pgaudit.log_catalog
~~~~~~~~~~~~~~~~~~~

-  在语句中的所有关系都在 ``pg_catalog`` 中的情况下，应启用会话日志记录。禁用此设置将减少 psql 和 pgAdmin 等大量查询目录的工具在日志中的干扰。
-  默认设置为 ``on``\ 。

.. _pgauditlog_client:

pgaudit.log_client
~~~~~~~~~~~~~~~~~~

-  指定日志消息是否对客户端进程（如 psql）可见。此设置通常应保持禁用状态，但可能对调试或其他目的有用。
-  请注意，只有当 ``pgaudit.log_client`` 处于打开状态时，才会启用 ``pgaudit.log`` 级别。
-  默认设置为 ``off``\ 。

.. _pgauditlog_level:

pgaudit.log_level
~~~~~~~~~~~~~~~~~

-  指定将用于日志项的日志级别，但请注意，不允许使用 ``ERROR``\ 、\ ``FATAL`` 和 ``PANIC``\ 。此设置用于回归测试，也可能对最终用户的测试或其他目的有用。
-  请注意，只有当 ``pgaudit.log_client`` 处于打开状态时，才会启用 ``pgaudit.log`` 级别；否则将使用默认值。
-  默认为 ``log``\ 。

.. _pgauditlog_parameter:

pgaudit.log_parameter
~~~~~~~~~~~~~~~~~~~~~

-  指定审计日志记录应包括随语句传递的参数。当参数存在时，它们将以 CSV 格式包含在语句文本之后。
-  默认设置为 ``off``\ 。

.. _pgauditlog_relation:

pgaudit.log_relation
~~~~~~~~~~~~~~~~~~~~

-  指定会话审计日志记录是否应为 ``SELECT`` 或 DML 语句中引用的每个关系（\ ``TABLE``\ 、\ ``VIEW`` 等）创建单独的日志条目。这是一个有用的快捷方式，可以在不使用对象审计日志的情况下进行详尽的日志记录。
-  默认设置为 ``off``\ 。

.. _pgauditlog_rows:

pgaudit.log_rows
~~~~~~~~~~~~~~~~

-  指定审计日志记录应包括检索到的行数或受语句影响的行数。启用后，行字段将包含在参数字段之后。
-  默认设置为 ``off``\ 。

.. _pgauditlog_statement:

pgaudit.log_statement
~~~~~~~~~~~~~~~~~~~~~

-  指定日志记录是否包括语句文本和参数（如果已启用）。根据需要，审计日志可能不需要这样做，这会降低日志的详细程度。
-  默认设置为 ``on``\ 。

.. _pgauditlog_statement_once:

pgaudit.log_statement_once
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  指定日志记录是将语句文本和参数与语句/子语句组合的第一个日志条目一起包含，还是与每个条目一起包含。启用此设置将减少详细的日志记录，但可能会使确定生成日志条目的语句变得更加困难，尽管语句/子语句以及进程 ID 应该足以识别使用以前的条目记录的语句文本。
-  默认设置为 ``off``\ 。

.. _pgauditrole:

pgaudit.role
~~~~~~~~~~~~

-  指定用于对象审计日志记录的主角色。可以通过将多个审计角色授予主角色来定义这些角色。这允许多个组负责审计日志的不同方面。
-  没有默认值。

会话审计日志
------------

会话审计日志提供用户在后端执行的所有语句的详细日志。

配置
~~~~

会话日志是通过 ``pgaudit.log_class`` 设置启用的。

为所有 DML 和 DDL 启用会话日志记录，并在 DML 语句中记录所有关系：

.. code:: sql

   set pgaudit.log_class = 'write, ddl';
   set pgaudit.log_relation = on;

为除 ``MISC`` 之外的所有命令启用会话日志，并将审计日志消息升级为 ``NOTICE``\ ：

.. code:: sql

   set pgaudit.log_class = 'all, -misc';
   set pgaudit.log_level = notice;

示例
~~~~

在本例中，会话审计日志用于记录 DDL 和 ``SELECT`` 语句。请注意，由于未启用 ``WRITE`` 类，因此不会记录插入语句。

.. code:: sql

   set pgaudit.log_class = 'read, ddl';

   create table account
   (
       id int,
       name text,
       password text,
       description text
   );

   insert into account (id, name, password, description)
                values (1, 'user1', 'HASH1', 'blah, blah');

   select *
       from account;

日志输出：

.. code:: sql

   AUDIT: SESSION,1,1,DDL,CREATE TABLE,TABLE,public.account,create table account
   (
       id int,
       name text,
       password text,
       description text
   );,<not logged>
   AUDIT: SESSION,2,1,READ,SELECT,,,select *
       from account,,<not logged>

对象审计日志
------------

对象审计日志记录影响特定关系的语句。仅支持 ``SELECT``\ 、\ ``INSERT``\ 、\ ``UPDATE`` 和 ``DELETE`` 命令。\ ``TRUNCATE`` 不包括在对象审计日志中。

对象审计日志记录旨在更细粒度地替换 ``pgaudit.log_class = 'read, write'``\ 。因此，将它们结合使用没有意义，但一种可能的情况是使用会话日志记录来捕获每条语句，然后用对象日志记录来补充，以获得有关特定关系的更多细节。

设置
~~~~

对象级审计日志记录是通过角色系统实现的。\ ``pgaudit.role`` 定义了将用于审计日志记录的角色。当审计角色具有执行命令的权限或从另一个角色继承权限时，将记录关于关系（如 ``TABLE``\ 、\ ``VIEW`` 等）的审计日志。这样，即使在任何上下文中只有一个主角色，您也可以有效地拥有多个审计角色。

将 ``pgaudit.role`` 设置为 ``auditor``\ ，并授予对帐户表的 ``SELECT`` 和 ``DELETE`` 权限。\ ``account`` 表上的任何 ``SELECT`` 或 ``DELETE`` 语句都将被记录：

.. code:: sql

   set pgaudit.role = 'auditor';

   grant select, delete
      on public.account
      to auditor;

.. _示例-1:

示例
~~~~

在本示例中，对象审计日志记录用于说明如何采用细粒度方法来记录 ``SELECT`` 和 DML 语句。请注意，登录 ``account`` 表受列级权限控制，而登录 ``account_role_map`` 表是表级权限。

.. code:: sql

   set pgaudit.role = 'auditor';

   create table account
   (
       id int,
       name text,
       password text,
       description text
   );

   grant select (password)
      on public.account
      to auditor;

   select id, name
     from account;

   select password
     from account;

   grant update (name, password)
      on public.account
      to auditor;

   update account
      set description = 'yada, yada';

   update account
      set password = 'HASH2';

   create table account_role_map
   (
       account_id int,
       role_id int
   );

   grant select
      on public.account_role_map
      to auditor;

   select account.password,
          account_role_map.role_id
     from account
          inner join account_role_map
               on account.id = account_role_map.account_id

日志输出：

.. code:: sql

   AUDIT: OBJECT,1,1,READ,SELECT,TABLE,public.account,select password
     from account,<not logged>
   AUDIT: OBJECT,2,1,WRITE,UPDATE,TABLE,public.account,update account
      set password = 'HASH2',<not logged>
   AUDIT: OBJECT,3,1,READ,SELECT,TABLE,public.account,select account.password,
          account_role_map.role_id
     from account
          inner join account_role_map
               on account.id = account_role_map.account_id,<not logged>
   AUDIT: OBJECT,3,1,READ,SELECT,TABLE,public.account_role_map,select account.password,
          account_role_map.role_id
     from account
          inner join account_role_map
               on account.id = account_role_map.account_id,<not logged>

格式
----

审计条目被写入标准日志记录工具，并包含以下逗号分隔格式的列。只有删除了每个日志项的日志行前缀部分，输出才符合 CSV 格式。

-  **AUDIT_TYPE**\ ：\ ``SESSION`` 或 ``OBJECT``\ 。
-  **STATEMENT_ID**\ ：此会话的唯一语句 ID。每个语句 ID 表示一个后端调用。即使某些语句未被记录，语句 ID 也是连续的。当记录多个关系时，一个语句 ID 可能有多个条目。
-  **SUBSTATEMENT_ID**\ ：主语句中每个子语句的顺序 ID。例如，从查询中调用函数。即使某些子语句未被记录，子语句 ID 也是连续的。当记录多个关系时，一个子语句 ID 可能有多个条目。
-  **CLASS**\ ：例如 ``READ`` 和 ``ROLE``\ 。
-  **COMMAND**\ ：例如 ``ALTER TABLE`` 和 ``SELECT``\ 。
-  **OBJECT_TYPE**\ ：例如 ``TABLE``\ 、\ ``INDEX``\ 、\ ``VIEW``\ 。可用于 ``SELECT``\ 、DML 和大多数 DDL 语句。
-  **OBJECT_NAME**\ ：完全限定的对象名称（例如 ``public.account``\ ）。可用于 ``SELECT``\ 、DML 和大多数 DDL 语句。
-  **STATEMENT**\ ：在后端执行的语句。
-  **PARAMETER**\ ：如果设置了 ``pgaudit.log_parameter``\ ，则此字段将包含引用 CSV 的语句参数，如果没有参数，则包含 ``<none>``\ 。否则，该字段为 ``<not logged>``\ 。

使用 `log_line_prefix <http://www.postgresql.org/docs/14/runtime-config-logging.html#GUC-LOG-LINE-PREFIX>`__ 添加满足审计日志要求所需的任何其他字段。典型的日志行前缀可能是 ``'%m %u %d [%p]: '``\ ，它将为每个审计日志提供日期/时间、用户名、数据库名称和进程 ID。
