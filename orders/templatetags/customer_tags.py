from django import template
from django.db.models import Sum
from orders.models import Customer

register = template.Library()

@register.simple_tag
def total_credit():
    total = Customer.objects.aggregate(total=Sum('credit_limit'))['total'] or 0
    return f"{total:,.0f}"

@register.simple_tag
def avg_credit():
    total = Customer.objects.aggregate(total=Sum('credit_limit'))['total'] or 0
    count = Customer.objects.count()
    if count > 0:
        avg = total / count
        return f"{avg:,.0f}"
    return "0"