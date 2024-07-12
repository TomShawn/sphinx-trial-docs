View Cluster Information
==========================

Steps
--------

1. Access ``http://<ip>:7788/`` to log into the Web Platform console.

2. Click **Dashboard** in the left navigation menu to view the cluster overview.

   .. image:: /images/web-platform-dashboard.png

   .. list-table::
      :header-rows: 1
      :align: left
      :widths: 10 19

      * - Display item
        - Description
      * - Overview
        - Cluster version, console version, cluster uptime, the number of cluster connection sessions, the total number of databases in the cluster, and total number of tables.
      * - Database State
        - The overall status of the database and the number of normal and abnormal segments.
      * - Disk Usage Summary
        - Disk usage of the coordinator and segments.

   .. image:: /images/web-platform-dashboard-metrics.png

   .. list-table::
      :header-rows: 1
      :align: left
      :widths: 8 20

      * - Display item
        - Description
      * - CPU
        - Shows the average CPU and maximum CPU usage of the cluster in the past 2 hours.
          - The orange and blue lines represent the system processes and user processes, respectively. Click the legend in the upper left corner to show or hide the line.
          - Hover the cursor over the chart to display the CPU usage percentage at specific time points.
      * - Memory
        - Shows the average memory usage percentage of the cluster in the past 2 hours.
          - Hover the cursor over the chart to display the average memory and maximum memory usage percentage at specific time points.


