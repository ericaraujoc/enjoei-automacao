import asyncio
import os
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# No seu GitHub Secrets, você deve colocar o valor do cookie '_website_session_7'
ENJOEI_COOKIE = os.getenv("ENJOEI_COOKIE")
LOJA_URL = "https://www.enjoei.com.br/@ericshop"

async def main():
    if not ENJOEI_COOKIE:
        logging.error("❌ Cookie ENJOEI_COOKIE não encontrado nos Secrets.")
        return

    async with async_playwright() as p:
        # Lançar navegador
        browser = await p.chromium.launch(headless=True)
        # O User Agent deve ser moderno para evitar bloqueios
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        
        # Adicionar os cookies conforme a imagem do navegador
        cookies = [
            {
                'name': '_website_session_7',
                'value': ENJOEI_COOKIE,
                'domain': 'www.enjoei.com.br',
                'path': '/',
                'httpOnly': True,
                'secure': True,
                'sameSite': 'Lax'
            }
        ]
        
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        try:
            logging.info(f"🔗 Acessando a loja: {LOJA_URL}")
            # Aumentar o timeout para garantir o carregamento em conexões lentas do CI
            await page.goto(LOJA_URL, wait_until="networkidle", timeout=60000)
            
            # Verificar se estamos logados
            # O Enjoei costuma ter um link ou botão de 'entrar' quando deslogado
            # Vamos tentar identificar se o perfil do usuário está visível
            is_logged_in = False
            try:
                # Se não encontrar o link de 'entrar', assume que está logado
                entrar_btn = page.locator('a:has-text("entrar"), button:has-text("entrar")').first
                if await entrar_btn.is_visible(timeout=10000):
                    logging.warning("⚠️ O robô parece NÃO estar logado. Verifique se o valor de ENJOEI_COOKIE (visto como _website_session_7 no navegador) ainda é válido.")
                else:
                    logging.info("✅ Login confirmado via Cookie!")
                    is_logged_in = True
            except:
                logging.info("✅ Login confirmado (seletor 'entrar' não encontrado)!")
                is_logged_in = True

            # Rolagem para carregar todos os produtos
            logging.info("⏳ Rolando a página para carregar produtos...")
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 800)")
                await asyncio.sleep(2)
            
            # Localizar botões de megafonar
            # O seletor pode variar, vamos usar um seletor CSS que busque pelo texto 'megafonar'
            megafonar_selector = 'button:has-text("megafonar")'
            buttons = page.locator(megafonar_selector)
            count = await buttons.count()
            logging.info(f"✅ Encontrados {count} botões de megafonar.")

            clicked = 0
            for i in range(count):
                try:
                    btn = buttons.nth(i)
                    if await btn.is_enabled(timeout=2000):
                        # Verifica se o botão não é o de "megafonar agora" do modal promocional
                        btn_text = await btn.inner_text()
                        if "agora" in btn_text.lower():
                            continue
                            
                        await btn.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        await btn.click(timeout=5000)
                        clicked += 1
                        logging.info(f"   → [{clicked}] Produto megafonado com sucesso!")
                        # Pausa aleatória curta para parecer humano
                        await asyncio.sleep(3)
                except Exception as e:
                    logging.debug(f"   ℹ️ Botão {i} não pôde ser clicado (provavelmente invisível ou modal): {e}")
                    continue
            
            if clicked == 0:
                logging.info("ℹ️ Nenhum produto disponível para megafonar no momento.")
                # Tira um print para diagnóstico
                await page.screenshot(path="diagnostico.png")
                logging.info("📸 Print de diagnóstico salvo como 'diagnostico.png'.")
            else:
                logging.info(f"🎉 Ciclo finalizado: {clicked} produtos megafonados!")

        except Exception as e:
            logging.error(f"❌ Erro crítico no ciclo: {e}")
            await page.screenshot(path="erro_critico.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
