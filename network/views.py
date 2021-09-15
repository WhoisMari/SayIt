import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import User, Post, Follow, Like


def index(request):
	posts = []

	if request.method == "POST":
		user = request.user
		new_post = request.POST.get("new_post", "")
		if new_post != "":
			Post.objects.create(user = user, post = new_post)

	qs_posts = Post.objects.all().order_by('-created_at')

	for post in qs_posts:
		if request.user.is_authenticated:
			post.user_liked = post.userLiked(request.user)
		posts.append(post)

	paginator = Paginator(posts, 10) # object + number of posts (objects) per page 
	page_number = request.GET.get('page') # get the page number
	page_obj = paginator.get_page(page_number) 

	context = {
		"page_obj": page_obj,
	}

	return render(request, "network/index.html", context)


def login_view(request):
	if request.method == "POST":

		# Attempt to sign user in
		username = request.POST["username"]
		password = request.POST["password"]
		user = authenticate(request, username=username, password=password)

		# Check if authentication successful
		if user is not None:
			login(request, user)
			messages.info(request, "Welcome back!")
			return redirect("index")
		else:
			messages.warning(request, "Invalid username and/or password.")
			return render(request, "network/login.html")
	else:
		return render(request, "network/login.html")


@login_required
def logout_view(request):
	logout(request)
	return redirect("index")


def register(request):
	if request.method == "POST":
		username = request.POST["username"]
		email = request.POST["email"]
		password = request.POST["password"]
		confirmation = request.POST["confirmation"]
		if password != confirmation:
			messages.warning(request, "Passwords must match")
			return render(request, "network/register.html")

		try:
			user = User.objects.create_user(username, email, password)
			user.save()
		except IntegrityError:
			messages.warning(request, "Username already taken")
			return render(request, "network/register.html")

		login(request, user)
		messages.success(request, "Registered successfully")
		return redirect("index")

	else:
		return render(request, "network/register.html")

def following(request):
	posts = []
	user = request.user
	following = Follow.objects.filter(follower=user).values('following_id')

	qs_posts = Post.objects.filter(user__in=following).order_by('-created_at')

	for post in qs_posts:
		if request.user.is_authenticated:
			post.user_liked = post.userLiked(request.user)
		posts.append(post)

	paginator = Paginator(posts, 10) # object + number of posts (objects) per page 
	page_number = request.GET.get('page') # get the page number
	page_obj = paginator.get_page(page_number) 

	context = {
		"page_obj": page_obj,
	}
	
	return render(request, "network/following.html", context)

def profile(request, user):
	posts = []

	current_user = User.objects.get(id=user)
	# self.is_watched = True if self.watchers.filter(id=user_id) else False
	button = "Follow" if Follow.objects.filter(follower=request.user, following=current_user).count() == 0 else "Unfollow"

	if request.method == "POST":
		if request.POST["button"] == "Follow":
			button = "Unfollow"
			Follow.objects.create(follower=request.user, following=current_user)
		else:
			button = "Follow"
			Follow.objects.get(follower=request.user, following=current_user).delete()

	qs_posts = Post.objects.filter(user=current_user.id).order_by('-created_at')

	for post in qs_posts:
		if request.user.is_authenticated:
			post.user_liked = post.userLiked(request.user)
		posts.append(post)

	paginator = Paginator(posts, 10) # object + number of posts (objects) per page 
	page_number = request.GET.get('page') # get the page number
	page_obj = paginator.get_page(page_number) 

	context = {
		"current_user": current_user,
		"followers": Follow.objects.filter(following=current_user).count(),
		"following": Follow.objects.filter(follower=current_user).count(), 
		"page_obj": page_obj,
		"button": button
	}
	
	return render(request, "network/profile.html", context)

@csrf_exempt
def edit(request, post_id):
	post = Post.objects.get(id=post_id)
	if request.method == "PUT":
		data = json.loads(request.body)
		if data.get("post") is not None:
			post.post = data["post"]
		post.save()
		return HttpResponse(status=204)

@csrf_exempt
def like(request, post_id):
	post = Post.objects.get(id=post_id)
	liked = post.userLiked(request.user)

	if request.method == "GET":
		if liked:
			Like.objects.filter(user=request.user, post=post).delete()
		else:
			Like.objects.create(user=request.user, post=post)
		return JsonResponse({"liked": liked, "likes": post.likeCount()})
