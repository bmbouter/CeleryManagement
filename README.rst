Quick Start Instructions
############

Overview of Steps
=================

    *Create your Python virtual environment containing the correct requirements
    *Configure your settings
    *Start the required processes

.. contents::

Create your virtual environment containing the correct requirements
===================================================================

Make sure you have pip and virtualenv installed on your system already.

#.  Change into the cloned CeleryManagement directory (where this README is contained)
#.  Run the following:    virtualenv --no-site-packages ve
#.  Activate your virtual environment by running:  source ve/bin/activate
#.  Install the requirements by running:  pip install -r requirements.pip
#.  pip uninstall celery django-celery
#.  pip install -U https://github.com/ask/django-celery/tarball/master#egg=django-celery
#.  pip uninstall celery
#.  pip install -U https://github.com/ask/celery/tarball/master#egg=celery

Configure your settings
=======================

#.  Change into the cloned CeleryManagement directory (where this README is contained)
#.  Create your settings.py file from the template by running:  cp settings.py.sample settings.py
#.  Open up your settings.py file and fill out the following configuration values:

    ``BROKER_HOST
      BROKER_PORT
      BROKER_USER
      BROKER_PASSWORD
      BROKER_VHOST``
#.  Create your database by running:  python manage.py syncdb

Start the required processes
============================
You will need two terminal sessions to run both the event listener and the web application at the same time

#.  Change into the cloned CeleryManagement directory (where this README is contained)
#.  Make sure your virtual environment is active by running:  ``source ve/bin/activate``
#.  Start the event listener by running:  ``python manage.py cmrun``
#.  Open a new session/terminal
#.  Change into the cloned CeleryManagement directory (where this README is contained)
#.  Make sure your virtual environment is active by running:  ``source ve/bin/activate``
#.  Start the web application by running:  ``python manage.py runserver 0.0.0.0:9253``

Starting a worker daemon: (Optional)
====================================
All workers must be started WITH events using the -E option to celeryd.  To start a worker on the same node you installed this web application do the following:

#.  Change into the cloned CeleryManagement directory (where this README is contained)
#.  Make sure your virtual environment is active by running:  ``source ve/bin/activate``
#.  Start a worker node by running:  ``python manage.py celeryd -E``
