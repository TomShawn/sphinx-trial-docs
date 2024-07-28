.. raw:: latex

   \newpage

使用 PostGIS 进行地理空间数据分析
=================================

PostGIS 是 PostgreSQL 的一个空间数据库扩展功能，它使数据库能够存储地理信息系统 (GIS) 对象。HashData Lightning 对 PostGIS 的扩展支持包括了一些可选功能，如基于 GiST 的 R-Tree 空间索引，以及分析和处理 GIS 对象的函数。此外，它还支持 PostGIS 的 Raster 数据类型。PostGIS Raster 和 PostGIS 的几何数据类型共同提供了一组覆盖 SQL 函数（例如 ``ST_Intersects``\ ），使得矢量和 Raster 类型的地理空间数据可以无缝结合处理。PostGIS Raster 采用了 GDAL（地理空间数据抽象库）作为其 Raster 地理空间数据格式的转换库，向应用程序提供了统一的 Raster 数据模型。

关于 HashData Lightning 对 PostGIS 扩展的支持详情，请参考 :ref:`PostGIS 扩展的支持与限制说明 <operate-with-data/advanced-data-analytics/postgis-analyses:postgis 扩展使用限制>`\ 。

想要了解更多关于 PostGIS 的信息，可以参考 https://postgis.net/\ 。

关于 GDAL 的更多信息，请访问 https://gdal.org/\ 。

添加扩展
--------

以下步骤用于启用 PostGIS 扩展和与 PostGIS 一起使用的扩展。

1. 要在数据库中启用 PostGIS 和 PostGIS Raster，请在登录数据库后执行以下命令。

   .. code:: sql

      CREATE EXTENSION postgis;

   如果要在特定 schema 中启用 PostGIS 和 PostGIS Raster，请先创建 schema，将 ``search_path`` 设置为 PostGIS schema，然后使用 ``WITH SCHEMA`` 子句启用 ``postgis`` 扩展。

   .. code:: sql

      SHOW search_path; -- 查看当前的 search_path
      CREATE SCHEMA <schema_name>;
      SET search_path TO <schema_name>;
      CREATE EXTENSION postgis WITH SCHEMA <schema_name>;

   启用扩展后，重置 ``search_path``\ 。如果需要，可在 ``search_path`` 中包含 PostGIS schema。

2. 如果需要，可在启用 ``postgis`` 扩展后启用 PostGIS TIGER 地理编码器。

   要启用 PostGIS TIGER 地理编码器，你需要在启用 ``postgis_tiger_geocoder`` 之前启用 ``fuzzystrmatch`` 扩展。以下两个命令用于启用相关扩展。

   .. code:: sql

      CREATE EXTENSION fuzzystrmatch;
      CREATE EXTENSION postgis_tiger_geocoder;

3. 如果需要，你还可以启用基于规则的地址标准化器并为标准化器添加规则表。

   .. code:: sql

      CREATE EXTENSION address_standardizer;
      CREATE EXTENSION address_standardizer_data_us;

开启 GDAL 栅格驱动
------------------

PostGIS 处理栅格数据时，例如在执行 ``ST_AsJPEG()`` 等函数时，需要借助 GDAL 栅格驱动。但默认设置下，所有的栅格驱动都是不启用的。要启用栅格驱动，需要在所有 HashData Lightning 集群主机的 ``greenplum_path.sh`` 文件中配置 ``POSTGIS_GDAL_ENABLED_DRIVERS`` 环境变量。

另一种方式是在会话级别进行设置，直接修改 ``postgis.gdal_enabled_drivers`` 参数。例如，在 HashData Lightning 的一个会话中，以下 ``SET`` 命令可以启用 3 种 GDAL 栅格驱动。

.. code:: sql

   SET postgis.gdal_enabled_drivers TO 'GTiff PNG JPEG';

以下 ``SET`` 命令将会话中启用的驱动设置为默认值。

.. code:: sql

   SET postgis.gdal_enabled_drivers = default;

要查看 HashData Lightning 系统支持的 GDAL 栅格驱动列表，请在 HashData Lightning coordinator 上运行 ``raster2pgsql`` 工具，并使用 ``-G`` 选项。

.. code:: shell

   raster2pgsql -G

该命令会显示驱动的长格式名称。GDAL 栅格驱动表，可以在 https://gdal.org/drivers/raster/index.html 查到，该表列出了长格式名称及其对应的代码，这些代码可被设定为环境变量的值。例如，长名称 Portable Network Graphics 的代码是 PNG。以下示例的 ``export`` 命令启用了 4 个 GDAL 栅格驱动。

.. code:: shell

   export POSTGIS_GDAL_ENABLED_DRIVERS="GTiff PNG JPEG GIF"

使用 ``gpstop -r`` 命令重启 HashData Lightning 系统，使 ``greenplum_path.sh`` 文件中更新的设置生效。

