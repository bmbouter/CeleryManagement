
.. _policies-overview:

Policies Overview
#################

Policies are designed to allow some automatic management of Celery workers.  
When a policy is executed, they first check to see if a condition is true.  If 
it is, then the body of the policy is executed.  Within the body, various 
Worker and Task attributes can be modified.

See :ref:`Policies-API` for information about the objects and functions 
available to executing policies.

.. note:: Policies run outside of Celery.  You may alter worker and task 
   settings without worrying how it will affect your currently-running policy.
   
.. contents::
   

Example
=======

The obligatory Hello World example::

    policy:
        schedule:
            crontab()
        condition:
            True
        apply:
            print "hello world!"
            
This will simply print "hello world!" every minute.  However, it illustrates 
the three sections of a policy: the schedule, condition, and apply.  The 
schedule determines when a policy is run.  The condition determines if the 
apply section is run.  And the apply section is the body of the policy—where 
Celery Task and Worker settings may be modified.

The :ref:`schedule section <Schedule>` must be an expression that returns an 
object that implements the Celery ``schedule`` interface.  Currently, the only 
available schedule type is ``crontab``, which is provided by Celery and permits 
cron-like scheduling.  With no arguments, it defaults to running every minute.

The :ref:`condition section <Condition>` determines if the apply section should 
be executed.  If it evaluates to ``True``, the apply is run, otherwise it is 
not.  It is optional—when not supplied the apply section is run every time.

The :ref:`apply section <Apply>` is the body of the policy—it is where Worker 
and Task settings may be modified.

Features & Limitations
======================

TODO....

Not permitted in any section:

- imports (selected modules are available to policies)
- defining functions (with ``def`` or with ``lambda``)
- defining classes
- ``exec`` statement or ``eval()`` function
- any name beginning with an underscore (this hides implementation details)
- selected built-in functions and types

Not permitted in the ``schedule`` or ``condition`` sections:

- assignment (these sections must be expressions)
- deletion (the ``del`` keyword)

These limitations keep policies focused and simple.


Policy Sections
===============

A Policy is made up of three sections: Schedule, Condition and Apply.

.. _Schedule:

Schedule
~~~~~~~~

The Schedule section determines when and/or how frequently a policy is 
executed.  The schedule section is required.

TODO....

.. _Condition:

Condition
~~~~~~~~~

The condition section is what determines whether the apply section will be run.  
The idea being that policies follow a simple if...then structure: 
if ``condition`` then ``apply``.  

Some key points about conditions:

- They are optional.  A non-existent condition is equivalent to a 
  condition that always evaluates to True.
- They must be simple.  Statements are not permitted—it must be an 
  expression.
- If there are multiple condition sections, the results are effectively ORed 
  together.  In other words, if any single condition evaluates to True, the 
  apply section is run.   
- Multiple lines in a single condition are ANDed together.  In other words, all 
  lines in a condition must be true for the condition as a whole to evaluate to 
  True.  (You can work around this using the usual Python line continuation 
  techniques: a backslash or wrapping it in parentheses.)
  
TODO....

.. _Apply:

Apply
~~~~~

The apply section is the body of the policy.  It is where the behavior of 
Celery can be modified.  The apply section is required.

TODO....

Execution Environment
=====================

Policies are run in a limited execution environment.  There are both 
parse-time and run-time mechanisms which enfore this environment.

At parse-time, the policy source is checked for certain language constructs 
which are available in the full Python language, but are not desired in 
policies.

Scope
~~~~~

At run-time, each policy is given a new copy of the execution environment in 
which to run.  Changes to the namespace (e.g. creating a new name) exist only 
while the execution continues.  Other policies, and indeed the same policy 
executed at a later time, will not see the changes.

Restrictions
~~~~~~~~~~~~

**Imports**
    No imports are allowed in policies.  This includes the import statements 
    ``import ...`` and ``from ... import ...`` as well as the builtin 
    ``__import__`` function.  

    Selected builtin modules are made available, including ``datetime``, 
    ``time``, ``calendar``, and ``math``.  (Actually, they are wrappers around 
    those modules to prevent any details of those modules leaking into the 
    execution environment.)

**Defining functions and classes**
    Function and class definitions are not allowed in policies.  This includes 
    the defintiions themselves, as well as their associated keywords 
    (``return``, ``yield``, etc).  Functions defined using ``lambda`` are also 
    not permitted.

**Arbitrary code execution**
    The normal Python languages provides several ways to execute code from 
    within a script.  None of these methods are available to policies.  This 
    includes the ``exec`` statement and the builtin functions ``eval()``, 
    ``compile()``, ``execfile()``, and ``input()``.

**Files**
    The builtin function ``open()`` is not permitted.
   
**Assignment**
    In the schedule and apply sections of a policy, assignment is not 
    permitted.  For instance: neither ``x = a + b`` nor ``x += a + b`` is 
    permitted.  This is because those sections must be expressions.  In the 
    apply section, assignment is permitted.
    
    Certain API objects cannot be assigned to, even in the apply section.  This 
    is primarily to alert the user to a possible error.  The names affected 
    include (but are not limited to) ``tasks``, ``workers``, and ``stats``.
    
**Looping statements**
    Looping statements are not permitted (``for`` and ``while``), except 
    within list comprehensions and generator expressions.

**Names**
    Names beginning with an underscore are not permitted in policies.  This 
    keeps some implementation details hidden.

    Some object attributes have special meaning in Python which should not be 
    exposed within policies.  Such names are not permitted.  This includes 
    ``__dict__``, ``__class__``, ``__new__``, and ``__init__`` (and several 
    more).  (Disallowing ``__init__`` prohibits its *direct* use on objects.  
    It does not affect constructing objects via the class name.  In other 
    words, ``x = MyClass()`` is permitted.)

    Names computed at runtime using strings can circumvent the policy 
    name-checking mechanism.  Therefore, functions which would facilitate this 
    are prohibited, including ``getattr()``, ``setattr()``, ``hasattr()`` and 
    ``delattr()``.

.. note:: Names are found by examining the policy source text.  This means that 
   *any* use of the forbidden names are prohibited, even if they actually refer 
   to some other object.  For instance, because the builtin ``type()`` function 
   is prohibited, policy code such as the following will produce errors: 
   ``type = "MyType"``
   
Exception handling
~~~~~~~~~~~~~~~~~~

The goal of the policy mechanism is to make it as robust in the face of 
exceptions as possible.  Care is taken in the implementation to prevent an 
exception raised while one policy is executing from affecting other policies as 
well as the Policy Manager process.  Where exceptions must be prevented from 
propogating further, the Policy Manager will attempt to print out the exception 
traceback.

Some details:

- Syntax Errors found while compiling a policy are displayed through the web 
  interface.
- Exceptions thrown while a policy is executing are generally handled by the 
  Policy Manager.  It will write them to the logger, which by default is 
  stdout.
- Exceptions thrown from within a Celery worker (while reading or writing 
  task or worker settings) are handled within the worker.  A traceback may be 
  written by the worker and the Policy Manager, so in such cases, it is 
  probably best to consult both the celeryd and Policy Manager logs.


Policy Manager
==============

The Policy Manager is the process that executes the policies.  There are two 
ways to run it: directly using ``cmpolicy`` or as part of ``cmrun``.

TODO....

Common Issues
=============

- The Policy Manager must be running for policies to be executed.
- It must have access to the django database where Dispatched Task status is 
  recorded.
- Celery workers must have access to the CeleryManagementLib package.  (Usually 
  this means installing it on the worker's (virtual) machine.)
  

  


  
TODO....

