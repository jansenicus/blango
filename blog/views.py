import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from blog.models import Post
from blog.forms import CommentForm

# Create your views here.
def index(request):
  posts = (
    Post.objects.filter(published_at__lte=timezone.now())
                      .select_related("author")
                      # .only("title", "summary", "content", "author", "published_at", "slug")
                      .defer("created_at", "modified_at")
                      )

  # after retrieving the Posts from db, log how many they are at DEBUG level
  logger.debug("Got %d posts", len(posts))

  return render(request, "blog/index.html", {"posts" : posts})

def post_detail(request, slug):
  post = get_object_or_404(Post, slug=slug)

  # First, we check if the user is active. 
  # Users who are inactive or aren’t logged in (anonymous users) 
  # will fail this test and 
  # default to having the comment_form variable set to None.
  if request.user.is_active:

    # Otherwise, we check the request method. 
    # If it’s not POST, a blank CommentForm is created.

    if request.method == "POST":
      comment_form = CommentForm(request.POST)

      if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.content_object = post
        comment.creator = request.user
        comment.save()
        # log a message when a comment is created
        logger.info("Createad comment on Post %d for user %s", 
                    post.pk,
                    request.user)

        # finally, we perform a redirect back to the current Post (this essentially just refreshes the page for the user so they see their new comment).
        return redirect(request.path_info)
    else:
      # blank CommentForm
      comment_form = CommentForm()
  else:
    comment_form = None

  return render(request, "blog/post-detail.html", 
                {"post": post,
                "comment_form": comment_form})

  
def get_ip(request):
  # view to return the IP address that's connected to Django
  from django.http import HttpResponse
  return HttpResponse(request.META['REMOTE_ADDR'])