from django.urls import path
from .proglam.views import HomeView, LoginView, CreateUser, FriendPageView
from .proglam.chat import ChatRoomView, CreateOpenRoomView, SelectRoomView, CreateFriendRoomView
from .proglam.user import MypageView, SearchFriendView,ChangeInfoView

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('home/', HomeView.as_view(), name='home'),
    path('create_user/', CreateUser.as_view(), name='create_user'),
    path('select_room/', SelectRoomView.as_view(), name='select_room'),
    path('create_open_room/', CreateOpenRoomView.as_view(), name='create_open_room'),
    path('create_friend_room/', CreateFriendRoomView.as_view(), name='create_friend_room'),
    path('chat/<str:room_name>/', ChatRoomView.as_view(), name='chat_room'),
    path('mypage/', MypageView.as_view(), name='mypage'),
    path('search_friend/', SearchFriendView.as_view(), name='search_friend'),
    path('friend/<int:friend_id>/', FriendPageView.as_view(), name='friend_page'),
    path('change_info/', ChangeInfoView.as_view(), name='change_info')
]