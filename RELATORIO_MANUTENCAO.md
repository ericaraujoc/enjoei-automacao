# Relatório de Manutenção e Diagnóstico: Automação Enjoei

Este documento fornece orientações sobre a validade da sessão e uma análise de possíveis erros que podem ocorrer durante a execução do robô de megafonar.

---

## 1. Validade da Sessão (Cookies)

A sessão do Enjoei através do cookie `_website_session_7` não é eterna, mas pode durar bastante tempo se cuidada corretamente.

| Fator | Descrição |
| :--- | :--- |
| **Duração Estimada** | Geralmente dura entre **7 a 30 dias**, dependendo da atividade. |
| **Expiração Manual** | Se você clicar em **"Sair" (Logout)** no seu navegador, o cookie no GitHub Actions parará de funcionar imediatamente. |
| **Troca de Senha** | Alterar a senha da conta invalida todas as sessões ativas, exigindo um novo cookie. |
| **Dica de Ouro** | Evite fazer logout manual. Se precisar usar outra conta, use uma **janela anônima** para não derrubar a sessão do robô. |

---

## 2. Relatório de Possíveis Erros e Soluções

Abaixo estão os erros mais comuns que podem interromper a sua automação e como resolvê-los:

### ❌ Erro: "O robô parece NÃO estar logado"
*   **Causa:** O cookie `ENJOEI_COOKIE` expirou ou foi invalidado por um logout.
*   **Solução:** Capturar o novo valor do cookie `_website_session_7` no navegador e atualizar o GitHub Secret.

### ❌ Erro: "Nenhum produto disponível para megafonar"
*   **Causa 1:** Todos os produtos já foram megafonados recentemente (existe um intervalo de tempo imposto pelo Enjoei).
*   **Causa 2:** Mudança no layout do site que impede o robô de encontrar os botões.
*   **Solução:** Verifique o arquivo `diagnostico.png` gerado nos artefatos do GitHub Actions para ver o que o robô está enxergando.

### ❌ Erro: "Timeout / Network Error"
*   **Causa:** O site do Enjoei demorou muito para carregar ou o GitHub Actions teve uma instabilidade de rede.
*   **Solução:** O script já possui um tempo de espera aumentado, mas se persistir, pode ser necessário reduzir a frequência de execução no arquivo `.yml`.

### ❌ Erro: "Cloudflare / Bot Detection"
*   **Causa:** O Enjoei detectou que o acesso está vindo de um servidor (Data Center) e bloqueou o acesso.
*   **Solução:** No código atual, usamos um **User Agent** moderno e pausas aleatórias. Se o bloqueio for frequente, pode ser necessário adicionar o cookie `_cfuvid` que aparece na sua imagem para reforçar a identidade.

---

## 3. Recomendações de Uso

1.  **Frequência:** Não execute o robô muitas vezes por hora. Uma execução a cada **2 ou 4 horas** é o ideal para evitar bloqueios por comportamento suspeito.
2.  **Monitoramento:** Uma vez por semana, dê uma olhada nos logs do GitHub Actions para garantir que o contador de "produtos megafonados" não está zerado constantemente.
3.  **Atualização:** Se o Enjoei mudar o design do site, os "seletores" (como o robô encontra o botão) podem precisar de ajuste.

---
*Relatório gerado em 13 de Abril de 2026.*
