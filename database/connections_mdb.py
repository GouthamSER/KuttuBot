import pymongo
from sample_info import tempDict
from info import DATABASE_URI, DATABASE_NAME, SECONDDB_URI
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Connect to the first database
myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]
mycol = mydb['CONNECTION']

# Connect to the second database
myclient2 = pymongo.MongoClient(SECONDDB_URI)
mydb2 = myclient2[DATABASE_NAME]
mycol2 = mydb2['CONNECTION']


# Add a connection to the correct database
async def add_connection(group_id, user_id):
    # Select the correct collection based on tempDict
    if tempDict['indexDB'] == DATABASE_URI:
        mycol_to_use = mycol
    else:
        mycol_to_use = mycol2

    query = mycol_to_use.find_one(
        { "_id": user_id },
        { "_id": 0, "active_group": 0 }
    )
    
    if query is not None:
        group_ids = [x["group_id"] for x in query["group_details"]]
        if group_id in group_ids:
            return False

    group_details = {
        "group_id": group_id
    }

    data = {
        '_id': user_id,
        'group_details': [group_details],
        'active_group': group_id,
    }

    if mycol.count_documents({"_id": user_id}) == 0 and mycol2.count_documents({"_id": user_id}) == 0:
        try:
            mycol_to_use.insert_one(data)
            return True
        except:
            logger.exception('Some error occurred!', exc_info=True)
            return False
    else:
        try:
            mycol_to_use.update_one(
                {'_id': user_id},
                {
                    "$push": {"group_details": group_details},
                    "$set": {"active_group": group_id}
                }
            )
            return True
        except:
            logger.exception('Some error occurred!', exc_info=True)
            return False


# Get the active connection for a user
async def active_connection(user_id):
    # Select the correct collection based on tempDict
    if tempDict['indexDB'] == DATABASE_URI:
        mycol_to_use = mycol
    else:
        mycol_to_use = mycol2

    query = mycol_to_use.find_one(
        { "_id": user_id },
        { "_id": 0, "group_details": 0 }
    )
    
    if not query:
        return None
    
    group_id = query['active_group']
    return int(group_id) if group_id is not None else None


# Get all connections for a user
async def all_connections(user_id):
    # Select the correct collection based on tempDict
    if tempDict['indexDB'] == DATABASE_URI:
        mycol_to_use = mycol
    else:
        mycol_to_use = mycol2

    query = mycol_to_use.find_one(
        { "_id": user_id },
        { "_id": 0, "active_group": 0 }
    )
    
    if query is not None:
        return [x["group_id"] for x in query["group_details"]]
    else:
        return None


# Check if a user is active in a particular group
async def if_active(user_id, group_id):
    # Select the correct collection based on tempDict
    if tempDict['indexDB'] == DATABASE_URI:
        mycol_to_use = mycol
    else:
        mycol_to_use = mycol2

    query = mycol_to_use.find_one(
        { "_id": user_id },
        { "_id": 0, "group_details": 0 }
    )
    
    return query is not None and query['active_group'] == group_id


# Make a user active in a particular group
async def make_active(user_id, group_id):
    # Select the correct collection based on tempDict
    if tempDict['indexDB'] == DATABASE_URI:
        mycol_to_use = mycol
    else:
        mycol_to_use = mycol2

    update = mycol_to_use.update_one(
        {'_id': user_id},
        {"$set": {"active_group": group_id}}
    )
    
    return update.modified_count != 0


# Make a user inactive
async def make_inactive(user_id):
    # Select the correct collection based on tempDict
    if tempDict['indexDB'] == DATABASE_URI:
        mycol_to_use = mycol
    else:
        mycol_to_use = mycol2

    update = mycol_to_use.update_one(
        {'_id': user_id},
        {"$set": {"active_group": None}}
    )
    
    return update.modified_count != 0


# Delete a user's connection to a specific group
async def delete_connection(user_id, group_id):
    # Select the correct collection based on tempDict
    if tempDict['indexDB'] == DATABASE_URI:
        mycol_to_use = mycol
    else:
        mycol_to_use = mycol2

    try:
        update = mycol_to_use.update_one(
            {"_id": user_id},
            {"$pull": {"group_details": {"group_id": group_id}}}
        )
        
        if update.modified_count == 0:
            return False
        
        query = mycol_to_use.find_one(
            { "_id": user_id },
            { "_id": 0 }
        )
        
        if len(query["group_details"]) >= 1:
            if query['active_group'] == group_id:
                prvs_group_id = query["group_details"][len(query["group_details"]) - 1]["group_id"]
                mycol_to_use.update_one(
                    {'_id': user_id},
                    {"$set": {"active_group": prvs_group_id}}
                )
        else:
            mycol_to_use.update_one(
                {'_id': user_id},
                {"$set": {"active_group": None}}
            )
        return True
    except Exception as e:
        logger.exception(f'Some error occurred! {e}', exc_info=True)
        return False
