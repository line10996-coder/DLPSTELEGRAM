import asyncio
import os
from bs4 import BeautifulSoup
from telegram import Bot
import cloudscraper

# ================= CONFIG =================
TOKEN = "8696621470:AAHjzTCA0x8G4uBy6s6ccT78u69R4ih4IZ8"
CHAT_ID = "1371125268"
URL = "https://dlpsgame.com/category/ps5/"
ARQUIVO = "ultimo_post.txt"

bot = Bot(token=TOKEN)

scraper = cloudscraper.create_scraper()

# ================= ARQUIVO =================
def carregar_ultimo():
    if not os.path.exists(ARQUIVO):
        return None

    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return f.read().strip()


def salvar_ultimo(link):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        f.write(link)


ultimo_link = carregar_ultimo()

# ================= SCRAPING =================
def pegar_ultimo_post():
    try:
        r = scraper.get(URL, timeout=15)

        if r.status_code != 200:
            print("Erro status:", r.status_code)
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        artigo = soup.find("article")
        if not artigo:
            return None

        a = artigo.find("h2").find("a")

        titulo = a.get_text(strip=True)
        link = a.get("href")

        img_tag = artigo.find("img")

        imagem = None
        if img_tag:
            imagem = (
                img_tag.get("data-src")
                or img_tag.get("data-lazy-src")
                or img_tag.get("src")
            )

            if imagem and imagem.startswith("//"):
                imagem = "https:" + imagem

        print(f"DEBUG → {titulo} | IMG: {imagem}")

        return {
            "titulo": titulo,
            "link": link,
            "imagem": imagem
        }

    except Exception as e:
        print("Erro scraping:", e)
        return None

# ================= ENVIO =================
async def enviar(post):
    msg = (
        f"🎮 <b>NOVO JOGO PS5 DISPONÍVEL</b>\n\n"
        f"<b>{post['titulo']}</b>\n\n"
        f"🔗 <a href='{post['link']}'>Baixar Agora</a>"
    )

    try:
        if post["imagem"]:
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=post["imagem"],
                caption=msg,
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=msg,
                parse_mode="HTML"
            )

    except Exception as e:
        print("Erro envio:", e)

# ================= LOOP =================
async def main():
    global ultimo_link

    print("🚀 BOT PROFISSIONAL INICIADO...")

    while True:
        try:
            post = pegar_ultimo_post()

            if not post:
                print("Nenhum post")
            else:
                if post["link"] != ultimo_link:
                    print("🔥 NOVO JOGO DETECTADO!")

                    await enviar(post)

                    salvar_ultimo(post["link"])
                    ultimo_link = post["link"]

                else:
                    print("Sem novidades...")

        except Exception as e:
            print("Erro geral:", e)

        await asyncio.sleep(60)

asyncio.run(main())
