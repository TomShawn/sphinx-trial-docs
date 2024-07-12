View Storage Information
==========================

Steps
--------

1. Access ``http://<ip>:7788/`` to log into the Web Platform console.

2. Click **Storage Usage** in the left navigation menu to view the storage overview information.

   .. image:: /images/web-platform-view-storage-info-1.png

3. Click the **Coordinator** and **Segments** cards at the top of the page to view the disk usage of the machines hosting the coordinator and segment nodes respectively.

   .. list-table::
      :header-rows: 1
      :align: left

      * - Display item
        - Description
      * - Host Name
        - Host names of the coordinator or segments. There may be multiple hosts.
      * - Data Directory
        - The mounting point and path information of each machine.
      * - Used Disk Space (%)
        - The disk usage of each machine and its percentage.
      * - Disk Space Free (GB)
        - The available amount of disks on each machine and its percentage.
      * - Total Space (GB)
        - The total capacity of disks on each machine.

4. Click the small triangle to the left of the **Hostname** to expand and view the disk usage under different mount points.
