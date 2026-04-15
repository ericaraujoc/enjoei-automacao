import asyncio
import os
from playwright.async_api import async_playwright
import logging

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configurações Globais
ENJOEI_COOKIE = os.getenv("ENJOEI_COOKIE")
LOJA_URL = "https://www.enjoei.com.br/@ericshop"

async def main():
    if not ENJOEI_COOKIE:
        logging.error("❌ ENJOEI_COOKIE não encontrado.")
        return

    logging.info("🚀 Iniciando ciclo de megafonar (Modo Econômico)")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            
            # Adiciona Cookie
            await context.add_cookies([{
                'name': '_website_session_7',
                'value': ENJOEI_COOKIE,
                'domain': 'www.enjoei.com.br',
                'path': '/',
                'httpOnly': True,
                'secure': True,
                'sameSite': 'Lax'
            }])
            
            page = await context.new_page()
            
            # Acessa a loja
            logging.info(f"🔗 Acessando a loja: {LOJA_URL}")
            await page.goto(LOJA_URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)

            # Verifica Login
            entrar_btn = page.locator('a:has-text("entrar"), button:has-text("entrar")').first
            if await entrar_btn.is_visible(timeout=5000):
                logging.error("❌ ERRO: O robô NÃO está logado. Atualize o ENJOEI_COOKIE.")
                await browser.close()
                return

            # Rolagem rápida
            await page.evaluate("window.scrollTo(0, 500)")
            await asyncio.sleep(2)
            
            # Localiza botões
            buttons = page.locator('button').filter(has_text="megafonar")
            count = await buttons.count()
            logging.info(f"✅ Encontrados {count} botões.")

            clicked = 0
            for i in range(count):
                try:
                    btn = buttons.nth(i)
                    btn_text = await btn.inner_text()
                    if "agora" in btn_text.lower(): continue
                    
                    await btn.scroll_into_view_if_needed()
                    await btn.click(timeout=5000)
                    clicked += 1
                    logging.info(f"   → [{clicked}] Megafonado!")
                    await asyncio.sleep(2) # Pausa mínima para não ser bloqueado
                except:
                    continue
            
            logging.info(f"🎉 Ciclo finalizado com {clicked} megafonadas.")
            await browser.close()

        except Exception as e:
            logging.error(f"🚨 Falha na execução: {e}")

if __name__ == "__main__":
    asyncio.run(main())
