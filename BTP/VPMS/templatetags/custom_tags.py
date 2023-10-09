from django import template
import json

register = template.Library()

@register.simple_tag
def json_script(data):
    return '<script type="application/json">%s</script>' % json.dumps(data)
