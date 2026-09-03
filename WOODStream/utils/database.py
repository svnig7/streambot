import pymongo
import time
import motor.motor_asyncio
from bson.objectid import ObjectId
from bson.errors import InvalidId
from WOODStream.server.exceptions import FIleNotFound

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.black = self.db.blacklist
        self.file = self.db.file
        # New collection for playlists, merged in from telestream-bot.
        self.playlist = self.db.playlist

    async def ensure_indexes(self):
        # Merged in from telestream-bot: keeps playlist lookups/TTL sweeps cheap.
        await self.playlist.create_index("token", unique=True)
        await self.file.create_index("exp")
        await self.playlist.create_index("exp")

#---------------------[ NEW USER ]---------------------#
    def new_user(self, id):
        return dict(
            id=id,
            join_date=time.time(),
            Links=0
        )

# ---------------------[ ADD USER ]---------------------#
    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

# ---------------------[ GET USER ]---------------------#
    async def get_user(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user

# ---------------------[ CHECK USER ]---------------------#
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

# ---------------------[ REMOVE USER ]---------------------#
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

# ---------------------[ BAN, UNBAN USER ]---------------------#
    def black_user(self, id):
        return dict(
            id=id,
            ban_date=time.time()
        )

    async def ban_user(self, id):
        user = self.black_user(id)
        await self.black.insert_one(user)

    async def unban_user(self, id):
        await self.black.delete_one({'id': int(id)})

    async def is_user_banned(self, id):
        user = await self.black.find_one({'id': int(id)})
        return True if user else False

    async def total_banned_users_count(self):
        count = await self.black.count_documents({})
        return count
        
# ---------------------[ ADD FILE TO DB ]---------------------#
    async def add_file(self, file_info):
        file_info["time"] = time.time()
        fetch_old = await self.get_file_by_fileuniqueid(file_info["user_id"], file_info["file_unique_id"])
        if fetch_old:
            # Same file re-sent (e.g. re-uploaded into a new album/playlist) - reuse the
            # existing doc, but still let this upload attach playlist/TTL fields to it.
            extra = {k: v for k, v in file_info.items() if k in ("pl", "pi", "exp", "poster") and v is not None}
            if extra:
                await self.file.update_one({"_id": fetch_old["_id"]}, {"$set": extra})
            return fetch_old["_id"]
        await self.count_links(file_info["user_id"], "+")
        return (await self.file.insert_one(file_info)).inserted_id

# ---------------------[ FIND FILE IN DB ]---------------------#
    async def find_files(self, user_id, range):
        user_files=self.file.find({"user_id": user_id})
        user_files.skip(range[0] - 1)
        user_files.limit(range[1] - range[0] + 1)
        user_files.sort('_id', pymongo.DESCENDING)
        total_files = await self.file.count_documents({"user_id": user_id})
        return user_files, total_files

    async def get_file(self, _id):
        try:
            file_info=await self.file.find_one({"_id": ObjectId(_id)})
            if not file_info:
                raise FIleNotFound
            if file_info.get("exp") and file_info["exp"] < time.time():
                # TTL link expired (feature merged in from telestream-bot) - purge and pretend it never existed.
                await self.file.delete_one({"_id": file_info["_id"]})
                raise FIleNotFound
            return file_info
        except InvalidId:
            raise FIleNotFound
    
    async def get_file_by_fileuniqueid(self, id, file_unique_id, many=False):
        if many:
            return self.file.find({"file_unique_id": file_unique_id})
        else:
            file_info=await self.file.find_one({"user_id": id, "file_unique_id": file_unique_id})
        if file_info:
            return file_info
        return False

# ---------------------[ TOTAL FILES ]---------------------#
    async def total_files(self, id=None):
        if id:
            return await self.file.count_documents({"user_id": id})
        return await self.file.count_documents({})

# ---------------------[ DELETE FILES ]---------------------#
    async def delete_one_file(self, _id):
        await self.file.delete_one({'_id': ObjectId(_id)})

# ---------------------[ UPDATE FILES ]---------------------#
    async def update_file_ids(self, _id, file_ids: dict):
        await self.file.update_one({"_id": ObjectId(_id)}, {"$set": {"file_ids": file_ids}})

# ---------------------[ PAID SYS ]---------------------#
#     async def link_available(self, id):
#         user = await self.col.find_one({"id": id})
#         if user.get("Plan") == "Plus":
#             return "Plus"
#         elif user.get("Plan") == "Free":
#             files = await self.file.count_documents({"user_id": id})
#             if files < 11:
#                 return True
#             return False
        
    async def count_links(self, id, operation: str):
        if operation == "-":
            await self.col.update_one({"id": id}, {"$inc": {"Links": -1}})
        elif operation == "+":
            await self.col.update_one({"id": id}, {"$inc": {"Links": 1}})

# ---------------------[ TTL LINKS (merged in from telestream-bot) ]---------------------#
    async def set_ttl(self, _id, exp):
        """exp is an epoch timestamp, or None to clear the expiry."""
        await self.file.update_one({"_id": ObjectId(_id)}, {"$set": {"exp": exp}})

# ---------------------[ CUSTOM THUMBNAILS (merged in from telestream-bot) ]---------------------#
    async def set_poster(self, _id, poster_url):
        await self.file.update_one({"_id": ObjectId(_id)}, {"$set": {"poster": poster_url}})

# ---------------------[ PLAYLISTS (merged in from telestream-bot) ]---------------------#
    async def add_playlist(self, token, name, items, poster=None, exp=None, owner_id=None):
        doc = dict(
            token=token,
            name=name,
            items=items,
            poster=poster,
            exp=exp,
            owner_id=owner_id,
            time=time.time(),
        )
        await self.playlist.update_one({"token": token}, {"$set": doc}, upsert=True)
        return token

    async def get_playlist(self, token):
        doc = await self.playlist.find_one({"token": token})
        if not doc:
            return None
        if doc.get("exp") and doc["exp"] < time.time():
            await self.playlist.delete_one({"token": token})
            return None
        return doc

    async def rm_playlist(self, token):
        await self.playlist.delete_one({"token": token})

# ---------------------[ EXPIRY SWEEP (merged in from telestream-bot) ]---------------------#
    async def purge_expired(self):
        """Deletes any file/playlist docs whose TTL has passed. Returns (files, playlists) removed."""
        now = time.time()
        files_result = await self.file.delete_many({"exp": {"$ne": None, "$lt": now}})
        playlists_result = await self.playlist.delete_many({"exp": {"$ne": None, "$lt": now}})
        return files_result.deleted_count, playlists_result.deleted_count