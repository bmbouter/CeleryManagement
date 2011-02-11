.. _operation:

Operation
#########


CeleryManagement has 3 modes:

passive:
  viewing of task and worker data only
static:
  starting and stopping of celeryd workers for existing nodes in your data center.  Viewing of task and worker data also enabled
dynamic:
  starting and stopping of cloud virtual machines and the management of celery processes on those nodes.  Viewing of task and worker data also enabled

.. contents::


.. _what_operating_mode_am_i_in:

What Operating Mode Am I In?
============================

The current mode of operation can be determined by going to the Configuration page and checking the bar labeled "Current Operation Mode" or by opening the settings file and checking the value of CELERYMANGEMENTAPP_INFRASTRUCTURE_USE_MODE.

.. _changing_operating_modes:

Changing Operating Modes
========================

To change operating modes, open the settings.py file and find::

    CELERYMANAGEMENT_APP_INFRASTRUCTURE_USE_MODE

change the value to one of "passive", "static", or "dynamic".  See below for the benefits and limitations of each.

.. _passive_operating_mode:

Passive Mode
============

This mode provides only monitoring capabilities.

.. _static_operating_mode:

Static Mode
===========

This mode provides monitoring and worker management.  Through the use of Out Of Band workers the system can turn workers on and off.  The configuration page allows for the creation of a new Out of Band worker, editing of existing workers and deleting of existing workers.  This mode also adds the ability to shutdown a worker entity from the System View.  This can be done by right-clicking a worker entity and choosing "Shutdown Worker" from the menu. 

Creating a new worker requires the following::

- Username: the username used to access the system the worker resides on
- SSH key: the PUBLIC key for the above username to access the system
- Celeryd Start Commands: 
- Celeryd Stop Commands:
- Celeryd Status Report Commands:
- IP Address: the IP address of the system the worker resides on
- Currently active: whether or not you want the worker to appear active to CeleryManagement

.. _dynamic_operating_mode:

Dynamic Mode
============

This mode provides monitoring, worker management and policy creation.  By choosing a cloud services provider defined by libcloud, the system can create and destroy worker instances on demand.  For more information the Policy Management please see ....

For a given installation of CeleryManagement in dynamic mode, only one Provider can be configured at a time.That means, deleting your old provider to switch to a new one is required.

Creating a new Provider requires the following::

- Provider: having an account and credentials to access a cloud provider specified by libcloud
- User ID: the user ID for the given provider
- Key: 
- Image ID: an availlible image properly configured from which instances will be created
- Username: the username to access the image instances from
- SSH Key: the key for the username above to access the instances
- Celeryd Start Commands: 
- Celeryd Stop Commands:
- Celeryd Status Report Commands:
