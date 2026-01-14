import os
from telegram import Update
from bot_telegram_ri import criar_app

TOKEN = os.environ["BOT_TOKEN"]
app = criar_app(TOKEN)

async def handler(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return {"status": "ok"}
