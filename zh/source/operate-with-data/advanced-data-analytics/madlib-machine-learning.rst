使用 MADlib 进行机器学习和深度学习
==================================

MADlib 是一个开源库，提供可扩展的数据库内分析功能。它为结构化和非结构化数据实现了数据并行的数学、统计和机器学习算法。

在 HashData Lightning 数据库中，可以通过安装 MADlib 扩展来使用 MADlib 的功能。MADlib 提供了一套基于 SQL 的机器学习、数据挖掘和统计算法，可以在数据库引擎内大规模运行，无需在数据库和其他工具之间传输数据。

使用 MADlib 可以利用数据库的可扩展性和性能，在熟悉的 SQL 环境中执行分析，提高了工作效率。它克服了在数据库外部工具的内存/CPU 限制。

安装 MADlib 组件
----------------

要在 Greenplum 数据库上安装 MADlib，首先需要安装兼容的 HashData Lightning MADlib 包，然后在目标数据库上安装 MADlib 函数库。

``gppkg`` 工具用于在 HashData Lightning 集群的所有主机上安装数据库扩展及其依赖项。\ ``gppkg`` 还会在系统扩展或 Segment 恢复的情况下自动在新主机上安装扩展。

安装 HashData Lightning MADlib 包
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在安装 MADlib 包之前，确保 HashData Lightning 数据库正在运行，已经设置了 ``greenplum_path.sh``\ ，并且已经设置了 ``$MASTER_DATA_DIRECTORY`` 和 ``$GPHOME`` 变量。

1. 获取 MADlib 扩展包。

2. 将 MADlib 包复制到 HashData Lightning 的 Coordinator 节点主机上。

3. 解压 MADlib 扩展包，示例如下：

   .. code:: shell

      $ tar xzvf madlib-1.21.0+1-gp5-rhel7-x86_64.tar.gz

4. 使用 ``gppkg`` 工具安装软件包，示例如下：

   .. code:: shell

      $ gppkg -i ./madlib-1.21.0+1-gp5-rhel7-x86_64/madlib-1.21.0+1-gp5-rhel7-x86_64.gppkg

将 MADlib 功能添加至数据库
--------------------------

在安装了 MADlib 包之后，运行 ``madpack`` 命令将 MADlib 函数添加到 HashData Lightning 中。\ ``madpack`` 位于 ``$GPHOME/madlib/bin`` 目录。

.. code:: shell

   $ $GPHOME/madlib/bin/madpack install [-s <schema_name>] -p cloudberry -c <user>@<host>:<port>/<database>

例如，要在服务器为 ``mdw`` 、端口为 ``5432`` 的 ``testdb`` 数据库中创建 MADlib 函数。在 ``madpack`` 命令中指定以 ``gpadmin`` 用户身份登录，并提示输入密码。目标 schema 是 ``madlib``\ 。

.. code:: shell

   $ $GPHOME/madlib/bin/madpack install -s madlib -p cloudberry -c gpadmin@mdw:5432/testdb

安装完函数后，HashData Lightning 数据库的超级用户角色 ``gpadmin`` 应该将目标 schema（以上示例中为 ``madlib``\ ）的所有权限授予给将要访问 MADlib 函数的用户。如果没有访问权限，用户在尝试访问目标 schema 时会遇到报错 ``ERROR: permission denied for schema MADlib``\ 。

从数据库中卸载 MADlib
---------------------

要将 MADlib 组件从 HashData Lightning 集群中卸载，使用 ``madpack uninstall`` 命令。以下示例命令从 ``testdb`` 数据库中移除 MADlib 对象。移除的同时，依赖 MADlib 的 schema 以及其他数据库对象都会被移除。

.. code:: shell

   $ $GPHOME/madlib/bin/madpack uninstall -s madlib -p cloudberry -c gpadmin@mdw:5432/testdb

使用示例
--------

查看 MADlib 的版本号
~~~~~~~~~~~~~~~~~~~~

.. code:: sql

   SELECT version FROM madlib.migrationhistory ORDER BY applied DESC LIMIT 1;

