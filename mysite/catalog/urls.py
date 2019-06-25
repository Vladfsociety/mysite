from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^categories/$', views.CategoriesListView.as_view(), name='categories'),
    url(r'^category/(?P<pk>\d+)$', views.CategoryBlogsView, name='category-detail'),
    url(r'^blog/(?P<blog_id>\d+)$', views.BlogDetailView.as_view(), name='blog-detail'),
    url(r'^blog/create/$', views.BlogCreate.as_view(), name='blog_create'),
    url(r'^blog/(?P<pk>\d+)/update/$', views.BlogUpdate.as_view(), name='blog_update'),
    url(r'^blog/(?P<pk>\d+)/delete/$', views.BlogDelete.as_view(), name='blog_delete'),
    url(r'^blog/comment/(?P<blog_id>[0-9]+)/$', views.add_comment, name='add_comment'),
]
