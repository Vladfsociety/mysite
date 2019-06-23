from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^categories/$', views.CategoriesListView.as_view(), name='categories'),
    url(r'^category/(?P<pk>\d+)$', views.CategoryBlogsView, name='category-detail'),
    url(r'^blog/(?P<pk>\d+)$', views.BlogDetailView, name='blog-detail'),
    url(r'^blog/create/$', views.BlogCreate.as_view(), name='blog_create'),
    url(r'^blog/(?P<pk>\d+)/update/$', views.BlogUpdate.as_view(), name='blog_update'),
    url(r'^blog/(?P<pk>\d+)/delete/$', views.BlogDelete.as_view(), name='blog_delete'),
]
