from django.conf import settings

def context_processor(request):
    additions = {
        'CELERYMANAGEMENTAPP_MEDIA_PREFIX' : settings.CELERYMANAGEMENTAPP_MEDIA_PREFIX,
        'CELERYMANAGEMENTAPP_SYSTEMVIEW_REFRESH_RATE' : settings.CELERYMANAGEMENTAPP_SYSTEMVIEW_REFRESH_RATE,
        'CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE' : settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE
    }

    return additions
