import motor.motor_asyncio
from sample_info import tempDict
from info import DATABASE_NAME, DATABASE_URI, SECONDDB_URI

class Database:
    
    def __init__(self, database_name):
        # Primary DB
        self._client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups

        # Secondary DB
        self._client2 = motor.motor_asyncio.AsyncIOMotorClient(SECONDDB_URI)
        self.db2 = self._client2[database_name]
        self.col2 = self.db2.users
        self.grp2 = self.db2.groups

    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )

    def new_group(self, id, title):
        return dict(
            id=id,
            title=title,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        if tempDict['indexDB'] == DATABASE_URI:
            await self.col.insert_one(user)
        else:
            await self.col2.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        if not user:
            user = await self.col2.find_one({'id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = (await self.col.count_documents({})) + (await self.col2.count_documents({}))
        return count

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=""
        )
        user = await self.col.find_one({'id': int(id)})
        if user:
            await self.col.update_one({'id': int(id)}, {'$set': {'ban_status': ban_status}})
        else:
            await self.col2.update_one({'id': int(id)}, {'$set': {'ban_status': ban_status}})

    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        user = await self.col.find_one({'id': int(user_id)})
        if user:
            await self.col.update_one({'id': int(user_id)}, {'$set': {'ban_status': ban_status}})
        else:
            await self.col2.update_one({'id': int(user_id)}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=""
        )
        user = await self.col.find_one({'id': int(id)})
        if user:
            return user.get('ban_status', default)
        else:
            user = await self.col2.find_one({'id': int(id)})
            if user:
                return user.get('ban_status', default)
        return default

    async def add_chat(self, chat, title):
        chat_data = self.new_group(chat, title)
        if tempDict['indexDB'] == DATABASE_URI:
            await self.grp.insert_one(chat_data)
        else:
            await self.grp2.insert_one(chat_data)

    async def get_chat(self, id):
        chat = await self.grp.find_one({'id': int(id)})
        if chat:
            return chat.get('chat_status')
        else:
            chat = await self.grp2.find_one({'id': int(id)})
            if chat:
                return chat.get('chat_status')
        return False

    async def total_chat_count(self):
        count = (await self.grp.count_documents({})) + (await self.grp2.count_documents({}))
        return count

    async def get_all_users(self):
        users_primary = await self.col.find({}).to_list(length=None)
        users_secondary = await self.col2.find({}).to_list(length=None)
        return users_primary + users_secondary

    async def get_all_chats(self):
        chats_primary = await self.grp.find({}).to_list(length=None)
        chats_secondary = await self.grp2.find({}).to_list(length=None)
        return chats_primary + chats_secondary

db = Database(DATABASE_NAME)
