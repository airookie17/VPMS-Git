from django import template
import json

register = template.Library()

@register.filter
def json_script(obj):
    return json.dumps(obj)
