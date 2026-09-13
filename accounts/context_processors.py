from .workspaces import personnel_interne


def workspace(request):
    return {
        'workspace': getattr(request, 'workspace', 'public'),
        'personnel_interne': personnel_interne(request),
    }
