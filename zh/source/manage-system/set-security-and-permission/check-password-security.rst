检查密码安全性
==============

本文档介绍 PasswordCheck 插件的使用场景、使用方法和使用限制。PasswordCheck 是 PostgreSQL 内核自带的插件，用于对用户密码的安全性进行校验检查。通过使用该特性，可以避免用户密码出现弱口令问题，提高数据库系统的安全性。

使用场景
--------

通过 SQL 设置密码时，比如 ``CREATE USER ... PASSWORD`` 或 ``ALTER USER ... PASSWORD``\ ，会对密码进行安全性校验。主要会从以下几个方面做弱口令校验：

-  密码长度必须大于 8 位
-  密码中不得包含用户名
-  密码中必须同时包含字母和非字母

使用方法
--------

要使用 PasswordCheck 插件，你可以选择以下任一方式：

-  在 HashData Lightning 集群启动前，使用 vim 手动编辑 ``postgresql.conf`` 配置文件，将 ``shared_preload_libraries`` 配置项的值设为 ``passwordcheck`` 并保存。集群启动时会自动引入 PasswordCheck 插件。

-  在 HashData Lightning 集群启动后，使用以下命令在线修改 ``shared_preload_libraries`` 配置项，并重启集群：

   .. code:: bash

      gpconfig -c shared_preload_libraries -v 'passwordcheck'
      gpstop -ra

配置完成后，每次设置密码时，PasswordCheck 都会对密码进行弱口令检查。

使用限制
--------

PasswordCheck 只支持对非加密的密码进行弱口令校验，不支持对加密后的密码进行校验。对于使用 MD5 或 SCRAM 算法加密的密码，PasswordCheck 只校验其账户名和密码是否相同。
