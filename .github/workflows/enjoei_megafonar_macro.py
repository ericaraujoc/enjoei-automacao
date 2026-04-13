import asyncio
import time
from playwright.async_api import async_playwright
import logging

logging.basicConfig(
    filename='enjoei_megafonar.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

INTERVALO_MINUTOS = 10   # ← Alterado para 20 minutos conforme solicitado

async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("✅ Conectado ao Opera GX!")
        except Exception as e:
            print("❌ Erro ao conectar no Opera GX.")
            print("   Abra o Opera GX com o comando --remote-debugging-port=9222")
            print(f"   Erro: {e}")
            return

        # Selecionar a aba do Enjoei
        page = None
        for context in browser.contexts:
            for pg in context.pages:
                url = pg.url.lower()
                title = (await pg.title()).lower()
                if "enjoei.com.br" in url or "enjoei" in title:
                    page = pg
                    print(f"✅ Aba do Enjoei selecionada: {await pg.title()}")
                    break
            if page:
                break

        if not page:
            print("❌ Não encontrou aba do Enjoei aberta.")
            print("   Abra o site no Opera GX e rode o script novamente.")
            return

        print(f"🔗 Usando aba: {await page.title()}")
        print(f"⏰ Intervalo configurado: {INTERVALO_MINUTOS} minutos\n")

        while True:
            try:
                print(f"\n🔄 Iniciando ciclo de Megafonar - {time.strftime('%H:%M:%S')}")

                # Rolagem para carregar produtos
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(4)
                await page.evaluate("window.scrollTo(0, 400)")
                await asyncio.sleep(2)

                # Clicar nos botões "megafonar" normais
                buttons = page.locator('button:has-text("megafonar")')
                count = await buttons.count()
                print(f"✅ Encontrados {count} botões megafonar")

                clicked = 0
                for i in range(count):
                    try:
                        btn = buttons.nth(i)
                        if await btn.is_visible(timeout=4000):
                            text = (await btn.inner_text()).strip().lower()
                            if "megafonar agora" in text:  
                                continue  # evita clicar no botão do modal
                            
                            await btn.scroll_into_view_if_needed()
                            await btn.click(timeout=10000)
                            print(f"   → Clicado: {text}")
                            logging.info(f"Clicado botão normal: {text}")
                            clicked += 1
                            await asyncio.sleep(1.8)
                    except:
                        continue

                # === TRATAMENTO SEGURO DO MODAL ===
                try:
                    if await page.locator('button:has-text("megafonar agora")').is_visible(timeout=7000):
                        print("📢 Modal 'megafonar agora' detectado! Fechando com X...")

                        closed = False
                        close_selectors = [
                            'button[aria-label="Close"]',
                            '.o-modal_close',
                            'button:has-text("×")',
                            'button:has-text("X")',
                            '[class*="close"]',
                        ]

                        for selector in close_selectors:
                            try:
                                close_btn = page.locator(selector).first
                                if await close_btn.is_visible(timeout=3000):
                                    await close_btn.click(timeout=8000)
                                    print("   → ✅ Modal fechado com sucesso (X)")
                                    logging.info("Modal fechado com X")
                                    closed = True
                                    break
                            except:
                                continue

                        if not closed:
                            # Último recurso: clica fora ou remove via JS
                            try:
                                await page.click('body', position={'x': 100, 'y': 100})
                                print("   → Tentativa de fechar clicando fora")
                            except:
                                await page.evaluate("""
                                    () => {
                                        const modals = document.querySelectorAll('[class*="modal"], [class*="Modal"]');
                                        modals.forEach(m => m.remove());
                                    }
                                """)
                                print("   → Modal removido via JavaScript")
                        await asyncio.sleep(3)
                except:
                    pass  # Nenhum modal apareceu

                print(f"✅ Ciclo finalizado ({clicked} cliques). Próxima rodada em {INTERVALO_MINUTOS} minutos...\n")
                logging.info(f"Ciclo OK - {clicked} cliques realizados")

                await asyncio.sleep(INTERVALO_MINUTOS * 60)

            except Exception as e:
                print(f"❌ Erro no ciclo: {e}")
                logging.error(f"Erro: {e}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    print("🚀 Macro Megafonar Opera GX - Intervalo de 20 minutos")
    print("   → Prioridade: clicar no X do modal (nunca em 'megafonar agora')")
    asyncio.run(main())
