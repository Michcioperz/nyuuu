from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.contrib import messages
from django.utils.feedgenerator import Atom1Feed
from .models import Hug
from .templatetags.hugnet import hugcheck
from .forms import SettingsForm
from .secrets import tweeter, pushshsh
import datetime, twitter, json, random


def index(request):
    hugs = Hug.objects.order_by("-timestamp")[:100]
    return render(request, "hug/index.html", {"hugs": hugs, "userson":json.dumps([x.username for x in User.objects.filter(is_active=True)])})

@login_required
def settings(request):
    if request.method == 'POST':
        if getattr(request.user, "bonus_data", None):
            form = SettingsForm(request.POST, instance=request.user.bonus_data)
        else:
            form = SettingsForm(request.POST, initial={'user': request.user})
        form.user = request.user
        if form.is_valid():
            form.save()
            messages.success(request, "Settings saved! <3")
            return redirect(reverse("index"))
        else:
            messages.error(request, "Something's wrong...")
    else:
        if getattr(request.user, "bonus_data", None):
            form = SettingsForm(instance=request.user.bonus_data)
        else:
            form = SettingsForm(initial={'user': request.user})
    return render(request, "hug/settings.html", {"form":form})

def user(request, name):
    usr = get_object_or_404(User, username=name)
    hugs = Hug.objects.filter(Q(target=usr) | Q(source=usr)).order_by("-timestamp")
    return render(request, "hug/user.html", {"hugs": hugs, 'usr': usr})

def user_hgd(request, name):
    usr = get_object_or_404(User, username=name)
    x = usr.hugs_given.values('target').annotate(hcount=Count('target'))
    return JsonResponse(data={"data":[{"value": y["hcount"], "label": get_object_or_404(User, pk=y["target"]).username} for y in x]})

def user_hby(request, name):
    usr = get_object_or_404(User, username=name)
    x = usr.hugs_gotten.values('source').annotate(hcount=Count('source'))
    return JsonResponse(data={"data":[{"value": y["hcount"], "label": get_object_or_404(User, pk=y["source"]).username} for y in x]})

def onehug(request, pk):
    hug = get_object_or_404(Hug, pk=pk)
    random.seed(hug)
    return render(request, "hug/temp.html", {"hug":hug, "hcol": random.choice(["red", "pink", "purple", "deep-purple", "indigo", "blue", "light-blue", "cyan", "teal", "green", "light-green", "lime", "yellow", "amber", "orange", "deep-orange"])+random.choice([(" accent-%i" % x ) for x in range(1,5)]+[(" darken-%i" % x) for x in range(1,5)]+[(" lighten-%i" % x) for x in range(1,3)]+[""])})

@login_required
def showme(request):
    return redirect(reverse("user", args=(request.user.username,)))

@login_required
def do_hug(request, target_name):
    target = get_object_or_404(User, username__iexact=target_name)
    hugcheck(request.user)
    if request.user.bonus_data.tokenet():
        x = Hug.objects.create(source=request.user, target=target)
        tw = tweeter()
        try:
            tw.PostUpdate("%i: %s hugged %s! <3" % (x.pk, getattr(getattr(request.user, "bonus_data", None), "twitter", request.user.username), getattr(getattr(target, "bonus_data", None), "twitter", target.username)))
        except twitter.error.TwitterError:
            pass
        pushshsh(x)
        messages.success(request, "%s hugged! <3" % target.username)
    else:
        messages.warning(request, "Sorry, but trim down on hugs please, don't kill our server <3")
    return redirect(reverse("index"))

def do_hug_r(request):
    if "name" in request.GET and User.objects.filter(username__iexact=request.GET["name"]).count() > 0: return redirect(reverse("do_hug", args=(request.GET["name"],)))
    messages.error(request, "I don't know that person...")
    return redirect(reverse("index"))

@login_required
def rehug(request, pk):
    h = get_object_or_404(Hug, pk=pk)
    hugcheck(request.user)
    if request.user.bonus_data.tokenet():
        x = Hug.objects.create(source=request.user, target=h.target, inspiration=h)
        tw = tweeter()
        try:
            tw.PostUpdate("%i: %s rehugged %s! <3" % (x.pk, getattr(getattr(request.user, "bonus_data", None), "twitter", request.user.username), getattr(getattr(h.target, "bonus_data", None), "twitter", h.target.username)))
        except twitter.error.TwitterError:
            pass
        pushshsh(x)
        messages.success(request, "%s was rehugged! <3" % h.target.username)
    else:
        messages.warning(request, "Sorry, but trim down on hugs please, don't kill our server <3")
    return redirect(reverse("index"))

def history(request, pk):
    return render(request, "hug/history.html", {"hug": get_object_or_404(Hug, pk=pk)})

@login_required
def hugback(request, pk):
    h = get_object_or_404(Hug, pk=pk)
    hugcheck(request.user)
    if request.user.bonus_data.tokenet():
        x = Hug.objects.create(source=request.user, target=h.source, inspiration=h)
        tw = tweeter()
        try:
            tw.PostUpdate("%i: %s hugged %s back! <3" % (x.pk, getattr(getattr(request.user, "bonus_data", None), "twitter", request.user.username), getattr(getattr(h.source, "bonus_data", None), "twitter", h.source.username)))
        except twitter.error.TwitterError:
            pass
        pushshsh(x)
        messages.success(request, "%s was hugged back! <3" % h.source)
    else:
        messages.warning(request, "Sorry, but trim down on hugs please, don't kill our server <3")
    return redirect(reverse("index"))

# feeds start here
class HugsFeed(Feed):
    def item_title(self, item):
        return item.nameme()
    def item_description(self, item):
        return item.inspiron()
    def item_link(self, item):
        return reverse("history", args=(item.pk,))
    def item_guid(self, item):
        return item.pk
    def item_pubdate(self, item):
        return item.timestamp

class AllHugsFeedRss(HugsFeed):
    title = "nyuuu.ovh all hugs"
    link = "https://nyuuu.ovh/"
    description = "All hugs that happen on nyuuu.ovh"
    def items(self):
        return Hug.objects.order_by('-timestamp')[:50]
class AllHugsFeedAtom(AllHugsFeedRss):
    feed_type = Atom1Feed
    subtitle = AllHugsFeedRss.description

class UserHgdFeedRss(HugsFeed):
    def get_object(self, request, username):
        return get_object_or_404(User, username=username)
    def title(self, obj):
        return "nyuuu.ovh hugs from %s" % obj.username
    def link(self, obj):
        return "https://nyuuu.ovh/who-is/%s/" % obj.username
    def description(self, obj):
        return "All hugs performed by %s on nyuuu.ovh" % obj.username
    def items(self, obj):
        return obj.hugs_given.order_by("-timestamp")[:50]
class UserHgdFeedAtom(UserHgdFeedRss):
    feed_type = Atom1Feed
    subtitle = UserHgdFeedRss.description

class UserHbyFeedRss(HugsFeed):
    def get_object(self, request, username):
        return get_object_or_404(User, username=username)
    def title(self, obj):
        return "nyuuu.ovh hugs to %s" % obj.username
    def link(self, obj):
        return "https://nyuuu.ovh/who-is/%s/" % obj.username
    def description(self, obj):
        return "All hugs received by %s on nyuuu.ovh" % obj.username
    def items(self, obj):
        return obj.hugs_gotten.order_by("-timestamp")[:50]
class UserHbyFeedAtom(UserHbyFeedRss):
    feed_type = Atom1Feed
    subtitle = UserHbyFeedRss.description