场景一：在数据库表上执行线性回归运算
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

以下示例在表 ``regr_example`` 上运行线性回归。因变量数据在 ``y`` 列，自变量数据在 ``x1`` 和 ``x2`` 列。

下面的语句创建 ``regr_example`` 表并加载一些样本数据：

.. code:: sql

   DROP TABLE IF EXISTS regr_example;
   CREATE TABLE regr_example (
      id int,
      y int,
      x1 int,
      x2 int
   );
   INSERT INTO regr_example VALUES 
      (1,  5, 2, 3),
      (2, 10, 7, 2),
      (3,  6, 4, 1),
      (4,  8, 3, 4);

MADlib 的 ``linregr_train()`` 函数从包含训练数据的输入表中生成回归模型。以下 ``SELECT`` 语句在 ``regr_example`` 表上运行简单的多元回归，并将模型保存在 ``reg_example_model`` 表中。

.. code:: sql

   SELECT madlib.linregr_train (
      'regr_example',         -- 源表
      'regr_example_model',   -- 输出模型表
      'y',                    -- 因变量
      'ARRAY[1, x1, x2]'      -- 自变量
   );

``madlib.linregr_train()``
函数可以有其他参数来设置分组列，并计算模型的异方差性。

.. attention:: 通过将一个自变量设置为常量 ``1`` 来计算截距，如前面的示例所示。

对 ``regr_example`` 表运行此查询会创建包含一行数据的 ``regr_example_model`` 表：

.. code:: sql

   SELECT * FROM regr_example_model;

                               coef                            |         r2        
    |                          std_err                           |                 
           t_stats                          |                           p_values   
                           |    condition_no    | num_rows_processed | num_missing_
   rows_skipped |                                                                  
                      variance_covariance                                          
                                               
   ------------------------------------------------------------+-------------------
   -+------------------------------------------------------------+-----------------
   -----------------------------------------+--------------------------------------
   ------------------------+--------------------+--------------------+-------------
   -------------+------------------------------------------------------------------
   --------------------------------------------------------------------------------
   --------------------------------------------
    {0.11111111111112681,1.148148148148149,1.0185185185185155} | 0.9686126804771108
    | {1.4958791130923574,0.2070433312499029,0.3464497580344945} | {0.0742781352708
   5907,5.545448584201562,2.93987366103776} | {0.9527997481474364,0.113579771006374
   09,0.20873079069527753} | 22.650203241881005 |                  4 |             
              0 | {{2.2376543209859783,-0.2572016460903422,-0.4372427983535821},{-0
   .2572016460903422,0.042866941015057024,0.034293552812045644},{-0.437242798353582
   1,0.03429355281204565,0.12002743484215979}}
   (1 row)

保存在 ``regr_example_model`` 表中的模型可以与 MADlib 线性回归预测函数 ``madlib.linregr_predict()`` 一起使用，以查看残差：

.. code:: sql

   SELECT regr_example.*, 
           madlib.linregr_predict ( ARRAY[1, x1, x2], m.coef ) as predict,
           y - madlib.linregr_predict ( ARRAY[1, x1, x2], m.coef ) as residual
   FROM regr_example, regr_example_model m;

    id | y  | x1 | x2 |      predict       |      residual       
   ----+----+----+----+--------------------+---------------------
     4 |  8 |  3 |  4 |  7.629629629629636 |   0.370370370370364
     1 |  5 |  2 |  3 |  5.462962962962971 | -0.4629629629629708
     2 | 10 |  7 |  2 | 10.185185185185201 | -0.1851851851852011
     3 |  6 |  4 |  1 |  5.722222222222238 |  0.2777777777777617
   (4 rows)

场景二：使用关联规则
~~~~~~~~~~~~~~~~~~~~

以下示例演示了在交易数据集上使用关联规则数据挖掘技术。关联规则挖掘是一种在大型数据集中发现变量之间关系的技术。以下示例考虑了在商店中经常一起购买的商品。

