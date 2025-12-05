from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Replaces or adds query parameters to the current URL.
    Usage: {% url_replace page=page_obj.next_page_number %}
    """
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()

@register.simple_tag(takes_context=True)
def toggle_tag(context, tag_name):
    """
    Toggles a tag in the 'tag' query parameter list.
    If the tag is present, it removes it. If not, it adds it.
    """
    query = context['request'].GET.copy()
    tags = query.getlist('tag')
    
    if tag_name in tags:
        tags.remove(tag_name)
    else:
        tags.append(tag_name)
    
    query.setlist('tag', tags)
    return query.urlencode()
