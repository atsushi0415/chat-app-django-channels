from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Room, Friend, FriendRoom, User
from django.http import Http404
from django.db.models import Q


class ChatRoomView(LoginRequiredMixin, View):
    def get(self, request, room_name):
        room = None
        try:
            room = Room.objects.get(name=room_name)
        except Room.DoesNotExist:
            room = FriendRoom.objects.get(name=room_name)

        context = {
            'room_name': room.name,
            'username': request.user.username,
            
        }
        return render(request, 'chat/chat_room.html', context)
    
class CreateOpenRoomView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'chat/create_open_room.html')
    
    def post(self, request):
        room_name = request.POST.get('room_name')
        if room_name:
            if Room.objects.filter(name=room_name).exists():
                messages.error(request, 'そのルーム名はすでに存在します')
                return redirect('create_open_room')
            
            Room.objects.create(name=room_name)
            messages.success(request, 'ルームが作成されました')
            return redirect('chat_room', room_name=room_name)
        else:
            messages.error(request, 'ルーム名を入力してください')
            return render(request, 'chat/create_open_room.html')
        
class SelectRoomView(View):
    def get(self, request):
        return render(request, 'chat/select_room.html')
    

class CreateFriendRoomView(LoginRequiredMixin, View):
    def get(self, request):
        login_user = request.user.id
        friend_name = Friend.objects.filter(user_id = login_user, request = 1)

        all = {
            'friend_name':friend_name,
            'log':login_user,
        }
        return render(request, 'chat/create_friend_room.html',all)
    
    def post(self, request):
        room_name = request.POST.get('room_name')
        select_friend_id = request.POST.get('select_friend_name')

        if select_friend_id == '':
            messages.error(request, 'フレンドを選択してください')
            return render(request, 'chat/create_friend_room.html')
        
        login_user = request.user
        friend_user = User.objects.get(id=select_friend_id)
        login_user_id = request.user.id

        

        if room_name and select_friend_id:
            if FriendRoom.objects.filter(name=room_name).exists():
                messages.error(request, 'そのルーム名はすでに存在しています')
                return redirect('create_friend_room')
            
            elif FriendRoom.objects.filter(Q(friend = select_friend_id) | Q(friend = login_user_id,user = select_friend_id)).exists():
                messages.error(request, 'すでにフレンドルームが存在しています')
                return redirect('create_friend_room')
            
            FriendRoom.objects.create(name=room_name, user=login_user, friend=friend_user)
            messages.success(request, 'ルームが作成されました')
            return redirect('chat_room', room_name=room_name)
        
        else:
            messages.error(request, 'ルーム名を入力してください')
            return render(request, 'chat/create_friend_room.html')