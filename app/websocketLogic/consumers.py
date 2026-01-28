import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the connection (The Handshake)
        self.group_name = "updates_group"
        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        print("WebSocket Connection Established")

        # 1️⃣ Increase active users
        active_users = cache.get("active_users", 0) + 1
        cache.set("active_users", active_users)

        # 2️⃣ Broadcast active users count
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "active_user_update",
                "active_users": active_users,
            }
        )

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print("WebSocket Connection Closed")

         # 3️⃣ Decrease active users
        active_users = max(cache.get("active_users", 1) - 1, 0)
        cache.set("active_users", active_users)

        # 4️⃣ Broadcast updated count
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "active_user_update",
                "active_users": active_users,
            }
        )

    # This method receives messages from the Group (sent by the API view)
    async def send_update(self, event):
        # Send the data to the React frontend
        await self.send(text_data=json.dumps({
            "type": "USER_COUNT_UPDATE",
            'user_count': event['user_count'],
            "teacher_count": event["teacher_count"],

            "student_count": event["student_count"],
            "staff_count": event["staff_count"],
            "placement_count": event["placement_count"],
            "company_count": event["company_count"],
        }))

    # NEW method – required for group_send
    async def active_user_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "ACTIVE_USER_UPDATE",
            "active_users": event["active_users"],
        }))

    async def receive(self, text_data):
        # Handle incoming data
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({
            'message': f"Echo: {data['message']}"
        }))