该示例使用 MADlib 函数 ``MADlib.assoc_rules`` 分析存储在表中的七个事务的购买信息。该函数假设数据存储在两列中，每行一个单项和事务 ID。包含多个项目的事务由多行组成，每个项目一行。

1. 创建测试表：

   .. code:: sql

      DROP TABLE IF EXISTS test_data;
      CREATE TABLE test_data (
      trans_id INT,
      product text
      );

2. 向表中添加数据。

   .. code:: sql

      INSERT INTO test_data VALUES 
      (1, 'beer'),
      (1, 'diapers'),
      (1, 'chips'),
      (2, 'beer'),
      (2, 'diapers'),
      (3, 'beer'),
      (3, 'diapers'),
      (4, 'beer'),
      (4, 'chips'),
      (5, 'beer'),
      (6, 'beer'),
      (6, 'diapers'),
      (6, 'chips'),
      (7, 'beer'),
      (7, 'diapers');

MADlib 函数 ``madlib.assoc_rules()`` 分析数据并确定具有以下特征的关联规则：

-  支持度至少为 .40。支持度是包含 X 的事务占所有事务的比率。
-  置信度至少为 .75。置信度是包含 X 的事务占包含 Y 的事务的比率。可以将此指标视为给定 Y 的 X 的条件概率。

以下 ``SELECT`` 命令确定关联规则，创建表 ``assoc_rules``\ ，并将统计信息添加到表中。

.. code:: sql

   SELECT * FROM madlib.assoc_rules (
      .40,          -- 支持度
      .75,          -- 置信度
      'trans_id',   -- 事务列
      'product',    -- 购买产品列
      'test_data',  -- 表名
      'public',     -- 模式名
      false);       -- 显示处理细节

以上命令输出如下，有两条规则符合这些特征。

.. code:: sql

   output_schema | output_table | total_rules |   total_time    
   ---------------+--------------+-------------+-----------------
    public        | assoc_rules  |           2 | 00:00:04.340151
   (1 row)

要查看关联规则，运行以下 ``SELECT`` 命令。

.. code:: sql

   SELECT pre, post, support FROM assoc_rules
      ORDER BY support DESC;

以下是输出。\ ``pre`` 和 ``post`` 列分别是关联规则左右两侧的项集。

.. code:: sql

   pre    |  post  |       support       
   -----------+--------+---------------------
    {diapers} | {beer} |  0.7142857142857143
    {chips}   | {beer} | 0.42857142857142855
   (2 rows)

场景三：进行朴素贝叶斯分类运算
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

朴素贝叶斯分析根据一个或多个独立变量 (属性) 预测类变量或类别的结果可能性。类变量是非数值的分类变量，是一个只能取有限数量值或类别的变量。类变量用整数表示，每个整数代表一个类别。例如，如果类别可以是 "true"、"false" 或 "unknown"，则可用整数 1、2 或 3 表示。

属性可以是数值类型和非数值类型的分类类型。训练函数有两个签名 - 一个用于所有属性都是数值类型的情况,另一个用于混合数值和分类类型。后者的附加参数标识应被视为数值的属性。属性以数组的形式提交给训练函数。

MADlib 朴素贝叶斯训练函数产生特征概率表和类先验表，这些表可以与预测函数一起使用，为属性集合提供类别的概率。

朴素贝叶斯示例 1 - 简单的全数值属性
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

在以下示例中，\ ``class`` 变量要么是 1 要么是 2，有三个整数属性。

1. 以下命令创建输入表并加载示例数据。

   .. code:: sql

      DROP TABLE IF EXISTS class_example CASCADE;
      CREATE TABLE class_example (
      id int, class int, attributes int[]);
      INSERT INTO class_example VALUES
      (1, 1, '{1, 2, 3}'),
      (2, 1, '{1, 4, 3}'),
      (3, 2, '{0, 2, 2}'),
      (4, 1, '{1, 2, 1}'),
      (5, 2, '{1, 2, 2}'),
      (6, 2, '{0, 1, 3}');

   实际生产场景中的数据比这个示例数据更丰富，会获得更好的结果。随着训练数据集的增大，分类的准确性会显著提高。

