import asyncio
import os
import logging
import time

from playwright.async_api import async_playwright

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================================================
# ⚙️  CONFIGURAÇÕES — edite aqui conforme necessário
# ============================================================
ENJOEI_COOKIE      = os.getenv("ENJOEI_COOKIE")
LOJA_URL           = "https://www.enjoei.com.br/@ericshop"
INTERVALO_MINUTOS  = 10      # ⏱ Minutos entre cada rodada de megafonar
DURACAO_TOTAL_MIN  = int(os.getenv("DURACAO_TOTAL_MIN", 355))  # ⏳ Injetado pelo job
# ============================================================


async def executar_megafonar():
    """Abre o browser, faz login via cookie e clica em todos os botões de megafonar disponíveis."""
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )

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

            logging.info(f"🔗 Acessando: {LOJA_URL}")
            await page.goto(LOJA_URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)

            # Verifica login
            try:
                logado = await page.locator('[data-testid="user-menu"], .user-avatar, .logout-btn').first.is_visible(timeout=5000)
            except Exception:
                logado = False

            if not logado:
                try:
                    entrar_visivel = await page.locator('a:has-text("entrar"), button:has-text("entrar")').first.is_visible(timeout=3000)
                    if entrar_visivel:
                        logging.error("❌ NÃO está logado. Atualize o ENJOEI_COOKIE.")
                        await browser.close()
                        return 0
                except Exception:
                    pass

            # Rolagem progressiva para carregar todos os produtos
            logging.info("📜 Carregando produtos...")
            for _ in range(6):
                await page.evaluate("window.scrollBy(0, 800)")
                await asyncio.sleep(1)

            # Clica em todos os botões disponíveis
            buttons = page.locator('button').filter(has_text="megafonar")
            count = await buttons.count()
            logging.info(f"🔎 {count} botões encontrados.")

            clicked = 0
            for i in range(count):
                try:
                    btn = buttons.nth(i)
                    btn_text = await btn.inner_text()

                    if "agora" in btn_text.lower():
                        continue  # Ainda em cooldown, pula

                    await btn.scroll_into_view_if_needed()
                    await btn.click(timeout=5000)
                    clicked += 1
                    logging.info(f"   ✅ [{clicked}] Megafonado!")
                    await asyncio.sleep(2)

                except Exception as e:
                    logging.warning(f"   ⚠️ Erro no botão {i+1}: {e}")
                    continue

            logging.info(f"🎉 Rodada finalizada: {clicked} megafonadas.")
            await browser.close()
            return clicked

        except Exception as e:
            logging.error(f"🚨 Falha: {e}")
            return 0


async def main():
    if not ENJOEI_COOKIE:
        logging.error("❌ ENJOEI_COOKIE não encontrado.")
        return

    inicio = time.time()
    limite_segundos = DURACAO_TOTAL_MIN * 60
    total = 0
    rodada = 0

    logging.info(f"🚀 Iniciando — rodadas a cada {INTERVALO_MINUTOS} min por {DURACAO_TOTAL_MIN} min.")

    while True:
        tempo_decorrido = time.time() - inicio

        if tempo_decorrido >= limite_segundos:
            logging.info("⏹ Tempo limite atingido. Encerrando.")
            break

        rodada += 1
        logging.info(f"\n{'='*40}\n🔁 Rodada {rodada}\n{'='*40}")

        megafonadas = await executar_megafonar()
        total += megafonadas

        tempo_restante = limite_segundos - (time.time() - inicio)

        if tempo_restante <= 60:
            logging.info("⏹ Menos de 1 min restante. Encerrando.")
            break

        espera = min(INTERVALO_MINUTOS * 60, tempo_restante - 60)
        logging.info(f"⏳ Próxima rodada em {int(espera/60)}min {int(espera%60)}s...")
        await asyncio.sleep(espera)

    logging.info(f"\n🏁 Total de megafonadas na sessão: {total}")


if __name__ == "__main__":
    asyncio.run(main())
