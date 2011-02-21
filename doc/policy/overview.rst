
Policies Overview
#################

Policies are designed to allow some automatic management of Celery workers.  
When a policy is executed, they first check to see if a condition is true.  If 
it is, then the body of the policy is executed.  Within the body, various 
Worker and Task attributes can be modified.

.. note:: Policies run outside of Celery.  You may alter worker and task 
   settings without worrying how it will affect your currently-running policy.
   

Example
=======

The compulsory Hello World example::

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

The schedule section must be an expression that returns an object that 
implements the Celery ``schedule`` interface.  Currently, the only available 
schedule type is ``crontab``, which is provided by Celery and permits cron-like 
scheduling.  With no arguments, it defaults to running every minute.

The condition section determines if the apply section should be executed.  If 
it evaluates to ``True``, the apply is run, otherwise it is not.  It is 
optional—when not supplied the apply section is run every time.

The apply section is the body of the policy—it is where Worker and Task 
settings may be modified.

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


Sections
========

A Policy is made up of three sections: Schedule, Condition and Apply.

Schedule
~~~~~~~~

The Schedule section determines when and/or how frequently a policy is 
executed.  The schedule section is required.

TODO....

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

Apply
~~~~~

The apply section is the body of the policy.  It is where the behavior of 
Celery can be modified.  The apply section is required.

TODO....

Limited Environment
===================

Policies are run in a limited execution environment.  These limitations 
manifest themselves when the source code is parsed and when the compiled 
bytecode is executed.

At parse time, the policy source is checked for certain language constructs 
which are available in the full Python language, but are not desired in 
policies.



Imports
~~~~~~~

No imports are allowed in policies.  This includes the import statements 
``import ...`` and ``from ... import ...`` as well as the builtin 
``__import__`` function.  

Selected builtin modules are made available, including ``datetime``, 
``time``, ``calendar``, and ``math``.  (Actually, they are wrappers around 
those modules to prevent any details of those modules leaking into the 
execution environment.)

Defining functions and classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO...

Arbitrary code execution
~~~~~~~~~~~~~~~~~~~~~~~~

The normal Python languages provides several ways to execute code from 
within a script.  None of these methods are available to policies.  This 
includes the ``exec`` statement and the builtin functions ``eval()``, 
``compile()``, ``execfile()``, and ``input()``.

Files
~~~~~

The builtin function ``open()`` is not permitted.

Names
~~~~~

Names beginning with an underscore are not permitted in policies.  This keeps 
some implementation details hidden.

Some object attributes have special meaning in Python which should not be 
exposed within policies.  Such names are not permitted.  This includes 
``__dict__``, ``__class__``, ``__new__``, and ``__init__`` (and several more).  
(Disallowing ``__init__`` prohibits its *direct* use on objects.  It does not 
affect constructing objects via the class name.  In other words, 
``x = MyClass()`` is permitted.)

Names computed at runtime using strings can circumvent the policy name-checking 
mechanism.  Therefore, functions which would facilitate this are prohibited, 
including ``getattr()``, ``setattr()``, ``hasattr()`` and ``delattr()``.

.. note:: Names are found by examining the policy source text.  This means that 
   *any* use of the forbidden names are prohibited, even if they actually refer 
   to some other object.  For instance, because the builtin ``type()`` function 
   is prohibited, policy code such as the following will produce errors: 
   ``type = "MyType"``


Policy Manager
==============

The Policy Manager is the process that executes the policies.  There are two 
ways to run it: directly using ``cmpolicy`` or as part of ``cmrun``.

TODO....

Common Issues
=============

- The Policy Manager must be running.
- It must have access to the django database where Dispatched Task status is 
  recorded.
- Celery workers must have access to the CeleryManagementLib package.  (Usually 
  this means installing it on the worker's (virtual) machine.)
- Exceptions:
  
  - Syntax Errors found while compiling a policy are displayed through the web 
    interface.
  - Exceptions thrown while a policy is executing are generally handled by the 
    Policy Manager.  It will write them to the logger, which by default is 
    stdout.
  - Exceptions thrown from within a Celery worker (while reading or writing 
    task or worker settings) are handled before returning to the Policy 
    Manager.  In such cases, it is probably best to consult both the celeryd 
    and Policy Manager logs.
  


  
TODO....