2. 使用 ``create_nb_prepared_data_tables()`` 函数训练模型。

   .. code:: sql

      SELECT * FROM madlib.create_nb_prepared_data_tables (
          'class_example',         -- 训练表名
          'class',                 -- 类(因变量)列名 
          'attributes',            -- 属性列名
          3,                       -- 属性数量
          'example_feature_probs', -- 特征概率输出表名
          'example_priors'         -- 类先验输出表名
          );

3. 创建一个包含要使用该模型进行分类的数据表。

   .. code:: sql

      DROP TABLE IF EXISTS class_example_topredict;

      CREATE TABLE class_example_topredict ( 
          id int, attributes int[]);

      INSERT INTO class_example_topredict VALUES
          (1, '{1, 3, 2}'),
          (2, '{4, 2, 2}'),
          (3, '{2, 1, 1}');

4. 使用特征概率表、类先验表和 ``class_example_topredict`` 表创建分类视图。

   .. code:: sql

      SELECT madlib.create_nb_probs_view (
          'example_feature_probs',    -- 特征概率输出表
          'example_priors',           -- 类先验输出表  
          'class_example_topredict',  -- 待分类数据表
          'id',                       -- 键列名
          'attributes',               -- 属性列名
          3,                         -- 属性数量
          'example_classified'       -- 要创建的视图名
          );

5. 显示分类结果。

   .. code:: sql

      SELECT * FROM example_classified;

      key | class |       nb_prob       
      -----+-------+---------------------
      1 |     1 |                 0.4
      1 |     2 |  0.5999999999999999
      2 |     1 | 0.24999999999999992
      2 |     2 |                0.75
      3 |     1 |                 0.5
      3 |     2 |                 0.5
      (6 rows)

朴素贝叶斯示例 2 - 天气和户外运动
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

这个例子根据天气条件计算用户进行户外运动，如高尔夫或网球的概率。

``weather_example`` 表包含示例值。该表的标识列是 ``day``\ ，是整数类型。

``play`` 列保存了因变量，有两个分类：

-  0 - 否
-  1 - 是

有四个属性：\ ``outlook``\ （天气状况）、\ ``temperature``\ （温度）、\ ``humidity``\ （湿度）和 ``wind``\ （风力）。这些都是分类变量。MADlib 的 ``create_nb_classify_view()`` 函数期望属性作为 ``INTEGER``\ 、\ ``NUMERIC`` 或 ``FLOAT8`` 值的数组提供，因此这个示例的属性用整数编码如下：

-  ``outlook`` 可能是 ``sunny(1)``\ 、\ ``overcast(2)`` 或 ``rain(3)``\ 。
-  ``temperature`` 可能是 ``hot(1)``\ 、\ ``mild(2)`` 或 ``cool(3)``\ 。
-  ``humidity`` 可能是 ``high(1)`` 或 ``normal(2)``\ 。
-  ``wind`` 可能是 ``strong(1)`` 或 ``weak(2)``\ 。

下表显示了训练数据，变量编码前的情况。

.. code:: sql

   day | play | outlook  | temperature | humidity | wind
   -----+------+----------+-------------+----------+--------
    2   | No   | Sunny    | Hot         | High     | Strong
    4   | Yes  | Rain     | Mild        | High     | Weak
    6   | No   | Rain     | Cool        | Normal   | Strong
    8   | No   | Sunny    | Mild        | High     | Weak
   10   | Yes  | Rain     | Mild        | Normal   | Weak
   12   | Yes  | Overcast | Mild        | High     | Strong
   14   | No   | Rain     | Mild        | High     | Strong
    1   | No   | Sunny    | Hot         | High     | Weak
    3   | Yes  | Overcast | Hot         | High     | Weak
    5   | Yes  | Rain     | Cool        | Normal   | Weak
    7   | Yes  | Overcast | Cool        | Normal   | Strong
    9   | Yes  | Sunny    | Cool        | Normal   | Weak
   11   | Yes  | Sunny    | Mild        | Normal   | Strong
   13   | Yes  | Overcast | Hot         | Normal   | Weak
   (14 rows)

