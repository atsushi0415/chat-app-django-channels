from django.contrib import admin
from .models import Room, Friend, FriendRoom, Userplus

admin.site.register(Room)
admin.site.register(Friend)
admin.site.register(FriendRoom)
admin.site.register(Userplus)