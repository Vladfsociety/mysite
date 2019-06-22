from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from .models import Blog, Category


def index(request):
    num_blogs=Blog.objects.all().count()
    num_categories=Category.objects.all().count()

    return render(
        request,
        'index.html',
        context={'num_blogs':num_blogs,'num_categories':num_categories},
    )


class CategoriesListView(generic.ListView):
    model = Category
    paginate_by = 5


def CategoryBlogsView(request, pk):
    category = get_object_or_404(Category, pk = pk)
    category_blogs = Blog.objects.filter(category = category)

    paginator = Paginator(category_blogs, 1) # Show 25 contacts per page

    page = paginator.page(1)
    #!!!!!!!!!!!!
    return render(
        request,
        'catalog/category_blogs.html',
        context={'category_blogs':category_blogs, 'page_obj':page},
    )

"""
class BlogDetailView(generic.DetailView):
    model = Blog

"""
def BlogDetailView(request, pk):
    blog = get_object_or_404(Blog, pk = pk)

    return render(
        request,
        'catalog/blog_detail.html',
        context={'blog_title':blog.title, 'blog_registration_time':blog.registration_datetime, 'blog_text':blog.text, 'blog_category':blog.category, 'blog_author':blog.author},
    )


class BlogCreate(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ['title','category','text']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(BlogCreate, self).form_valid(form)


class BlogUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "catalog.can_delete_update"
    model = Blog
    fields = ['title','category','text']


class BlogDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "catalog.can_delete_update"
    model = Blog
    success_url = reverse_lazy('index')
