from django.contrib import messages


def send_sweetalert(request, message_type, message):
    type_mapping = {
        'success': messages.SUCCESS,
        'info': messages.INFO,
        'warning': messages.WARNING,
        'error': messages.ERROR,
        'question': messages.INFO,
    }

    level = type_mapping.get(message_type, messages.INFO)
    extra_tags = f'swal-{message_type}'

    messages.add_message(request, level, message, extra_tags=extra_tags)
