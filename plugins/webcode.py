from aiohttp import web as webserver
from plugins.miniapp import routes as miniapp_routes
from plugins.website import routes as website_routes


async def bot_run(bot=None):
    _app = webserver.Application(client_max_size=30000000)
    _app["bot"] = bot   # miniapp API uses this client to send files to users
    _app.add_routes(website_routes)   # public site: / , /health , /api/*
    _app.add_routes(miniapp_routes)   # Telegram Mini App: /app , /app/api/*
    return _app
