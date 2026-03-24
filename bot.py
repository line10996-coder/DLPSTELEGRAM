import requests
from bs4 import BeautifulSoup
import asyncio
import os
from telegram import Bot

# ================= CONFIG =================
TOKEN = "8696621470:AAHjzTCA0x8G4uBy6s6ccT78u69R4ih4IZ8"
CHAT_ID = "1371125268"
URL = "https://dlpsgame.com/category/ps5/"
ARQUIVO = "posts_enviados.txt"

bot = Bot(token=TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ================= ARQUIVO =================
def carregar_links():
    if not os.path.exists(ARQUIVO):
        return set()

    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return set(linha.strip() for linha in f.readlines())


def salvar_link(link):
    with open(ARQUIVO, "a", encoding="utf-8") as f:
        f.write(link + "\n")


ultimos_links = carregar_links()

# ================= PEGAR IMAGEM DO POST =================
def pegar_imagem_do_post(link):
    try:
        r = requests.get(link, headers=HEADERS, timeout=10)
        s = BeautifulSoup(r.text, "html.parser")

        imagens = s.find_all("img")

        for img in imagens:
            src = img.get("src")

            # 🔥 FILTRO CERTO (esse resolve)
            if src and "wp-content/uploads" in src:
                if src.startswith("//"):
                    src = "https:" + src
                return src

    except Exception as e:
        print("Erro imagem:", e)

    return None

# ================= SCRAPING =================
def pegar_posts():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)

        print("Status:", response.status_code)

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        posts = []

        titulos = soup.select("h2 a")

        print("Títulos encontrados:", len(titulos))

        for a in titulos:
            titulo = a.get_text(strip=True)
            link = a.get("href")

            if not link or "ps5" not in link.lower():
                continue

            imagem = pegar_imagem_do_post(link)

            print(f"DEBUG → {titulo} | IMG: {imagem}")

            posts.append({
                "titulo": titulo,
                "link": link,
                "imagem": imagem
            })

        print("Posts válidos:", len(posts))

        return posts

    except Exception as e:
        print("Erro scraping:", e)
        return []

# ================= ENVIO =================
async def enviar_post(post):
    msg = f"🔥 <b>NOVO JOGO PS5</b>\n\n{post['titulo']}\n{post['link']}"

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

        await bot.send_message(
            chat_id=CHAT_ID,
            text=msg,
            parse_mode="HTML"
        )

# ================= LOOP =================
async def main():
    global ultimos_links

    print("🚀 BOT INICIADO...")

    while True:
        try:
            posts = pegar_posts()

            if not posts:
                print("Nenhum post encontrado")
            else:
                for post in posts:
                    if post["link"] not in ultimos_links:
                        await enviar_post(post)

                        print("✅ Enviado:", post["titulo"])

                        salvar_link(post["link"])
                        ultimos_links.add(post["link"])

        except Exception as e:
            print("Erro geral:", e)

        await asyncio.sleep(60)

# ================= START =================
asyncio.run(main())
