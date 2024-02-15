from django import template
from django.contrib import messages
from django.contrib.messages.storage.base import Message
from django.utils.html import escape, mark_safe

register = template.Library()

BS_CLASSES = {}
DEFAULT_TAGS = {
    messages.INFO: ("primary", ""),
    messages.DEBUG: ("secondary", ""),
    messages.SUCCESS: ("success", ""),
    messages.WARNING: ("warning", ""),
    messages.ERROR: ("danger", ""),
}


@register.simple_tag
def bs_alert(message: Message):
    bs_class, bs_label = DEFAULT_TAGS.get(message.level, ("", ""))
    if bs_class:
        lines = [
            f'<div class="alert alert-{bs_class} alert-dismissible fade show" role="alert"',
            f"<strong>{bs_label}</strong> {escape(str(message))}",
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            "</div>",
        ]
    else:
        lines = ["<!-- INVALID ALERT: {message} -->"]
    return mark_safe("\n".join(lines))
