Deploy HashData Lightning through Visual Interface
======================================================

HashData Lightning Web Platform is a console tool for deploying and managing HashData Lightning clusters, providing a simple and intuitive user interface. Compared to the manual method, deployment through visual interface is simpler and more intuitive. You only need to follow the interface prompts to operate, without understanding complex commands and configuration files, making deployment more efficient.

Applicable version
-----------------------

Make sure that you are deploying HashData Lightning v1.5.4 or a later version.

Deploy HashData Lightning cluster
------------------------------------

This section introduces how to deploy HashData Lightning on physical machines using the Web Platform.

Software and hardware configuration requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HashData Lightning supports deployment on the following operating systems and CPU architectures. See the table below for details.

.. list-table::
   :header-rows: 1
   :align: left

   * - Operating system
     - Supported CPU architectures
   * - RHEL/CentOS 7.6+
     - x86_64 and AArch64
   * - Kylin V10 SP1 or SP2
     - x86_64 and AArch64

Installation steps
~~~~~~~~~~~~~~~~~~~~~~~

Installing HashData Lightning on servers mainly involves 4 steps: preparation, installation of the database RPM package, database deployment, and post-installation setup.

Step 1: Prepare to deploy
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Before installation, check and confirm the basic information of the server to better plan and deploy the cluster.

   .. list-table::
      :header-rows: 1
      :align: left
      :widths: 8 10 18

      * - **Step**
        - **Command**
        - **Purpose**
      * - 1
        - ``free -h``
        - Views memory information of the operating system.
      * - 2
        - ``df -h``
        - Checks disk space.
      * - 3
        - ``lscpu``
        - Checks the number of CPUs.
      * - 4
        - ``cat/etc/system-release``
        - Views the version information of the operating system.
      * - 5
        - ``uname -a``
        - Outputs all kernel information in this order (where if the detection results of -p and -i are unknown, they are omitted): kernel name, hostname on the network node, kernel release number, kernel version, hardware architecture name of the host, processor type, hardware platform, operating system name.
      * - 6
        - ``tail -11 /proc/cpuinfo``
        - Views CPU information.

2. Create a ``gpadmin`` user on each node server as the admin user. Create a user group and username ``gpadmin``, and set the identification number of the user group and username to ``520``. Create and specify the home directory ``/home/gpadmin/``. The commands are as follows.

   .. code:: bash

      groupadd -g 520 gpadmin  # Creates the user group gpadmin.
      useradd -g 520 -u 520 -m -d /home/gpadmin/ -s /bin/bash gpadmin  # Creates the user gpadmin and the home directory.
      passwd gpadmin  # Sets password for gpadmin.

3. Configure as follows on the machine where HashData Lightning is to be installed:

   1. Turn off the firewall. Otherwise, you cannot deploy through the Web Platform.

      .. code:: shell

         sudo systemctl stop firewalld.service
         sudo systemctl disable firewalld.service

   2. Disable SELinux. You can edit the ``/etc/selinux/config`` file and set the value of SELINUX to ``disabled``:

      .. code:: shell

         sudo sed s/^SELINUX=.*$/SELINUX=disabled/ -i /etc/selinux/config
         sudo setenforce 0

4. Set system parameters on each server.

5. Permanently disable IPv6.

   To do that, you need to edit the ``/etc/sysctl.conf`` file (or create a new configuration file in the ``/etc/sysctl.d/`` directory) and add the following line:

   ::

      net.ipv6.conf.all.disable_ipv6 = 1
      net.ipv6.conf.default.disable_ipv6 = 1

   After that, run ``sudo sysctl -p`` to apply the changes, or restart your system.

6. Configure password-free login between servers. Enable password-free login to each machine from other nodes in the ``gpadmin`` account. The check command is ``ssh ip``, such as ``ssh 192.168.48.58``. If the password-free setting is successful, no password is required.

7. Enable the gpadmin user to perform ``sudo`` without password.

   .. note:: After switching to the ``gpadmin`` user by running ``su - gpadmin``, if you cannot run the ``ifconfig`` command, you need to configure the environment variable for ``ifconfig``. Assuming the ``ifconfig`` file is in the ``/usr/sbin`` directory, you need to add a line ``export PATH=/usr/sbin:$PATH`` in the ``~/.bashrc`` file, and then run ``source ~/.bashrc`` to make it effective.


8. Copy the RPM package. Copy the RPM package to each node server where you want to install HashData Lightning.

Step 2: Install the database RPM package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On each node machine, run the following commands to install the database RPM package, and the system dependencies will be automatically installed.

.. code:: shell

   cd /home/gpadmin
   sudo yum install hashdata-lightning-1.5.4-1.el7.x86_64-75889-release.rpm
   sudo chown -R gpadmin:gpadmin /usr/local
   sudo chown -R gpadmin:gpadmin /usr/local/cloudberry*

.. note:: During the actual installation process, you need to replace the RPM file name ``hashdata-lightning-1.5.4-1.el7.x86_64-75889-release.rpm`` with the real RPM package name.

Step 3: Deploy the database through the interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use Web Platform, the embedded visual interface, to deploy HashData Lightning. By default, the visual deployment tool accesses the ``7788`` port of the database node server. After installation, the ``7788`` port is open by default for all nodes.

