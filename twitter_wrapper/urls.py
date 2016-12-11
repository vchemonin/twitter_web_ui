from django.conf.urls import url

from . import views

app_name = views.APPLICATION_NAME
urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^user/(?P<screen_name>[a-zA-Z0-9_-]+)$', views.userData, name = 'user_data'),
    url(r'^search/?$', views.search, name = 'search'),
    url(r'^update$', views.forceUpdate, name = 'force_update'),
    url(r'^signin$', views.signIn, name = 'sign_in'),
    url(r'^authorization$', views.authorization, name = 'authorization'),
    url(r'^logout$', views.logOut, name = 'log_out'),
]
