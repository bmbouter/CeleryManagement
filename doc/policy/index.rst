========
Policies
========

Policies facilitate some automatic control over Celery behavior.  They are 
simple Python-like scripts that may modify Celery Task and/or Worker settings.  
They run periodically at which time a condition is evaluated.  If the condition 
is true, then the main body of the Policy is executed.  It is in this main body 
that changes can be made to Tasks and/or Workers.


.. toctree::
    :maxdepth: 2

    overview
    api
    recipes