在所有主机上更新 ``greenplum_path.sh`` 文件并重启 HashData Lightning 系统后，可以通过 ``ST_GDALDrivers()`` 函数显示已启用的栅格驱动。该 ``SELECT`` 命令会列出所有已启用的栅格驱动。

.. code:: sql

   SELECT short_name, long_name FROM ST_GDALDrivers();

启用外部数据库栅格功能
----------------------

安装 PostGIS 后，系统默认不开启外部数据库栅格支持，这一设置在 ``greenplum_path.sh`` 文件中的 ``POSTGIS_ENABLE_OUTDB_RASTERS`` 项被置为 ``0``\ 。如果需要启用这一功能，你需要将该参数值改为 ``true``\ （即任何非零值），并且在所有主机上做同样的修改，然后重启 HashData Lightning 系统。

此外，你也可以只在当前的 HashData Lightning 会话中开启或关闭这一功能。例如，用以下的 ``SET`` 命令可以仅为当前会话启用这一功能。

.. code:: sql

   SET postgis.enable_outdb_rasters = true;

**注意**

启用外部数据库栅格后，可以通过服务器配置参数 ``postgis.gdal_enabled_drivers`` 来决定使用哪些栅格格式。

移除 PostGIS 支持
-----------------

要移除 PostGIS 扩展及其相关扩展的支持，你需要使用 ``DROP EXTENSION``
命令。

从数据库中移除 PostGIS 支持并不会从 ``greenplum_path.sh`` 文件中删除这些 PostGIS 栅格环境变量：\ ``GDAL_DATA``\ 、\ ``POSTGIS_ENABLE_OUTDB_RASTERS``\ 、\ ``POSTGIS_GDAL_ENABLED_DRIVERS``\ 。

**警告**

从数据库中移除 PostGIS 支持会在不进行任何预警的情况下删除数据库中的 PostGIS 数据对象。用户如果正在访问 PostGIS 对象，可能会干扰删除过程。

使用 ``DROP EXTENSION`` 命令
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

根据你为 PostGIS 启用的扩展，可以从数据库中移除这些扩展的支持。

-  如果你启用了地址标准化器和示例规则表，使用以下命令从当前数据库中移除扩展支持。

   .. code:: sql

      DROP EXTENSION IF EXISTS address_standardizer_data_us;
      DROP EXTENSION IF EXISTS address_standardizer;

-  如果你启用了 TIGER 地理编码器和 ``fuzzystrmatch`` 扩展，使用以下命令从当前数据库中移除扩展支持。

   .. code:: sql

      DROP EXTENSION IF EXISTS postgis_tiger_geocoder;
      DROP EXTENSION IF EXISTS fuzzystrmatch;

-  移除 PostGIS 和 PostGIS 栅格的支持。使用以下命令从当前数据库中移除扩展支持。

   .. code:: sql

      DROP EXTENSION IF EXISTS postgis;

-  如果你启用了 PostGIS 支持，并且在 ``CREATE EXTENSION`` 命令中指定了特定的架构，你可以根据需要更新 ``search_path`` 并移除 PostGIS 架构。

使用示例
--------

场景一：使用 PostGIS 在数据库中创建非 OpenGIS 表并插入和查询各种几何对象
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sql

   -- 创建一个名为 geom_test 的表。
   CREATE TABLE geom_test ( gid int4, geom geometry, 
     name varchar(25) );

   -- 向表中插入一行数据，gid 为 1,geometry 字段使用 WKT 格式表示一个三维多边形对象（一个三维正方形）,name 为 '3D Square'。
   INSERT INTO geom_test ( gid, geom, name )
     VALUES ( 1, 'POLYGON((0 0 0,0 5 0,5 5 0,5 0 0,0 0 0))', '3D Square');
     
   -- 插入第二行数据，gid 为 2，geometry 为一条三维线串，name 为 '3D Line'。
   INSERT INTO geom_test ( gid, geom, name ) 
     VALUES ( 2, 'LINESTRING(1 1 1,5 5 5,7 7 5)', '3D Line' );
     
   -- 插入第三行，gid 为 3，geometry 为一个二维多点对象，name 为 '2D Aggregate Point'。
   INSERT INTO geom_test ( gid, geom, name )
     VALUES ( 3, 'MULTIPOINT(3 4,8 9)', '2D Aggregate Point' );

   -- 先使用 ST_GeomFromEWKT 从 EWKT 构造一个三维线串对象
   -- 然后用 Box3D 获取该对象的三维边界框。再使用 && 操作符查询 geom_test 表中的 geom 字段与该边界框相交的所有行。
   SELECT * from geom_test WHERE geom &&
     Box3D(ST_GeomFromEWKT('LINESTRING(2 2 0, 3 3 0)'));

