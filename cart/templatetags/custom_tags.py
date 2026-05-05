from django import template

register = template.Library()

@register.filter()
def multiply(value,value2,*args):
    try:
        return int(value) * int(value2)
    except (ValueError, TypeError):
        return ''


@register.filter()
def add_total(value,*args):
    try:
        return int(value) + int(100)
    except (ValueError, TypeError):
        return ''