from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import datetime, random

class Hug(models.Model):
    source = models.ForeignKey(User, related_name="hugs_given")
    target = models.ForeignKey(User, related_name="hugs_gotten")
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    inspiration = models.ForeignKey("self", related_name="inspired", null=True, blank=True)
    def __unicode__(self): return self.nameme()
    def history(self):
        x = self
        xx = []
        while x.inspiration:
            xx.insert(0, x.inspiration)
            x = x.inspiration
        return xx
    def colour(self):
        random.seed(self.nameme())
        return "pastelback%i" % random.randrange(1,17)
        #return random.choice(["red", "pink", "purple", "deep-purple", "indigo", "blue", "light-blue", "cyan", "teal", "green", "light-green", "lime", "yellow", "amber", "orange", "deep-orange"])+random.choice([(" accent-%i" % x) for x in range(1,5)]+[(" darken-%i" % x) for x in range(1,5)]+[(" lighten-%i" % x) for x in range(1,3)]+[""])
    def inspiron(self, mode="text"): return self.nameme(mode)+(' after '+self.inspiration.inspiron(mode) if getattr(self, "inspiration", None) else '')
    def descendants(self):
        dd = []
        for d in self.inspired.all():
            dd.append(d)
            for ddd in d.descendants():
                dd.append(ddd)
        return dd
    def nameme(self, mode="text"):
        return "%s %shugged %s%s!" % (self.source.bonus_data.nameme(mode=mode), ("re" if getattr(getattr(self, "inspiration", None), "target", "") == self.target else ""), ("self" if self.target == self.source else self.target.bonus_data.nameme(mode=mode)), (" back" if getattr(getattr(self, "inspiration", None), "source", "") == self.target else ""))
    def grandgrand(self, pa):
        h = self.history()
        h.reverse()
        return h.index(pa)+1

class BonusData(models.Model):
    user = models.OneToOneField(User, related_name="bonus_data")
    twitter = models.CharField(max_length=50, null=True, blank=True)
    tokens = models.IntegerField(default=0)
    specialrate = models.IntegerField(null=True, blank=True)
    def __unicode__(self): return self.user.username
    def nameme(self, mode="text"):
        if "twitter" in mode:
            return self.twitter or self.user.username
        if "link" in mode:
            return '<a href="%s">%s</a>' % (reverse("user",args=(self.user.username,)), self.user.username)
        return self.user.username
    def tokenet(self):
        r = getattr(self, "specialrate", 0)
        if self.user.hugs_given.exclude(timestamp__lte=(datetime.datetime.utcnow()-datetime.timedelta(minutes=5))).count() < (r if r > 0 else 15):
            return True
        if self.tokens >= 1:
            self.tokens = self.tokens - 1
            self.save()
            return True
        return False
