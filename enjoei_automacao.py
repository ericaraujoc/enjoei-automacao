import asyncio
import os
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ENJOEI_COOKIE = os.getenv("ENJOEI_COOKIE")
LOJA_URL = "https://www.enjoei.com.br/@ericshop"

async def main( ):
    if not ENJOEI_COOKIE:
        logging.error("❌ Cookie ENJOEI_COOKIE não encontrado nos Secrets.")
        return

    async with async_playwright() as p:
        # Lançar navegador
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        
        # Adicionar o cookie de sessão
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
            logging.info(f"🔗 Acessando a loja: {LOJA_URL}")
            await page.goto(LOJA_URL, wait_until="networkidle")
            
            # Verificar se estamos logados (procurar por algo que só aparece logado, como o menu do usuário)
            # Ou simplesmente verificar se o botão 'entrar' ainda existe
            entrar_btn = page.locator('a:has-text("entrar")')
            if await entrar_btn.is_visible(timeout=5000):
                logging.warning("⚠️ O robô parece NÃO estar logado. Verifique se o ENJOEI_COOKIE ainda é válido.")
            else:
                logging.info("✅ Login confirmado via Cookie!")

            # Rolagem para carregar todos os produtos
            logging.info("⏳ Rolando a página para carregar produtos...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(4)
            await page.evaluate("window.scrollTo(0, 500)")
            await asyncio.sleep(2)

            # Localizar botões de megafonar
            # O Enjoei às vezes usa classes diferentes, vamos tentar pelo texto de forma mais abrangente
            buttons = page.locator('button:has-text("megafonar")')
            count = await buttons.count()
            logging.info(f"✅ Encontrados {count} botões de megafonar.")

            clicked = 0
            for i in range(count):
                try:
                    btn = buttons.nth(i)
                    if await btn.is_visible(timeout=2000):
                        text = (await btn.inner_text()).lower()
                        # Evitar clicar no botão do modal de anúncio
                        if "agora" in text or "impulsionar" in text:
                            continue
                        
                        await btn.scroll_into_view_if_needed()
                        await btn.click(timeout=5000)
                        clicked += 1
                        logging.info(f"   → [{clicked}] Produto megafonado com sucesso!")
                        await asyncio.sleep(2) # Pausa entre cliques para evitar bloqueio
                except Exception as e:
                    logging.error(f"   ❌ Erro ao clicar no botão {i}: {e}")
                    continue
            
            if clicked == 0:
                logging.info("ℹ️ Nenhum produto disponível para megafonar no momento.")
                # Tira um print para diagnóstico se não clicar em nada
                await page.screenshot(path="diagnostico.png")
                logging.info("📸 Print de diagnóstico salvo como 'diagnostico.png' (veja nos artefatos do Action).")
            else:
                logging.info(f"🎉 Ciclo finalizado: {clicked} produtos megafonados!")

        except Exception as e:
            logging.error(f"❌ Erro crítico no ciclo: {e}")
            await page.screenshot(path="erro_critico.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
