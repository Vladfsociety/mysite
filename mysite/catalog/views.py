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
from django.contrib.auth import login, authenticate
from .models import Blog, Category
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from .forms import SignUpForm
from .tokens import account_activation_token


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            from_email = 'kobylnikvlad@gmail.com'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, from_email, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


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
