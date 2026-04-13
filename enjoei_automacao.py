import asyncio
import os
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ENJOEI_COOKIE = os.getenv("ENJOEI_COOKIE")

async def main():
    if not ENJOEI_COOKIE:
        logging.error("❌ Cookie ENJOEI_COOKIE não encontrado nos Secrets.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies([{
            'name': '_enjoei_session',
            'value': ENJOEI_COOKIE,
            'domain': '.enjoei.com.br',
            'path': '/',
            'httpOnly': True,
            'secure': True,
            'sameSite': 'Lax'
        }] )
        
        page = await context.new_page()
        try:
            logging.info("🔗 Acessando Enjoei...")
            # Tenta acessar a página de anúncios do usuário
            await page.goto("https://www.enjoei.com.br/minha-loja", wait_until="networkidle" )
            
            # Rolagem para carregar botões
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)

            buttons = page.locator('button:has-text("megafonar")')
            count = await buttons.count()
            logging.info(f"✅ Encontrados {count} botões.")

            clicked = 0
            for i in range(count):
                btn = buttons.nth(i)
                if "megafonar agora" not in (await btn.inner_text()).lower():
                    await btn.click()
                    clicked += 1
                    await asyncio.sleep(1.5)
            
            logging.info(f"✅ Ciclo finalizado: {clicked} produtos megafonados.")
        except Exception as e:
            logging.error(f"❌ Erro: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
