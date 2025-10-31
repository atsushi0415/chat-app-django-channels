from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Friend(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend_of', on_delete=models.CASCADE)
    request = models.CharField(max_length=1)

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"{self.user.username} <-> {self.friend.username}"
    
class FriendRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User,related_name='user',on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend',)

    def __str__(self):
        return self.name
    
class Userplus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friend_code = models.IntegerField()
    introduce = models.CharField(max_length=300)
    hobby = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user} -> {self.friend_code}"