Access the deployment interface
''''''''''''''''''''''''''''''''''

1. Visit the deployment visual interface. Open your browser (IE series browsers are not supported) and visit the following link to open the interface. You need to replace ``<IP>`` with the IP address of any node server:

   ::

      http://<IP>:7788/

2. Fill in the superuser password to log in to the deployment node, as shown in the following figure. To view the superuser password, run the command ``find / -path "*/cloudberry-*/cloudberryUI/resources/users.json" 2>/dev/null | xargs cat | grep -A1 '"username": "gpmon",'``.

   The default installation directory is /usr/local, and you can view the username and password of the gpmon account using the command ``cat /usr/local/cloudberry-db/cloudberryUI/resources/users.json``.

   .. image:: /images/web-platform-deploy-login.png

After successful login, choose the deployment mode: single-node deployment or multi-node deployment.

.. note:: You cannot log in with the same IP address and user at the same time. Otherwise, an error will be prompted.

Deploy in single-node mode
''''''''''''''''''''''''''''

The single-node deployment mode is intended for testing purposes. This mode does not support high availability. Do not use this mode in production environments.

This mode only requires one physical machine because all services will be deployed on the same machine. 

1. Once logged in, select **Single Node Deployment** and click **Next**.

2. Set the configuration items for a single node. The screenshot below shows an example configuration:

   .. image:: /images/web-platform-deploy-single-node.png

3. Click **Perform Deployment** and wait for the deployment to complete.

   After the deployment is complete, you will see the following screen:

   .. image:: /images/web-platform-welcome.png

Deploy in multi-node mode
''''''''''''''''''''''''''''

1. Once logged in, select **Add nodes and start database cluster** and click Next.

2. Add a node. You can use the **Add in batch** to add nodes quickly, or you can add a node manually.

   -  To quickly add nodes: The deployment tool will automatically detect all nodes that have the RPM packages installed and show the **one-click add** in the upper-left corner of the window.
  
      Click **one-click add** and the deployment tool will automatically add the available nodes.

   -  To manually add nodes: Enter the hostname or IP address of the node that you want to add in the text box, such as ``i-uv2qw6ad`` or ``192.168.176.29``, and then click **Add node**.

      .. note:: 

         -  Make sure that the nodes you add can be detected and are not duplicated. Otherwise, the deployment tool will report an error at the top of the window, indicating that the hostname was not detected or the node to be added already exists.

         -  The multi-node deployment mode cannot proceed if you only add one node.

3. Complete the following configuration for the cluster:

   -  Configure the standby node for the primary node and configure mirror nodes for the data nodes.

   -  **Data mirroring** determines whether the cluster's data nodes have mirror copies. It is recommended to enable this option in production environments to ensure high availability.

   -  Change the ``gpmon`` password and check **Allow remote connection to the database**.

   .. image:: /images/web-platform-deploy-multi.png

4. Set the storage path. Note that the current HashData Lightning version requires the mounting points of all nodes to be specified to the same one. Otherwise, an error message is prompted. Then click **Next**.

5. Confirm the configurations made in the previous steps. You can go back to correct the wrong setting if there is one. Click **Start Deployment** in the lower-right corner. The deployment starts and a progress bar is displayed. 

   If the deployment is completed, you will be taken to the completion page. Note that you will be asked if you want to deploy again the next time you log in. 

6. Run ``psql`` to check whether the database is up. If yes, you can continue with the post-installation configuration. If not, try to log into the node server again and run ``psql`` as the ``gpadmin`` user.

Step 4: Perform post-installation configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  Run the following command as the ``gpadmin`` user.

   .. code:: shell

      sudo chown -R gpadmin:gpadmin /usr/local/cloudberry-db/cloudberryUI/resources

-  Enable remote connection.

   HashData Lightning supports remote connections. If **Allow remote connection to database** is not checked when you configure the cluster parameters (as described in Step 3 of the above **Deploy in multi-node mode** section), you can add the following code line to the ``$COORDINATOR_DATA_DIRECTORY/pg_hba`` file to allow users from any IP to connect through password authentication.

   To ensure security, restrict the IP range or database name based on actual needs. For ``pg_hba.conf``, the HashData technical support team has an auto-generated initialization version. The support engineers will configure the version on-site based on the actual situation and security requirements. It is recommended to check ``pg_hba.conf``.

   .. code:: shell

      host  all       all   0.0.0.0/0  md5

   Once the changes are made, run the following command to reload the database configuration file ``pg_hba.conf``:

   .. code:: shell

      gpstop -u

-  You can use the following commands to start, stop, restart, and view the status of HashData Lightning.

   .. list-table::
      :header-rows: 1
      :align: left
      :widths: 8 18

      * - Command
        - Description
      * - ``gpstop -a``
        - Stops the cluster. In this mode, if there is a connected session, you need to wait for the session to be closed before stopping the cluster.
      * - ``gpstop -af``
        - Forcibly shuts down the cluster.
      * - ``gpstop -ar``
        - Restarts the cluster. Waits for the SQL statement to finish execution. In this mode, if there is a connected session, you need to wait for the session to be closed before stopping the cluster.
      * - ``gpstate -s``
        - Shows the current status of the cluster.


Troubleshooting tips
------------------------

- After logging into the console through ``http://<IP>:7788/``, if you see a message indicating that the cluster nodes are not connected or stuck in the process of collecting host information, it is recommended to check that the SSH mutual trust between the nodes is properly configured, and then run the following commands to restart the node:

   .. code:: shell

      su - gpadmin
      cd /usr/local/cloudberry-db
      sudo pkill cbuiserver
      ./cbuiserver

-  If the node machines have previously undergone visual deployment and you wish to reinstall the RPM packages on these machines, run ``sudo pkill cbuiserver`` on each machine before installation and then clear the ``/usr/local/cloudberry-db`` directory.
