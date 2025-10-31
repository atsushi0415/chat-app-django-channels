import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    connected_users_per_room = {}

    async def connect(self):
        # URLからルーム名を取得
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # ルームグループに参加
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # ログインユーザーをそのルームのリストに追加
        user = self.scope['user']
        if user.is_authenticated:
            # ルームのセットが存在しない場合は作成
            if self.room_group_name not in ChatConsumer.connected_users_per_room:
                ChatConsumer.connected_users_per_room[self.room_group_name] = set()
            ChatConsumer.connected_users_per_room[self.room_group_name].add(user.username)
        
        # そのルームの全クライアントにユーザーリストの更新を通知
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_list_update',
                'users': list(ChatConsumer.connected_users_per_room.get(self.room_group_name, set()))
            }
        )

        await self.accept()

    async def disconnect(self, close_code):
        # ルームグループから退出
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # ログインユーザーをそのルームのリストから削除
        user = self.scope['user']
        if user.is_authenticated:
            if self.room_group_name in ChatConsumer.connected_users_per_room:
                ChatConsumer.connected_users_per_room[self.room_group_name].discard(user.username)
                # もしルームに誰もいなくなったら、そのルームのエントリを削除
                if not ChatConsumer.connected_users_per_room[self.room_group_name]:
                    del ChatConsumer.connected_users_per_room[self.room_group_name]

        # そのルームの全クライアントにユーザーリストの更新を通知
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_list_update',
                'users': list(ChatConsumer.connected_users_per_room.get(self.room_group_name, set()))
            }
        )

    # WebSocketからメッセージを受信したときの処理
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username
        
        # ルームグループにメッセージとユーザー名を送信
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    # ルームグループからメッセージを受信したときの処理
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        
        # WebSocketにメッセージとユーザー名を送信
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username
        }))

    # ユーザーリスト更新メッセージを受信したときの処理
    async def user_list_update(self, event):
        users = event['users']
        
        await self.send(text_data=json.dumps({
            'type': 'user_list_update',
            'users': users
        }))