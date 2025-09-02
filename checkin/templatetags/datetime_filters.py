from django import template
from django.utils import timezone
from zoneinfo import ZoneInfo

register = template.Library()

@register.filter
def indian_datetime_12h(value):
    """Convert datetime to Indian timezone and format in 12-hour format"""
    if not value:
        return ''
    
    # Convert to Indian timezone
    indian_tz = ZoneInfo('Asia/Kolkata')
    if timezone.is_aware(value):
        indian_time = value.astimezone(indian_tz)
    else:
        indian_time = value.replace(tzinfo=indian_tz)
    
    # Format in 12-hour format
    return indian_time.strftime('%d %b %Y, %I:%M %p IST')

@register.filter
def indian_date(value):
    """Convert date to Indian format"""
    if not value:
        return ''
    
    if hasattr(value, 'date'):
        value = value.date()
    
    return value.strftime('%d %b %Y')

@register.filter
def indian_time_12h(value):
    """Convert time to 12-hour format"""
    if not value:
        return ''
    
    # Convert to Indian timezone if it's a datetime
    if hasattr(value, 'astimezone'):
        indian_tz = ZoneInfo('Asia/Kolkata')
        if timezone.is_aware(value):
            indian_time = value.astimezone(indian_tz)
        else:
            indian_time = value.replace(tzinfo=indian_tz)
        return indian_time.strftime('%I:%M %p IST')
    
    # If it's just a time object
    return value.strftime('%I:%M %p')