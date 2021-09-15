from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	pass

class Follow(models.Model):
	follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following") # o user que segue
	following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower") # o user que é seguido

	def __str__(self):
		return f"'{self.follower}' is following '{self.following}'"

class Post(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user") 
	post = models.CharField(max_length=300)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Post id: {self.id} - user: {self.user}"

	def likeCount(self):
		return Like.objects.filter(post=self.id).count()

	def userLiked(self, user_id):
		qs_likes = Like.objects.filter(user_id=user_id, post=self.id).count()
		liked = True if qs_likes > 0 else False

		return liked

	def serialize(self):
		return {
			"likes": self.likes,
		}

class Like(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likeduser") 
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likedpost")

	def __str__(self):
		return f"{self.user} liked: {self.post}"