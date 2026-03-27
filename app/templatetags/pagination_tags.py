from django import template

register = template.Library()


@register.simple_tag
def get_pagination_pages(current, total):
    if total <= 7:
        return [{'num': i, 'type': 'current' if i == current else 'page'} for i in range(1, total + 1)]
    
    pages = []
    shown_pages = set()
    
    for i in range(1, min(4, total + 1)):
        shown_pages.add(i)
        if i == current:
            pages.append({'num': i, 'type': 'current'})
        else:
            pages.append({'num': i, 'type': 'page'})
    
    if current > 4:
        pages.append({'num': None, 'type': 'ellipsis'})
    
    if current > 3 and current < total - 2:
        if current - 1 not in shown_pages:
            pages.append({'num': current - 1, 'type': 'page'})
            shown_pages.add(current - 1)
        
        if current not in shown_pages:
            pages.append({'num': current, 'type': 'current'})
            shown_pages.add(current)
        
        if current + 1 not in shown_pages and current + 1 < total - 2:
            pages.append({'num': current + 1, 'type': 'page'})
            shown_pages.add(current + 1)
    elif current > 3:
        if current - 1 > 3 and current - 1 not in shown_pages:
            pages.append({'num': current - 1, 'type': 'page'})
            shown_pages.add(current - 1)
        if current not in shown_pages:
            pages.append({'num': current, 'type': 'current'})
            shown_pages.add(current)
    
    if current < total - 3:
        pages.append({'num': None, 'type': 'ellipsis'})
    
    if total not in shown_pages:
        if total == current:
            pages.append({'num': total, 'type': 'current'})
        else:
            pages.append({'num': total, 'type': 'page'})
        shown_pages.add(total)
    
    return pages

