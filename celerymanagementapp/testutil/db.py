from djcelery.models import WorkerState, TaskState

def clear_stored_workers():
    WorkerState.objects.all().delete()

def clear_stored_tasks():
    TaskState.objects.all().delete()

