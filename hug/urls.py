from django.conf.urls import include, url
from django.contrib import admin
from hug.views import AllHugsFeedRss, AllHugsFeedAtom, UserHgdFeedRss, UserHgdFeedAtom, UserHbyFeedAtom, UserHbyFeedRss

urlpatterns = [
    # Examples:
    # url(r'^$', 'hug.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'hug.views.index', name='index'),
    url(r'^rss/$', AllHugsFeedRss()),
    url(r'^atom/$', AllHugsFeedAtom()),
    url(r'^(?P<pk>\d+)/$', 'hug.views.onehug', name='onehug'),
    url(r'^i-want/to-rehug/(?P<pk>\d+)/$', 'hug.views.rehug', name='rehug'),
    url(r'^i-want/to-hug-back/(?P<pk>\d+)/$', 'hug.views.hugback', name='hugback'),
    url(r'^i-want/to-hug/(?P<target_name>[A-Za-z0-9\-\._]+)/$', 'hug.views.do_hug', name='do_hug'),
    url(r'^i-want/to-hug/$', 'hug.views.do_hug_r', name='do_hug_r'),
    url(r'^i-want/to-know-what-led-to/(?P<pk>\d+)/$', 'hug.views.history', name='history'),
    url(r'^who-is/(?P<name>[A-Za-z0-9\-\._]+)/$', 'hug.views.user', name='user'),
    url(r'^who-hugged/(?P<name>[A-Za-z0-9\-\._]+)\/$', 'hug.views.user_hby', name="user_hby_json"),
    url(r'^who/(?P<name>[A-Za-z0-9\-\._]+)/hugged\/$', 'hug.views.user_hgd', name="user_hgd_json"),
    url(r'^who-hugged/(?P<username>[A-Za-z0-9\-\._]+)\/rss/$', UserHbyFeedRss()),
    url(r'^who/(?P<username>[A-Za-z0-9\-\._]+)/hugged\/rss/$', UserHgdFeedRss()),
    url(r'^who-hugged/(?P<username>[A-Za-z0-9\-\._]+)\/atom/$', UserHbyFeedAtom()),
    url(r'^who/(?P<username>[A-Za-z0-9\-\._]+)/hugged\/atom/$', UserHgdFeedAtom()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/profile/', 'hug.views.showme', name='profile'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^settings/', 'hug.views.settings', name='settings'),
]
