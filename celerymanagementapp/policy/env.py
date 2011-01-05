from celery.schedules import crontab

#==============================================================================#
# GLOBALS and LOCALS apply to all sections.  The other dicts apply to the 
# section given in their name.  When policies are run, they will be provided 
# with *copies* of these dicts.

GLOBALS = {}
LOCALS = {}

SCHEDULE_GLOBALS = {}
SCHEDULE_LOCALS = {'crontab': crontab}
CONDITION_GLOBALS = {}
CONDITION_LOCALS = {}
APPLY_GLOBALS = {}
APPLY_LOCALS = {}

#==============================================================================#
# Merge GLOBALS dict with *_GLOBALS dicts (and likewise for LOCALS)
SCHEDULE_GLOBALS.update(GLOBALS)
SCHEDULE_LOCALS.update(LOCALS)
CONDITION_GLOBALS.update(GLOBALS)
CONDITION_LOCALS.update(LOCALS)
APPLY_GLOBALS.update(GLOBALS)
APPLY_LOCALS.update(LOCALS)

#==============================================================================#
