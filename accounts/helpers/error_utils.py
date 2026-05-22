import traceback
from datetime import datetime
from django.shortcuts import redirect


def handle_exception(request, exception):
    try:
        request.session['global_error_context'] = {
            'message': str(exception),
            'exception_type': exception.__class__.__name__,
            'traceback': traceback.format_exc(),
            'path': request.path,
            'method': request.method,
            'user': getattr(request.user, 'username', ''),
            'query_string': request.META.get('QUERY_STRING', ''),
            'post_keys': list(request.POST.keys()) if request.method == 'POST' else [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        request.session.modified = True
    except Exception as log_error:
        request.session['global_error_context'] = {
            'message': str(exception),
            'exception_type': exception.__class__.__name__,
            'traceback': traceback.format_exc(),
            'path': request.path,
            'method': request.method,
            'user': getattr(request.user, 'username', ''),
            'query_string': request.META.get('QUERY_STRING', ''),
            'post_keys': [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'capture_error': str(log_error),
        }
        request.session.modified = True

    referrer = request.META.get('HTTP_REFERER')
    return redirect(referrer or 'dashboard-home')
