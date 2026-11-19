# Capturas do dashboard

Capturas reais do painel local com o logo na navbar, geradas com Playwright e Chromium em 18/11/2026. Todas usam o recorte padrão: 853 municípios, risco até 20%, todas as classes de solo e grupos de cultivar, decêndios 28–36.

| Arquivo | Conteúdo | Viewport em pixels CSS | PNG em pixels |
| --- | --- | --- | --- |
| [desktop.png](desktop.png) | Tela inicial com filtros laterais e cobertura do calendário | 1440 × 1000 | 1440 × 1000 |
| [desktop-completo.png](desktop-completo.png) | Conteúdo completo, incluindo os três gráficos e as fontes | 1440 × 2249 | 1440 × 2249 |
| [mobile.png](mobile.png) | Tela inicial com filtros no conteúdo | 390 × 844 | 1170 × 2532 |
| [mobile-resultados.png](mobile-resultados.png) | Tela rolada até os indicadores e o início do gráfico de cobertura | 390 × 844 | 1170 × 2532 |
| [mobile-completo.png](mobile-completo.png) | Conteúdo completo com os gráficos empilhados | 390 × 4133 | 1170 × 12399 |

O mobile usa emulação de largura, toque e escala de pixels no Chromium (DPR 3). Estas imagens não constituem teste em aparelho físico ou no Safari.

Para as versões completas, a altura do viewport foi ampliada mantendo a largura, pois o Streamlit usa rolagem interna. A interface, os dados e o CSS da aplicação foram preservados.

As verificações no navegador confirmaram o logo carregado e visível na navbar e o menu dentro da tela em todas as capturas, filtros laterais no desktop, filtros no conteúdo e gráficos empilhados no mobile, ausência de rolagem horizontal, preservação da seleção ao redimensionar, limpeza da seleção e abertura/fechamento do menu por clique e toque. Não houve erros de JavaScript na página.

[validacao.json](validacao.json) registra a versão do navegador e do Playwright, o commit base, as dimensões, os filtros e os hashes SHA-256 das imagens e dos arquivos de origem. No momento das capturas, a integração do logo era uma alteração local: `source_worktree_dirty` registra esse estado, e `source_files` identifica os arquivos usados nas capturas.