场景二：使用 PostGIS 创建包含地理参考的表，插入地理编码点数据，以及输出点数据为标准文本格式
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sql

   -- 创建一个名为 geotest 的表。
   CREATE TABLE geotest (id INT4, name VARCHAR(32) );

   -- 为表 geotest 添加一个名为 geopoint 的 geometry 列，定义为 POINT 点类型
   -- 坐标维度为 2，并指定其空间参考系统 (SRID) 为 4326（代表 WGS84 地理坐标系）。
   SELECT AddGeometryColumn('geotest','geopoint', 4326,'POINT',2);

   -- 插入第一行数据，id 为 1，name 为 'Olympia'，geopoint 是使用 ST_GeometryFromText
   -- 从 WKT 文本构造的一个点对象，其坐标为 (-122.90, 46.97)，SRID 为 4326。
   INSERT INTO geotest (id, name, geopoint)
     VALUES (1, 'Olympia', ST_GeometryFromText('POINT(-122.90 46.97)', 4326));
     
   -- 插入第二行数据，id 为 2，name 为 'Renton'
   -- 点坐标为 (-122.22, 47.50)，SRID 同样为 4326。
   INSERT INTO geotest (id, name, geopoint)
     VALUES (2, 'Renton', ST_GeometryFromText('POINT(-122.22 47.50)', 4326));

   -- 从 geotest 表中选择 name 和 geopoint 字段,但将 geopoint 字段使用
   -- ST_AsText 函数转换为标准文本 (WKT) 格式输出。
   SELECT name,ST_AsText(geopoint) FROM geotest;

场景三：支持空间索引功能
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sql

   -- 创建表格
   CREATE TABLE spatial_data (
     id SERIAL PRIMARY KEY,
     geom geometry
   );

   -- 插入数据
   INSERT INTO spatial_data (geom) VALUES 
   (ST_GeomFromText('POINT(0 0)')),
   (ST_GeomFromText('POINT(1 1)')),
   (ST_GeomFromText('POLYGON((0 0, 4 0, 4 4, 0 4, 0 0))'));

   -- 创建空间索引
   CREATE INDEX spatial_data_gist_idx
     ON spatial_data
     USING GIST (geom);

PostGIS 支持与使用限制
----------------------

本节介绍了 HashData Lightning PostGIS 扩展支持的功能及其限制。通常情况下，HashData Lightning PostGIS 扩展不支持以下几项功能：

-  PostGIS 的拓扑扩展 (``postgis_topology``)
-  PostGIS 的 3D 和地理处理扩展 (``postgis_sfcgal``)
-  一些用户自定义的函数和聚合操作
-  PostGIS 的长时间事务处理

支持的 PostGIS 数据类型
~~~~~~~~~~~~~~~~~~~~~~~

HashData Lightning PostGIS 扩展支持以下 PostGIS 数据类型：

-  ``box2d``
-  ``box3d``
-  ``geometry``
-  ``geography``

有关完整的 PostGIS 数据类型、操作符和函数，参见 `PostGIS 参考文档 <https://postgis.net/docs/manual-3.3/reference.html>`__\ 。

支持的 PostGIS 索引
~~~~~~~~~~~~~~~~~~~

HashData Lightning 的 PostGIS 扩展支持 GiST (Generalized Search Tree) 索引。

PostGIS 扩展使用限制
~~~~~~~~~~~~~~~~~~~~

本节列出了 HashData Lightning 的 PostGIS 扩展对用户定义函数 (UDF)、数据类型和聚合方面的限制。

-  HashData Lightning 不支持与 PostGIS 拓扑功能相关的数据类型和函数，例如 ``TopoGeometry``\ 。

-  HashData Lightning 不支持以下 PostGIS 聚合：

   -  ``ST_Collect``

   -  ``ST_MakeLine``

   在拥有多个 Segment 的 HashData Lightning 集群中，如果连续多次调用同一聚合函数，可能会得到不同的结果。

-  HashData Lightning 不支持 PostGIS 的长时间事务处理。

   PostGIS 依赖于触发器和 PostGIS 表 ``public.authorization_table`` 来实现长时间事务的支持。当 PostGIS 尝试锁定长时间事务时，HashData Lightning 会报错，指出函数无法访问名为 ``authorization_table`` 的表。

-  HashData Lightning 不支持 ``_postgis_index_extent`` 函数。

-  ``<->`` 操作符 (``geometry <-> geometry``) 用于返回两个几何体中心点之间的距离。

-  HashData Lightning 支持 TIGER 地理编码器扩展，但不支持升级 TIGER 地理编码器扩展。

-  ``standardize_address()`` 函数采用 ``lex``\ 、\ ``gaz`` 或 ``rules`` 表作为参数。如果你使用的是除了 ``us_lex``\ 、\ ``us_gaz`` 或 ``us_rules`` 之外的表，你应该将它们设置为 ``DISTRIBUTED REPLICATED`` 分布策略，以确保它们在 HashData Lightning 上能正常工作。
