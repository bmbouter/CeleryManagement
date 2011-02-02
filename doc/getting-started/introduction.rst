.. _intro:

==============
 Introduction
==============

.. _celery-synopsis:

.. _`Celery`: http://celeryq.org/docs/getting-started/introduction.html

CeleryManagement is an open source Management Library designed to monitor and
manage `Celery`_ installations.  It has two primary functions:

    * Visualize task and worker performance and statistics
    * Policy driven monitoring of celery infrastructure to achieve
         * task latency
         * task throughput
         * worker utilization

Celery be a critical component in server and web service architectures and
having knowledge about the performance and reliability of those celery
functions is valuable.  CeleryManagement can be used to help identify problems
before they happen or after a strange Celery event has occurred.

CeleryManagement is also designed to be fully interoperable with celery add on
packages `django-celery`_, `celery-pylons`_, and `Flask-Celery`_ add-on
packages.  This ensures that CeleryManagement can provide value to the
`Django`_, `Pylons`_ and `Flask`_ communities.

.. _`Django`: http://djangoproject.com/
.. _`Pylons`: http://pylonshq.com/
.. _`Flask`: http://flask.pocoo.org/
.. _`django-celery`: http://pypi.python.org/pypi/django-celery
.. _`celery-pylons`: http://pypi.python.org/pypi/celery-pylons
.. _`Flask-Celery`: http://github.com/ask/flask-celery/

.. contents::
    :local:

.. _celery-management-overview:

Overview
========

This is a high level overview of the architecure.

Event data is enabled on all celery workers by using the `-E option on celeryd`_.  This event data is sent through your existing AMQP message bus and received by CeleryManagement which delivers this information into a database.  The celery data is examined and displayed such that.

.. _`-E option on celeryd`: http://ask.github.com/celery/reference/celery.bin.celeryd.html#cmdoption-celeryd-E

.. _celery-example:

Example
=======

@TODO link to the examples page with pretty graphs

.. _celery-features:

Features
========

    +------------------+----------------------------------------------------+
    | Visualization    | Graphically renders all worker and task data       |
    |                  | visually.  This helps give you a quick look at     |
    |                  | what your celery infrastructure is organized.      |
    +------------------+----------------------------------------------------+
    | Analytics        | Drill down into your task and worker performance   |
    |                  | data visually.                                     |
    +------------------+----------------------------------------------------+
    | Auto-scaling     | Brings online and offline worker nodes to          |
    |                  | dynamically grow and shrink the number of worker   |
    |                  | nodes.                                             |
    +------------------+----------------------------------------------------+
    | Cloud Enabled    | Full cloud management and provisiong capabilities  |
    |                  | through `libcloud`_.                               |
    +------------------+----------------------------------------------------+
    | Monitoring       | Celery event monitoring with email notifications   |
    |                  | capability.  Monitoring can happen continuously on |
    |                  | definable schedules.                               |
    +------------------+----------------------------------------------------+
    | Scheduling       | Supports recurring tasks like cron, or specifying  |
    |                  | an exact date or countdown for when after the task |
    |                  | should be executed.                                |
    +------------------+----------------------------------------------------+
    | Policy Driven    | Control all monitoring of your system through a    |
    |                  | simple policy language.  This allows you to fully  |
    |                  | customize the policies that govern your            |
    |                  | infrastructure.                                  |
    +------------------+----------------------------------------------------+
    | Routing          | Using AMQP's flexible routing model you can route  |
    |                  | tasks to different workers, or select different    |
    |                  | message topologies, by configuration or even at    |
    |                  | runtime.                                           |
    +------------------+----------------------------------------------------+
    | Managed Settings | Remote contorl functions have been added to manage |
    |                  | and modify worker settings at runtime              |
    +------------------+----------------------------------------------------+

.. _celery-management-documentation:

Documentation
=============

The `latest documentation`_ with user guides and tutorials is hosted at Github.

.. _`latest documentation`: http://bmbouter.github.com/CeleryManagement/

.. _celery-management-installation:

Installation
============

You can install CeleryManagement either via the Python Package Index (PyPI)
or from source.

To install using `pip`,::

    $ pip install CeleryManagement

To install using `easy_install`,::

    $ easy_install CeleryManagement

.. _celery-management-installing-from-source:

Downloading and installing from source
--------------------------------------

Download the latest version of CeleryManagement from
http://pypi.python.org/pypi/celerymanagement/

You can install it by doing the following,::

    $ tar xvfz celery-management-0.0.0.tar.gz
    $ cd celery-management-0.0.0
    $ python setup.py build
    # python setup.py install # as root

.. _celery-management-installing-from-git:

Using the development version
-----------------------------

You can clone the repository by doing the following::

    $ git clone git://github.com/bmbouter/CeleryManagement.git
