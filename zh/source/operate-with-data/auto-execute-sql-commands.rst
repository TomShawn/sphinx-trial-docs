.. raw:: latex

   \newpage

自动化执行 SQL 语句
===================

Create Task 是 HashData Lightning 在 v1.4.0 中引入的功能，你可以通过创建和管理任务 (Task) 来自动执行 SQL 语句或脚本。通过使用 Create Task，你可以按照一定的时间间隔或使用 Cron 表达式来调度任务，并可指定任务要在哪个数据库上运行。

语法说明
--------

CREATE TASK
~~~~~~~~~~~

.. code:: sql

   CREATE TASK [IF NOT EXISTS] <name> SCHEDULE '<num> SECONDS | <cron_expr>'
       [DATABASE <db_name>]
       [USER <username>]
   AS
       <sql>

语句字段解释如下：

-  ``SCHEDULE``\ ：指定 xx 秒执行一次，或者可以使用 Cron 表达式指定。
-  ``DATABASE``\ ：可选，默认是当前数据库的名称。
-  ``USER``\ ：可选，默认是当前用户名。
-  ``<sql>``\ ：需要执行的 SQL 语句。

``cron_expr`` 遵循标准的 cron 表达式规范，如下：

.. code:: none

   ┌───────────── min (0 - 59)
    │ ┌────────────── hour (0 - 23)
    │ │ ┌─────────────── day of month (1 - 31)
    │ │ │ ┌──────────────── month (1 - 12)
    │ │ │ │ ┌───────────────── day of week (0 - 6) (0 to 6 are Sunday to
    │ │ │ │ │                  Saturday, or use names; 7 is also Sunday)
    │ │ │ │ │
    │ │ │ │ │
    * * * * *

其中 ``*`` 表示所在的每个周期都执行，也可以指定一个具体的数字，表示只在这个时间执行。

.. attention:: 

   HashData Lightning 目前不支持类似 0/5 这样的写法，虽然这也是一个有效的 Cron 表达式。

   如果想要在某个周期内循环执行，例如每 5 分钟执行一次，可以这样写：\ ``*/5 * * * *``\ 。

ALTER TASK
~~~~~~~~~~

.. code:: sql

   ALTER TASK [IF EXISTS] <name>
       [SCHEDULE '<num> SECONDS | <cron_expr>']
       [DATABASE <db_name>]
       [USER <username>]
       [ACTIVE | NOT ACTIVE]
       [AS <sql>]

语句字段解释如下：

-  ``SCHEDULE``\ ：指定 xx 秒执行一次，或者 Cron 表达式
-  ``DATABASE``\ ：数据库的名称
-  ``USER``\ ：用户名称
-  ``ACTIVE | NOT ACTIVE``\ ：设置任务为活跃/不活跃
-  ``sql``\ ：需要执行的 SQL 语句

DROP TASK
~~~~~~~~~

.. code:: sql

   DROP TASK [ IF EXISTS ] <name>

.. attention:: 该语句会将此 Task 的执行历史记录都删除掉。

查看 Create Task 元信息
-----------------------

HashData Lightning 目前使用了两张系统表来存储 Task 的相关信息。

``pg_task`` 系统表，主要存储每个 Task 任务，包含其执行周期，执行的 SQL 命令等。

.. code:: sql

   postgres=# \d pg_task
                Table "pg_catalog.pg_task"
     Column  |  Type   | Collation | Nullable | Default
   ----------+---------+-----------+----------+---------
    jobid    | oid     |           | not null |
    schedule | text    | C         |          |
    command  | text    | C         |          |
    nodename | text    | C         |          |
    nodeport | integer |           |          |
    database | text    | C         |          |
    username | text    | C         |          |
    active   | boolean |           |          |
    jobname  | text    | C         |          |
   Indexes:
       "pg_task_jobid_index" PRIMARY KEY, btree (jobid), tablespace "pg_global"
       "pg_task_jobname_username_index" UNIQUE CONSTRAINT, btree (jobname, username), tablespace "pg_global"
   Tablespace: "pg_global"

``pg_task_run_history`` 主要存储了 Task 执行的历史记录，包含执行的 SQL 命令、执行状态、执行结果等。

.. code:: sql

   postgres=# \d pg_task_run_history
                      Table "pg_catalog.pg_task_run_history"
        Column     |           Type           | Collation | Nullable | Default
   ----------------+--------------------------+-----------+----------+---------
    runid          | oid                      |           | not null |
    jobid          | oid                      |           | not null |
    job_pid        | integer                  |           | not null |
    database       | text                     | C         |          |
    username       | text                     | C         |          |
    command        | text                     | C         |          |
    status         | text                     | C         |          |
    return_message | text                     | C         |          |
    start_time     | timestamp with time zone |           |          |
    end_time       | timestamp with time zone |           |          |
   Indexes:
       "pg_task_run_history_runid_index" PRIMARY KEY, btree (runid), tablespace "pg_global"
       "pg_task_run_history_jobid_index" btree (jobid), tablespace "pg_global"
   Tablespace: "pg_global"

调参说明
--------

要调整 HashData Lightning 中 Create Task 的行为，你可以修改以下用户配置参数 GUC 值。

.. attention:: 

   以下 GUC 值均只能通过 ``gpconfig -c -v`` 的方式进行修改。

      -  **task_enable_superuser_jobs**\ ：是否允许执行超级用户的 Task。
      -  **task_host_addr**\ ：数据库服务器地址，用于客户端连接。
      -  **task_log_run**\ ：将 Task 的执行历史记录到系统表中。
      -  **task_log_statement**\ ：每次执行 Task 之前都记录日志。
      -  **task_timezone**\ ：Task 执行的时区
      -  **task_use_background_worker**\ ：使用 background worker 的方式运行 Task。
      -  **max_running_tasks**\ ：最大可执行的 Task 数量。

使用示例
--------

创建示例表

.. code:: sql

   CREATE TABLE task_test (message TEXT) distributed by (message);

创建 Task，每三秒执行一次，向表中插入一条记录。

.. code:: none

   CREATE TASK insert_hello SCHEDULE '3 seconds' AS $$INSERT INTO task_test values ('Hello')$$;
