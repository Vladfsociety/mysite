from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.template.context_processors import csrf
from django.contrib import auth
from .models import Blog, Category, Comment
from .forms import CommentForm


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


def BlogDetailView(request, pk):
    blog = get_object_or_404(Blog, pk = pk)

    return render(
        request,
        'catalog/blog_detail.html',
        context={'blog_title':blog.title, 'blog_registration_time':blog.registration_datetime, 'blog_text':blog.text, 'blog_category':blog.category, 'blog_author':blog.author},
    )
"""

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


class BlogDetailView(View):
    template_name = 'catalog/blog_detail_comment.html'
    comment_form = CommentForm()

    def get(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, id=self.kwargs['blog_id'])
        context = {}
        context.update(csrf(request))
        user = auth.get_user(request)
        # Помещаем в контекст все комментарии, которые относятся к статье
        # попутно сортируя их по пути, ID автоинкрементируемые, поэтому
        # проблем с иерархией комментариев не должно возникать
        context['comments'] = Comment.objects.filter(blog_id=blog.id).order_by('path')
        context['next'] = blog.get_absolute_url()
        # Будем добавлять форму только в том случае, если пользователь авторизован
        if user.is_authenticated:
            context['form'] = self.comment_form

        return render_to_response(template_name=self.template_name, context=context)


@login_required
@require_http_methods(["POST"])
def add_comment(request, blog_id):

    form = CommentForm(request.POST)
    blog = get_object_or_404(Blog, id=blog_id)

    if form.is_valid():
        comment = Comment()
        comment.path = []
        comment.blog_id = blog
        comment.author_id = auth.get_user(request)
        comment.content = form.cleaned_data['comment_area']
        comment.save()

        # Django не позволяет увидеть ID комментария по мы не сохраним его,
        # хотя PostgreSQL имеет такие средства в своём арсенале, но пока не будем
        # работать с сырыми SQL запросами, поэтому сформируем path после первого сохранения
        # и пересохраним комментарий
        try:
            comment.path.extend(Comment.objects.get(id=form.cleaned_data['parent_comment']).path)
            comment.path.append(comment.id)
        except ObjectDoesNotExist:
            comment.path.append(comment.id)

        comment.save()

    return redirect(blog.get_absolute_url())
