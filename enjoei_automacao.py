import asyncio
import os
import logging
 
from playwright.async_api import async_playwright
 
# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
 
# Configurações Globais
ENJOEI_COOKIE = os.getenv("ENJOEI_COOKIE")
LOJA_URL = "https://www.enjoei.com.br/@ericshop"
 
CICLOS = 5               # Quantos ciclos por run (5 ciclos x 10min = ~50min)
INTERVALO_MINUTOS = 10   # Minutos entre cada ciclo
 
 
async def executar_megafonar():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
 
            # Adiciona Cookie de sessão
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
 
            # Verifica Login — procura elemento que só aparece quando logado
            try:
                logado = await page.locator('[data-testid="user-menu"], .user-avatar, .logout-btn').first.is_visible(timeout=5000)
            except Exception:
                logado = False
 
            # Fallback: se botão "entrar" estiver visível, não está logado
            if not logado:
                try:
                    entrar_visivel = await page.locator('a:has-text("entrar"), button:has-text("entrar")').first.is_visible(timeout=3000)
                    if entrar_visivel:
                        logging.error("❌ ERRO: Robô NÃO está logado. Atualize o ENJOEI_COOKIE.")
                        await browser.close()
                        return 0
                except Exception:
                    pass
 
            # Rolagem progressiva para carregar todos os produtos
            logging.info("📜 Rolando página para carregar produtos...")
            for _ in range(6):
                await page.evaluate("window.scrollBy(0, 800)")
                await asyncio.sleep(1)
 
            # Localiza botões de megafonar
            buttons = page.locator('button').filter(has_text="megafonar")
            count = await buttons.count()
            logging.info(f"✅ Encontrados {count} botões de megafonar.")
 
            clicked = 0
            for i in range(count):
                try:
                    btn = buttons.nth(i)
                    btn_text = await btn.inner_text()
 
                    # Pula botões que já foram megafonados recentemente
                    if "agora" in btn_text.lower():
                        logging.info(f"   → [{i+1}] Já megafonado recentemente, pulando.")
                        continue
 
                    await btn.scroll_into_view_if_needed()
                    await btn.click(timeout=5000)
                    clicked += 1
                    logging.info(f"   → [{clicked}] Megafonado com sucesso!")
                    await asyncio.sleep(2)  # Pausa para não ser bloqueado
 
                except Exception as e:
                    logging.warning(f"   → Erro no botão {i+1}: {e}")
                    continue
 
            logging.info(f"🎉 Ciclo finalizado: {clicked} megafonadas.")
            await browser.close()
            return clicked
 
        except Exception as e:
            logging.error(f"🚨 Falha na execução: {e}")
            return 0
 
 
async def main():
    if not ENJOEI_COOKIE:
        logging.error("❌ ENJOEI_COOKIE não encontrado nas variáveis de ambiente.")
        return
 
    logging.info(f"🚀 Iniciando automação — {CICLOS} ciclos de {INTERVALO_MINUTOS} minutos cada.")
    total_megafonadas = 0
 
    for ciclo in range(1, CICLOS + 1):
        logging.info(f"\n{'='*40}")
        logging.info(f"🔁 Ciclo {ciclo}/{CICLOS}")
        logging.info(f"{'='*40}")
 
        megafonadas = await executar_megafonar()
        total_megafonadas += megafonadas
 
        if ciclo < CICLOS:
            logging.info(f"⏳ Aguardando {INTERVALO_MINUTOS} minutos para o próximo ciclo...")
            await asyncio.sleep(INTERVALO_MINUTOS * 60)
 
    logging.info(f"\n🏁 Automação concluída! Total de megafonadas: {total_megafonadas}")
 
 
if __name__ == "__main__":
    asyncio.run(main())
