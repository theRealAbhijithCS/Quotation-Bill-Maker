from django import template
from quotations.utils import format_indian_currency

register = template.Library()

@register.filter(name='indian_format')
def indian_format_filter(value):
    return format_indian_currency(value)
