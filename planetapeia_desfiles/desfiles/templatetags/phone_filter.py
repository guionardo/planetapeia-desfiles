from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def format_phone(phone: str) -> str:
    phone = "".join(c for c in phone if c.isnumeric())
    match len(phone):
        case 8:  # 9999-9999
            return f"{phone[:4]}-{phone[-4:]}"
        case 9:  # 99999-9999
            return f"{phone[:5]}-{phone[-4:]}"
        case 10:  # 99 9999-9999
            return f"{phone[:2]} {phone[2:6]}-{phone[-4:]}"
        case 11:  # 99 99999-9999
            return f"{phone[:2]} {phone[2:7]}-{phone[-4:]}"
    return phone
