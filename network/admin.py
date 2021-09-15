from django.contrib import admin
from .models import User, Like, Follow, Post
# Register your models here.

admin.site.register(User)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(Post)