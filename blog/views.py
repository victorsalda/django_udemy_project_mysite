# File with the logic of the application. Each view receives an http request, process it and returns a response.

# A view function, or view for short, is simply a Python function that takes a Web request and returns a Web response.

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .models import Post
from .forms import EmailPostForm
from django.core.mail import send_mail


def post_list(request):

    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)

    except PageNotAnInteger:
        # if page is not an integer deliver the first page.
        posts = paginator.page(1)

    except EmptyPage:
        # if page is out of rage deliver the first page.
        posts = paginator.page(paginator.num_pages)

    return render (request, 'post/list.html', { 'page': page,
                                                'posts': posts})

class PostListView (ListView):

    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'post/list.html'



def post_detail(request, year, month, day, post):

    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    return render(request, 'post/detail.html', {'post': post})



def post_share (request,post_id):

    # Retrieve post by id.
    post = get_object_or_404(Post, id=post_id, status = 'published') # Post is a class in the models file.
    sent = False

    if request.method == 'POST':

        # Form was submitted.
        form = EmailPostForm(request.POST)

        if form.is_valid():

            # Form fields passed validation.
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'],cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True

    else:

        form = EmailPostForm()

    return render(request, 'post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})