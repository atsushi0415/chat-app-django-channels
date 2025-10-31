from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Friend, Userplus
from django.db.models import Q

    
class MypageView(LoginRequiredMixin, View):
    def get(self, request):
        username = request.user.username
        user_id = request.user.id
        user_code = Userplus.objects.get(user = user_id)
        friend = Friend.objects.filter(Q(user = user_id, request = 1) | Q(friend = user_id, request = 1))
        no_friend = Friend.objects.filter(friend = user_id, request=0)
        all = {
            'username':username,
            'user_code':user_code,
            'friend': friend,
            'no_friend':no_friend,
        }
        return render(request, 'chat/mypage.html', all)

class SearchFriendView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'chat/search_friend.html')
    
    def post(self, request):
        if 'yes' in request.POST:
            found_username = request.POST.get('search_user')
            search_username = request.POST.get('friend_code')

            if found_username:
                found_user = User.objects.get(username=found_username)
                if Friend.objects.filter(Q(friend=request.user, user=found_user, request = 1) | Q(friend=found_user, user=request.user, request = 1)).exists():
                    messages.error(request, 'すでにフレンドです')
                elif Friend.objects.filter(friend=request.user, user=found_user, request = 0).exists():
                    messages.error(request, 'すでにリクエストを送っています')
                elif Userplus.objects.filter(user=request.user, friend_code=search_username).exists():
                    messages.error(request, '自分のフレンドコードです')
                else:
                    Friend.objects.create(user=request.user, friend=found_user, request = 0)
                    messages.success(request, f'「{found_username}」さんにフレンドに申請しました')
            return redirect('home')


        elif 'no' in request.POST:
            return redirect('search_friend')

        else:
            search_username = request.POST.get('friend_code')
            user_id = request.user.id
            user = Userplus.objects.get(user = user_id)
            log_user_id = str(user.friend_code)

            if search_username == log_user_id:
                messages.error(request, 'あなたのユーザー名です')
                return render(request, 'chat/search_friend.html')
            
            try:
                found_user_obj = Userplus.objects.get(friend_code=search_username)
                return render(request, 'chat/search_friend.html', {'found_user': found_user_obj})
            except Userplus.DoesNotExist:
                messages.error(request, 'そのユーザーは存在しません')
                return render(request, 'chat/search_friend.html')
            
class ChangeInfoView(View):
    def get(self, request):
        user_id = request.user.id
        user_code = Userplus.objects.get(user = user_id)
        friend = Friend.objects.filter(user = user_id, request = 1)
        all = {
            'user_code':user_code,
            'friend': friend,
        }
        return render(request, 'chat/change_info.html',all)
    
    def post(self, request):
        change_intro = request.POST.get('change_intro')
        change_hobby = request.POST.get('change_hobby')
        userplus_instance = get_object_or_404(Userplus, user=request.user)
        userplus_instance.introduce = change_intro
        userplus_instance.hobby = change_hobby
        userplus_instance.save() 
        return redirect('mypage')