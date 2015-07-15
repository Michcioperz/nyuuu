from django import template
from django.contrib.auth.models import User
from ..models import BonusData
import random

register = template.Library()

@register.inclusion_tag('hug/temp.html')
def hugrender(hug):
    return {"hug":hug, "hcol": hug.colour()}

@register.inclusion_tag('hug/inspiron.html')
def inspiron(hug):
    return {"hug":hug}

@register.filter
def grandpa(hug, other):
    return hug.grandgrand(other)

@register.filter
def hugcheck(user):
    try:
        user.bonus_data
    except:
        BonusData.objects.create(user=user)
    return user
