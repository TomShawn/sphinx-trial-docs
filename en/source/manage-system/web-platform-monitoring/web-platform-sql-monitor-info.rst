View SQL Monitoring Information
=================================

HashData Lightning Web Platform provides monitoring information for SQL statements being executed in the database. On the **Query Monitor** page, you can see the execution status and details of each SQL statement,  and the status of each database session. An example is as follows:

.. image:: /images/web-platform-view-sql-monitor-info-1.png

Access the page
-----------------

To access the **Query Monitor** page, you need to:

1. Access the Web Platform dashboard in your browser via ``http://<cluster_node_IP>:7788/``.
2. Click **Query Monitor** in the left navigation menu to enter the page.

View SQL execution status
-----------------------------

To view the execution status of a SQL statement, click the **Query Status** tab.

In the search area, fill in the corresponding drop-down option box according to the execution status of the SQL statement, the user, and the database. Then click **Query** to search. The **User** box supports multiple selections.

The options in the **Status** drop-down box are described as follows:

.. list-table::
   :header-rows: 1
   :align: left

   * - Option name
     - Description
   * - Running
     - The SQL statement is being executed.
   * - Done
     - The SQL statement has been executed.
   * - Abort
     - The SQL statement has been aborted.
   * - Canceling
     - SQL statement is being canceled.

After clicking **Query**, a SQL list will be displayed in the area below, and you should be able to find the target SQL statement from the list. The fields of the SQL list are described as follows:

.. list-table::
   :header-rows: 1
   :align: left

   * - Field name
     - Description
   * - Query ID
     - Identifies the unique ID of the SQL statement being executed in the database.
   * - Status
     - The status of the SQL statement execution.
   * - User
     - The user who executes the SQL statement.
   * - Database
     - The database where the SQL statement is executed.
   * - Submitted Time
     - The time when the SQL statement was submitted.
   * - Queue Time
     - The queue time before executing the SQL statement.
   * - Run Time
     - The execution time of the SQL statement.
   * - Operation
     - For a SQL statement, you can click Cancel Query to cancel the SQL statement.

Cancel SQL execution
~~~~~~~~~~~~~~~~~~~~~~

To cancel one or more SQL statements, locate the **Operation** column of the corresponding SQL statement in the SQL list, and then click **Cancel Query**.

.. image:: /images/web-platform-view-sql-monitor-info-2.png

View SQL details
~~~~~~~~~~~~~~~~~~

To view the details of a SQL statement, click the query ID of the SQL statement, and then enter the details page.

.. image:: /images/web-platform-view-sql-monitor-info-3.png

The details page displays the details of SQL execution. You can click different tabs to view the query plan diagram, SQL text, and the query plan text of the SQL statement. An example is as follows:

.. image:: /images/web-platform-view-sql-monitor-info-4.png

View session status
--------------------

To view session status in the database, click the **Session Status** tab on the **Query Monitor** page.

A list of real-time sessions running in the database is displayed, including session ID, execution status, the user who operates, the database where the session is running, the start time, the application, and idle time.

.. image:: /images/web-platform-view-sql-monitor-info-5.png

To view the details of a session, in the search area, fill in the corresponding drop-down option box according to the execution status, user, database, and application name. Then click **Query** to search. The **User** box supports multiple selections.

The options in the **Status** drop-down box are described as follows:

.. list-table::
   :header-rows: 1
   :align: left

   * - Option name
     - Description
   * - Active
     - The backend is running the session.
   * - Idle
     - The backend is waiting for new client commands.
   * - Idle in transaction (aborted)
     - The backend is in a transaction, but currently, no query is running.
   * - Fastpath function call
     - The backend is executing the fast path function.
   * - Disabled
     - The status is reported when ``track_activities`` is disabled in the backend.
   * - Unknown
     - The session status is unknown.

After clicking **Query**, a list of sessions is displayed in the area below, and you should be able to find the target session from the list.

By default, the session list is sorted by **Start Time** in descending order. You can click **Start Time** to sort in ascending order, or sort by **Idle Time**. The description of the fields in the list is as follows:

.. list-table::
   :header-rows: 1
   :align: left

   * - Option name
     - Description
   * - Session ID
     - Identifies the unique ID of the session being executed in the database.
   * - Status
     - The status of the session.
   * - User
     - The user who performs the session operation.
   * - Database
     - The database where the session is running.
   * - Start Time
     - The start time of the session.
   * - Application
     - The client application for executing the session.
   * - Idle time
     - The idle time of the session.
   * - Operation
     - For running sessions, you can click **Cancel Query** to cancel the session.
