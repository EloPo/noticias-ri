from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters
)

import requests
import pycountry

# ================= CONFIGURAÇÕES =================

TOKEN = "8356540548:AAF7XfeK9dy3ugo8KkS5lsLRsfjQzivl0Kg"
GNEWS_API_KEY = "a68a14382ac2378b57f56114412665dc"

# Continentes com TODOS os países (ISO-3166)
CONTINENTES = {
    "África": [
        "DZ","AO","BJ","BW","BF","BI","CV","CM","CF","TD","KM","CG","CD",
        "CI","DJ","EG","GQ","ER","SZ","ET","GA","GM","GH","GN","GW","KE",
        "LS","LR","LY","MG","MW","ML","MR","MU","MA","MZ","NA","NE","NG",
        "RW","ST","SN","SC","SL","SO","ZA","SS","SD","TZ","TG","TN","UG",
        "ZM","ZW"
    ],
    "América": [
        "AG","AR","BS","BB","BZ","BO","BR","CA","CL","CO","CR","CU","DM",
        "DO","EC","SV","GD","GT","GY","HT","HN","JM","MX","NI","PA","PY",
        "PE","KN","LC","VC","SR","TT","US","UY","VE"
    ],
    "Europa": [
        "AL","AD","AT","BY","BE","BA","BG","HR","CY","CZ","DK","EE","FI",
        "FR","DE","GR","HU","IS","IE","IT","LV","LI","LT","LU","MT","MD",
        "MC","ME","NL","MK","NO","PL","PT","RO","RU","SM","RS","SK","SI",
        "ES","SE","CH","UA","GB","VA"
    ],
    "Ásia": [
        "AF","AM","AZ","BH","BD","BT","BN","KH","CN","GE","IN","ID","IR",
        "IQ","IL","JP","JO","KZ","KW","KG","LA","LB","MY","MV","MN","MM",
        "NP","KP","OM","PK","PH","QA","SA","SG","KR","LK","SY","TJ","TH",
        "TL","TR","TM","AE","UZ","VN","YE"
    ],
    "Oceania": [
        "AU","FJ","KI","MH","FM","NR","NZ","PW","PG","WS","SB","TO","TV",
        "VU"
    ]
}

DOMINIOS_POR_PAIS = {
    "PT": [".pt"],
    "FR": [".fr"],
    "DE": [".de"],
    "ES": [".es"],
    "IT": [".it"],
    "GB": [".uk"],
    "US": [".us", ".com"],
    "BR": [".br"],
    "AR": [".ar"],
    "CL": [".cl"],
    "MX": [".mx"]
}

MIDIA_LOCAL = {
    "Lisboa": [
        "publico.pt",
        "expresso.pt",
        "dn.pt",
        "observador.pt",
        "jn.pt"
    ],
    "Porto": [
        "jn.pt",
        "publico.pt"
    ],
    "Paris": [
        "lemonde.fr",
        "lefigaro.fr",
        "liberation.fr"
    ],
    "Berlin": [
        "tagesspiegel.de",
        "bz-berlin.de"
    ],
    "Madrid": [
        "elpais.com",
        "elmundo.es"
    ]
}


# ================= FUNÇÕES AUXILIARES =================

def nome_pais(codigo):
    return pycountry.countries.get(alpha_2=codigo).name

def teclado_continentes():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(c, callback_data=f"cont|{c}")]
        for c in CONTINENTES.keys()
    ])

def teclado_paises(continente):
    keyboard = [
        [InlineKeyboardButton(nome_pais(c), callback_data=f"pais|{c}")]
        for c in CONTINENTES[continente]
    ]

    keyboard.append([botao_voltar("continente")])
    return InlineKeyboardMarkup(keyboard)

def teclado_midia():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📰 Grande Renome", callback_data="midia|mainstream")],
        [InlineKeyboardButton("🧠 Independente", callback_data="midia|independente")],
        [botao_voltar("cidade")]
    ])

def buscar_noticias_locais(pais, cidade, tipo):
    url = "https://gnews.io/api/v4/search"

    fontes = MIDIA_LOCAL.get(cidade)
    dominios = DOMINIOS_POR_PAIS.get(pais, [])

    if fontes:
        params = {
            "q": cidade,
            "domains": ",".join(fontes),
            "max": 5,
            "apikey": GNEWS_API_KEY
        }
    else:
        params = {
            "q": cidade,
            "max": 5,
            "apikey": GNEWS_API_KEY
        }

    r = requests.get(url, params=params)
    if r.status_code != 200:
        return []

    return r.json().get("articles", [])

def botao_voltar(etapa):
    return InlineKeyboardButton("⬅️ Voltar", callback_data=f"voltar|{etapa}")

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Bem-vindo ao Bot Global de Notícias de Relações Internacionais\n\n"
        "Escolha um continente:",
        reply_markup=teclado_continentes()
    )

async def escolher_continente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    continente = query.data.split("|")[1]
    context.user_data["continente"] = continente

    await query.edit_message_text(
        f"🌍 Continente: {continente}\n\nEscolha um país:",
        reply_markup=teclado_paises(continente)
    )

async def escolher_pais(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pais = query.data.split("|")[1]
    context.user_data["pais"] = pais

    await query.edit_message_text(
        f"🌍 País: {nome_pais(pais)}\n\n📍 Digite o nome da cidade:"
    )

async def receber_cidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cidade"] = update.message.text

    await update.message.reply_text(
        "📰 Escolha o tipo de veículo:",
        reply_markup=teclado_midia()
    )

async def escolher_midia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tipo = query.data.split("|")[1]

    pais = context.user_data["pais"]
    cidade = context.user_data["cidade"]

    await query.edit_message_text(
        "🔎 Buscando notícias conforme suas escolhas..."
    )

    noticias = buscar_noticias_locais(pais, cidade, tipo)

    if not noticias:
        await query.message.reply_text("❌ Nenhuma notícia encontrada.")
        return

    for n in noticias:
        await query.message.reply_text(
            f"📰 {n['title']}\n{n['url']}",
            disable_web_page_preview=True
        )

async def voltar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    etapa = query.data.split("|")[1]

    if etapa == "continente":
        await query.edit_message_text(
            "🌍 Escolha um continente:",
            reply_markup=teclado_continentes()
        )

    elif etapa == "pais":
        continente = context.user_data.get("continente")
        await query.edit_message_text(
            f"🌍 Continente: {continente}\n\nEscolha um país:",
            reply_markup=teclado_paises(continente)
        )

    elif etapa == "cidade":
        pais = context.user_data.get("pais")
        await query.edit_message_text(
            f"🌍 País: {nome_pais(pais)}\n\n📍 Digite o nome da cidade:"
        )

# ================= MAIN =================

def criar_app(token):
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(voltar, pattern="^voltar"))
    app.add_handler(CallbackQueryHandler(escolher_continente, pattern="^cont"))
    app.add_handler(CallbackQueryHandler(escolher_pais, pattern="^pais"))
    app.add_handler(CallbackQueryHandler(escolher_midia, pattern="^midia"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_cidade))

    return app
