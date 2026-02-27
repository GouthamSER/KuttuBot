import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, USE_CAPTION_FILTER

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME


async def save_file(media):
    """Save file in database"""
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    try:
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption.html if media.caption else None,
        )
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
        return False, 2
    else:
        try:
            await file.commit()
        except DuplicateKeyError:
            logger.warning(
                f'{getattr(media, "file_name", "NO_FILE")} is already saved in database'
            )
            return False, 0
        else:
            logger.info(f'{getattr(media, "file_name", "NO_FILE")} is saved to database')
            return True, 1


async def get_search_results(query, file_type=None, max_results=10, offset=0, filter=False):
    """For given query return (results, next_offset)"""
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)
    next_offset = offset + max_results

    if next_offset > total_results:
        next_offset = ''

    cursor = Media.find(filter)
    cursor.sort('$natural', -1)
    cursor.skip(offset).limit(max_results)
    files = await cursor.to_list(length=max_results)

    return files, next_offset, total_results


async def get_file_details(query):
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails


async def get_movie_list(max_results=30):
    """
    Returns a list of recent movie file names.
    Movies are identified by NOT having episode/season patterns like S01E01.
    """
    try:
        # Episode pattern — if file name matches this, it's a series not a movie
        series_pattern = re.compile(
            r'(s\d{1,2}[\s\.\-_]*e\d{1,2}|season[\s\.\-_]*\d+|episode[\s\.\-_]*\d+|\b\d+x\d+\b)',
            flags=re.IGNORECASE
        )
        cursor = Media.find({})
        cursor.sort('$natural', -1)
        cursor.limit(max_results * 5)  # fetch extra to filter down to movies
        all_files = await cursor.to_list(length=max_results * 5)

        movies = []
        seen = set()
        for file in all_files:
            name = file.file_name or ""
            # Skip if it looks like a series episode
            if series_pattern.search(name):
                continue
            # Clean up name for display
            clean_name = re.sub(r'\.(mkv|mp4|avi|mov|wmv|flv|webm)$', '', name, flags=re.IGNORECASE).strip()
            if clean_name and clean_name not in seen:
                seen.add(clean_name)
                movies.append(clean_name)
            if len(movies) >= max_results:
                break

        return movies
    except Exception as e:
        logger.exception(f"Error in get_movie_list: {e}")
        return []


async def get_series_grouped(max_results=50):
    """
    Returns a dict of { series_title: [episode_numbers] } for recent series.
    Series are identified by having S01E01 or similar patterns in the file name.
    """
    try:
        # Match series episode patterns e.g. S01E01, S1E1, Season 1 Episode 1
        episode_pattern = re.compile(
            r's(\d{1,2})[\s\.\-_]*e(\d{1,2})',
            flags=re.IGNORECASE
        )

        cursor = Media.find({})
        cursor.sort('$natural', -1)
        cursor.limit(max_results * 10)
        all_files = await cursor.to_list(length=max_results * 10)

        series_dict = {}
        for file in all_files:
            name = file.file_name or ""
            match = episode_pattern.search(name)
            if not match:
                continue

            ep_num = int(match.group(2))  # episode number

            # Extract series title = everything before the SxxExx match
            title_raw = name[:match.start()].strip()
            # Clean up title
            title = re.sub(r'[\._\-]+', ' ', title_raw).strip()
            title = re.sub(r'\s+', ' ', title).strip()

            if not title:
                continue

            if title not in series_dict:
                series_dict[title] = set()
            series_dict[title].add(ep_num)

            if len(series_dict) >= max_results:
                break

        # Convert sets to sorted lists
        return {title: sorted(eps) for title, eps in series_dict.items()}

    except Exception as e:
        logger.exception(f"Error in get_series_grouped: {e}")
        return {}


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
