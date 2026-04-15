import asyncio
import os
import time
from playwright.async_api import async_playwright
import logging

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Configurações Globais
ENJOEI_COOKIE = os.getenv("ENJOEI_COOKIE")
LOJA_URL = "https://www.enjoei.com.br/@ericshop"
INTERVALO_ENTRE_CICLOS = 600  # 10 minutos
MAX_EXECUTION_TIME = 5 * 3600  # 5 horas (limite de segurança para o GitHub Actions)

async def megafonar_ciclo(page):
    """Executa um ciclo único de megafonar."""
    try:
        logging.info(f"🔗 Acessando a loja: {LOJA_URL}")
        # Aumentamos o timeout e usamos 'domcontentloaded' para ser mais rápido e resiliente
        await page.goto(LOJA_URL, wait_until="domcontentloaded", timeout=90000)
        await asyncio.sleep(10) # Espera o JS carregar os botões

        # Verificar se o robô está logado
        entrar_btn = page.locator('a:has-text("entrar"), button:has-text("entrar")').first
        if await entrar_btn.is_visible(timeout=5000):
            logging.error("❌ ERRO: O robô NÃO está logado. Verifique o ENJOEI_COOKIE.")
            return "AUTH_ERROR"

        # Rolagem para carregar produtos
        logging.info("⏳ Rolando página para carregar produtos...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(3)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(2)
        
        # Localizar botões de megafonar
        # Seletor mais genérico para capturar qualquer botão de megafonar
        buttons = page.locator('button').filter(has_text="megafonar")
        count = await buttons.count()
        logging.info(f"✅ Encontrados {count} botões de megafonar.")

        clicked = 0
        for i in range(count):
            try:
                btn = buttons.nth(i)
                # Filtra botões que não são os de megafonar o produto (ex: modais)
                btn_text = await btn.inner_text()
                if "agora" in btn_text.lower() or "impulsionar" in btn_text.lower():
                    continue

                if await btn.is_visible(timeout=2000):
                    await btn.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    await btn.click(timeout=5000)
                    clicked += 1
                    logging.info(f"   → [{clicked}] Produto megafonado com sucesso!")
                    await asyncio.sleep(5) # Pausa maior entre cliques para evitar bloqueio
            except Exception as e:
                logging.warning(f"   ⚠️ Falha ao clicar no botão {i}: {e}")
                continue
        
        if clicked == 0:
            logging.info("ℹ️ Nenhum produto disponível para megafonar neste ciclo.")
        else:
            logging.info(f"🎉 Ciclo concluído: {clicked} produtos megafonados.")
        
        return "SUCCESS"

    except Exception as e:
        logging.error(f"❌ Erro inesperado no ciclo: {e}")
        return "CYCLE_ERROR"

async def main():
    if not ENJOEI_COOKIE:
        logging.error("❌ ERRO CRÍTICO: ENJOEI_COOKIE não encontrado nos Secrets do GitHub.")
        return

    start_time = time.time()
    logging.info("🚀 MODO IMORTAL INICIADO: O robô tentará rodar por até 5 horas.")

    while (time.time() - start_time) < MAX_EXECUTION_TIME:
        ciclo_inicio = time.time()
        
        # Iniciamos o navegador dentro do loop para renovar a sessão se necessário
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
                
                # Configura o Cookie
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
                
                # Executa o ciclo de megafonar
                resultado = await megafonar_ciclo(page)
                
                if resultado == "AUTH_ERROR":
                    logging.error("🚨 Parando execução devido a erro de autenticação.")
                    await browser.close()
                    break # Para o loop se o cookie estiver errado

                await browser.close()
                
            except Exception as e:
                logging.error(f"🚨 Falha no navegador/contexto: {e}")
                # Não dá break, tenta novamente no próximo ciclo

        # Cálculo de espera para o próximo ciclo (exatamente 10 minutos)
        tempo_decorrido = time.time() - ciclo_inicio
        espera = max(30, INTERVALO_ENTRE_CICLOS - tempo_decorrido)
        
        proxima_rodada = time.strftime('%H:%M:%S', time.localtime(time.time() + espera))
        logging.info(f"😴 Ciclo finalizado. Aguardando {int(espera)}s. Próxima rodada às: {proxima_rodada}")
        await asyncio.sleep(espera)

    logging.info("⏰ Fim do tempo de vida da execução (5h). O GitHub iniciará uma nova em breve.")

if __name__ == "__main__":
    asyncio.run(main())
