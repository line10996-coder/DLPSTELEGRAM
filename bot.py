import asyncio
import os
from bs4 import BeautifulSoup
from telegram import Bot
import cloudscraper

# ================= CONFIG =================
TOKEN = "8696621470:AAHjzTCA0x8G4uBy6s6ccT78u69R4ih4IZ8"
CHAT_ID = "1371125268"
URL = "https://dlpsgame.com/category/ps5/"
ARQUIVO = "posts_enviados.txt"

bot = Bot(token=TOKEN)

# 🔥 BYPASS CLOUDFLARE
scraper = cloudscraper.create_scraper()

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

# ================= SCRAPING =================
def pegar_posts():
    try:
        response = scraper.get(URL, timeout=15)

        print("Status:", response.status_code)

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        posts = []
        artigos = soup.find_all("article")

        print("Artigos encontrados:", len(artigos))

        for art in artigos:
            h2 = art.find("h2")
            if not h2:
                continue

            a = h2.find("a")
            if not a:
                continue

            titulo = a.get_text(strip=True)
            link = a.get("href")

            if not link or "ps5" not in link.lower():
                continue

            # 🔥 imagem da listagem (funciona na nuvem)
            img_tag = art.find("img")

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

            posts.append({
                "titulo": titulo,
                "link": link,
                "imagem": imagem
            })

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
