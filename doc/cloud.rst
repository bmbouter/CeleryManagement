.. _cloud:

Cloud Enabled
#############

.. _libcloud: http://incubator.apache.org/libcloud/
.. _DreamHost: http://www.dreamhost.com/hosting-vps.html
.. _Amazon: http://aws.amazon.com/ec2/
.. _`Enomaly ECP`: http://www.enomaly.com/
.. _ElasticHosts: http://www.elastichosts.com/
.. _GoGrid: http://www.gogrid.com/
.. _`IBM Developer Cloud`: http://www-935.ibm.com/services/us/igs/cloud-development/
.. _Linode: http://www.linode.com/
.. _OpenNebula: http://www.opennebula.org/
.. _Rackspace: http://www.rackspacecloud.com/index.php
.. _RimuHosting: http://rimuhosting.com/
.. _Slicehost: http://www.slicehost.com/
.. _Softlayer: http://www.softlayer.com/
.. _VoxCloud: http://www.voxel.net/
.. _VPS.net: http://www.vps.net/


CeleryManagement is fully integrated with libcloud_ allowing you to operate
your CeleryManagement infrastructure on the cloud computing provider of your
choice.


.. contents::

.. _supported_clouds:

Supported Clouds
================

CeleryManagement currently supports the following cloud environments:

    - DreamHost_
    - Amazon_
    - `Enomaly ECP`_
    - ElasticHosts_
    - GoGrid_
    - `IBM Developer Cloud`_
    - Linode_
    - OpenNebula_
    - Rackspace_
    - RimuHosting_
    - Slicehost_
    - Softlayer_
    - VoxCloud_
    - VPS.net_


.. _building_your_cloud_image:

Building Your Image on the Cloud
================================

.. _CeleryManagementLib: https://github.com/bmbouter/CeleryManagementLib

To begin running your celery infrastructure in cloud computing environments,
you will need to first build a cloud image that meets the following
requirements:

    - celery or django-celery installed
    - SSH server start by default at boot
    - Your Task code
    - Have installed CeleryManagementLib_ (optional but recommended)

.. _configuring_your_cloud_system:

Configuring Your System
=======================

If you want to have CeleryManagement manage and control your infrastructure
dynamically set the following variable in the settings.py file:

``CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE = "dynamic"``

Once set, all configuration and management happens through the web interface at
this location:

``/celerymanagementapp/view/configure/``
