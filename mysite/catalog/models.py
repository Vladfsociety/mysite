from datetime import date, datetime
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import ArrayField


class Category(models.Model):

    name = models.CharField(max_length=30, help_text="Category name")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return '{}'.format(self.name)

    def get_absolute_url(self):
        return reverse('category-detail', args=[str(self.id)])


class Blog(models.Model):

    title = models.CharField(max_length=100, help_text="Blog title")
    registration_datetime = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField('Category', help_text="Select a category for this blog")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.TextField(help_text="Blog text")

    class Meta:
        ordering = ['title']
        permissions = (("can_delete_update", "Can delete update"),)

    def display_category(self):
        return ', '.join([category.name for category in self.category.all()[:3]])

    def __str__(self):
        return '{}'.format(self.title)

    def get_absolute_url(self):
        return reverse('blog-detail', args=[str(self.id)])

    display_category.short_description = 'Category'


class Comment(models.Model):
    class Meta:
        db_table = "comments"

    path = ArrayField(models.IntegerField())
    blog_id = models.ForeignKey(Blog, on_delete=models.CASCADE)
    author_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField('Комментарий')
    pub_date = models.DateTimeField('Дата комментария', auto_now_add=True)

    def __str__(self):
        return self.content[0:200]

    def get_offset(self):
        level = len(self.path) - 1
        if level > 5:
            level = 5
        return level

    def get_col(self):
        level = len(self.path) - 1
        if level > 5:
            level = 5
        return 12 - level
