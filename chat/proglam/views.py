from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Room, FriendRoom, Userplus, Friend
import sqlite3 as splite3
from django.db.models import Q 
import random

class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        rooms = Room.objects.all()
        user_id = request.user.id
        
        # ログインユーザーが user または friend に含まれる FriendRoom を取得
        friend_rooms = FriendRoom.objects.filter(Q(user=user_id) | Q(friend=user_id))
        
        # ★ここから追加/修正
        friend_rooms_with_partner = []
        for room in friend_rooms:
            # ログインユーザーが room.user だった場合、相手は room.friend
            if room.user.id == user_id:
                partner_username = room.friend.username
            # ログインユーザーが room.friend だった場合、相手は room.user
            else:
                partner_username = room.user.username
            
            # 辞書を作成し、ルームオブジェクトの情報と相手のユーザー名を含める
            room_info = {
                'name': room.name,
                'partner': partner_username  # 相手のユーザー名を格納
            }
            friend_rooms_with_partner.append(room_info)
        # ★ここまで追加/修正

        context = {
            'username': request.user.username,
            'rooms': rooms,
            'friend_rooms': friend_rooms_with_partner, # 修正したリストを使用
        }
        return render(request, 'chat/home.html', context)

class LoginView(View):
    def get(self, request):
        return render(request, 'chat/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'ユーザー名かパスワードが正しくない') 
        return render(request, 'chat/login.html')
    
class CreateUser(View):
    def get(self, request):
        return render(request, 'chat/create_user.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        again_pass = request.POST.get('again_pass')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'そのユーザー名はすでに存在します')
            return render(request, 'chat/create_user.html')

        if password != again_pass:
            messages.error(request, 'パスワードが一致しません')
            return render(request, 'chat/create_user.html')
        
        if username and password and again_pass:
            while True:
                friend_code = random.randint(10000000, 99999999)
                if not Userplus.objects.filter(friend_code=friend_code).exists():
                    break
            User.objects.create_user(username=username, password=password)
            Userplus.objects.create(user=User.objects.get(username=username), friend_code=friend_code)
            messages.success(request, 'ユーザーが作成されました')
            return redirect('login')
        else:
            messages.error(request, 'ユーザー名とパスワードを入力してください')
        return render(request, 'chat/create_user.html')
    
class FriendPageView(View):
    def get(self, request, friend_id):
        friend_user = get_object_or_404(User, id=friend_id)
        friend_request = Friend.objects.get(Q(user = request.user, friend = friend_id) | Q(friend = request.user, user = friend_id))
        friend_user_info = Userplus.objects.get(user = friend_user)

        context = {
            'friend_user': friend_user,
            'no_friend': friend_user_info,
            'friend_request': friend_request,
            'friend_id':friend_id
        }
        return render(request, 'chat/friend_page.html', context)
    
    def post(self, request, friend_id):
        if 'yes' in request.POST:
            friend = get_object_or_404(Friend, user=friend_id, friend=request.user)
            friend.request = 1
            friend.save()
            return redirect('home')
        
        elif 'no' in request.POST:
            friend = get_object_or_404(Friend, user=friend_id, friend=request.user)
            friend.delete()
            return redirect('home')
        
        elif 'delete' in request.POST:
            friend_to_delete = get_object_or_404(Friend, Q(user=request.user, friend=friend_id) | Q(user = friend_id, friend = request.user))
            friend_to_delete.delete()
            chat_delete = FriendRoom.objects.filter(user=request.user, friend=friend_id).exists()
            if chat_delete:
                chat_delete.delete()
            return redirect('home')
        return redirect('home')