from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django import forms
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.views.generic.edit import FormMixin
from .forms import CommentForm
from .models import Post

# Create your views here.

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        queryset= Post.objects.filter(author = user).order_by('-date_posted')
        return queryset



class PostDetailView(FormMixin, DetailView):
    model = Post
    form_class = CommentForm 

    def success_url(self):
        return reverse('post-detail', kwargs={'pk': self.object.pk})

    def context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden
        self.object = self.get_object
        form = self.get_form
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        new_comment = form.save(commit=False)
        new_comment.post = self.get_object()
        return super().form_valid(form)



class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = [
        'title',
        'content'
    ]
    def form_valid(self, form):
        form.instance.author = self.request.user 
        return super().form_valid(form )


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = [
        'title',
        'content'
    ]
    def form_valid(self, form):
        form.instance.author = self.request.user 
        return super().form_valid(form )

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False



class PostLatestView(ListView):
    model = Post
    template_name = 'blog/post_latest.html'
    ordering = ['-date_posted']
    
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user)
        # queryset = Post.objects.filter(author=user).order_by('-date_posted')[:3]
        queryset = Post.objects.all()[:3]
        self.object_list = self.get_queryset()
        context = {
            'queryset':queryset
        }
        print(context)
        return self.render_to_response(context)       


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