1. 创建训练表：

   .. code:: sql

      DROP TABLE IF EXISTS weather_example;
      CREATE TABLE weather_example (
      day int,
      play int,
      attrs int[]
      );
      INSERT INTO weather_example VALUES
      ( 2, 0, '{1,1,1,1}'), -- sunny, hot, high, strong
      ( 4, 1, '{3,2,1,2}'), -- rain, mild, high, weak
      ( 6, 0, '{3,3,2,1}'), -- rain, cool, normal, strong
      ( 8, 0, '{1,2,1,2}'), -- sunny, mild, high, weak
      (10, 1, '{3,2,2,2}'), -- rain, mild, normal, weak
      (12, 1, '{2,2,1,1}'), -- etc.
      (14, 0, '{3,2,1,1}'),
      ( 1, 0, '{1,1,1,2}'),
      ( 3, 1, '{2,1,1,2}'),
      ( 5, 1, '{3,3,2,2}'),
      ( 7, 1, '{2,3,2,1}'),
      ( 9, 1, '{1,3,2,2}'),
      (11, 1, '{1,2,2,1}'),
      (13, 1, '{2,1,2,2}');

2. 从训练表中创建模型：

   .. code:: sql

      SELECT madlib.create_nb_prepared_data_tables (
          'weather_example',  -- 训练源表
          'play',             -- 因变量列
          'attrs',            -- 属性列
          4,                  -- 属性数量
          'weather_probs',    -- 特征概率输出表
          'weather_priors'    -- 类先验
          );

3. 查看特征概率：

   .. code:: sql

      SELECT * FROM weather_probs;

      class | attr | value | cnt | attr_cnt 
      -------+------+-------+-----+----------
          0 |    3 |     1 |   4 |        2
          1 |    2 |     3 |   3 |        3
          0 |    2 |     3 |   1 |        3
          1 |    1 |     1 |   2 |        3
          1 |    2 |     1 |   2 |        3
          1 |    2 |     2 |   4 |        3
          1 |    4 |     1 |   3 |        2
          0 |    2 |     1 |   2 |        3
          0 |    1 |     1 |   3 |        3
          0 |    2 |     2 |   2 |        3
          0 |    4 |     1 |   3 |        2
          1 |    3 |     2 |   6 |        2
          0 |    3 |     2 |   1 |        2
          0 |    1 |     2 |   0 |        3
          1 |    1 |     3 |   3 |        3
          1 |    4 |     2 |   6 |        2
          0 |    1 |     3 |   2 |        3
          1 |    1 |     2 |   4 |        3
          1 |    3 |     1 |   3 |        2
          0 |    4 |     2 |   2 |        2
      (20 rows)

4. 要使用模型对一组记录进行分类，首先需将数据加载到一个表中。在此示例中，表 ``t1`` 有四行待分类。

   .. code:: sql

      DROP TABLE IF EXISTS t1;
      CREATE TABLE t1 (
          id integer,
          attributes integer[]);
          
      insert into t1 values
          (1, '{1, 2, 1, 1}'),
          (2, '{3, 3, 2, 1}'),
          (3, '{2, 1, 2, 2}'),
          (4, '{3, 1, 1, 2}');

5. 使用 MADlib 的 ``create_nb_classify_view()`` 函数对表中的行进行分类。

   .. code:: sql

      SELECT madlib.create_nb_classify_view (
          'weather_probs',      -- 特征概率表
          'weather_priors',     -- 类先验名称
          't1',                 -- 包含待分类值的表
          'id',                 -- 键列
          'attributes',         -- 属性列
          4,                    -- 属性数量
          't1_out'              -- 输出表名
      );

   结果是四行，每行对应 ``t1`` 表中的一条记录。

   .. code:: sql

      SELECT * FROM t1_out ORDER BY key;
      key | nb_classification
      -----+-------------------
      1 | {0}
      2 | {1}
      3 | {1}
      4 | {0}
      (4 rows)
