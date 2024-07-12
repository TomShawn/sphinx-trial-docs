View Database Object Information
===================================

HashData Lightning Web Platform provides information of database objects. On the **Tables** page, you can view detailed information about tables in the database, such as the schema to which the table belongs, the table name, whether the table contains partitions, the table size, the user, and the estimated number of rows. An example page is as follows:

.. image:: /images/web-platform-view-db-object-info-1.png

To access the **Tables** page, you need to:

1. Access the Web Platform dashboard in your browser via ``http://<cluster_node_IP>:7788/``.
2. Click **Tables** in the left navigation menu to enter the page.

View table objects
--------------------

To query the information of a table, you can fill in the drop-down option boxes according to the database, the schema, the table name, and the user. Then click **Query**. The **User** box supports multiple selections.

The fields for the table information are described as follows:

.. list-table::
   :header-rows: 1
   :align: left

   * - Field name
     - Description
   * - Schema
     - The schema to which the table belongs.
   * - Relation Name
     - The table or view name.
   * - Include Partitions
     - Indicates whether the table contains partitions. ``False`` means no, and ``true`` means yes.
   * - Size
     - The storage size that the table occupies.
   * - User
     - The database user to which the table belongs.
   * - Est. Rows
     - The estimated number of rows.
   * - Last Analyzed
     - The last time the table was analyzed for updated statistics.
