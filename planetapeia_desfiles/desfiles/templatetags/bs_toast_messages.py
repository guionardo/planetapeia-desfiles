from django import template
from django.contrib import messages
from django.contrib.messages.storage.base import Message
from django.utils.html import escape, mark_safe

register = template.Library()

BS_CLASSES = {}
DEFAULT_TAGS = {
    messages.INFO: ("primary", "Informação", "#0dcaf0"),
    messages.DEBUG: ("secondary", "DEBUG", "#6c757d"),
    messages.SUCCESS: ("success", "Sucesso", "#198754"),
    messages.WARNING: ("warning", "Atenção", "#ffc107"),
    messages.ERROR: ("danger", "ERRO", "#dc3545"),
}


@register.simple_tag
def bs_toast(message: Message):
    bs_class, title, img_color = DEFAULT_TAGS.get(message.level, ("", "", ""))
    if bs_class:
        img = f"""<svg class="bd-placeholder-img rounded me-2" width="20" height="20" xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true" preserveAspectRatio="xMidYMid slice" focusable="false">
            <rect width="100%" height="100%" fill="{img_color}"></rect>
        </svg>"""
        lines = [
            '<div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="10000">',
            '<div class="toast-header">',
            img,
            f'<strong class="me-auto">{title}</strong>',
            f"<small>{message.extra_tags}</small>" if message.extra_tags else "",
            '<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Fechar"></button>',
            "</div>",
            f'<div class="toast-body">{escape(str(message))}</div>',
            "</div>",
        ]
    #     <div id="liveToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
    #     <div class="toast-header">
    #         <img src="..." class="rounded me-2" alt="...">
    #         <strong class="me-auto">Bootstrap</strong>
    #         <small>11 mins ago</small>
    #         <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    #     </div>
    #     <div class="toast-body">
    #         Hello, world! This is a toast message.
    #     </div>
    # </div>
    else:
        lines = ["<!-- INVALID ALERT: {message} -->"]
    return mark_safe("\n".join(lines))
