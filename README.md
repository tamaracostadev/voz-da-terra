# 🌱 Voz da Terra

**Global Solution — FIAP | Protótipo acadêmico com dados reais e rastreáveis**

O Voz da Terra transforma dados públicos do **Zoneamento Agrícola de Risco Climático (ZARC)** em visualizações compreensíveis para apoiar a consulta de **janelas indicadas de plantio**. O público pretendido inclui pequenos produtores rurais, agentes de extensão e organizações de apoio à agricultura familiar.

## Recorte definido pela auditoria dos dados

**Feijão · Minas Gerais · Sequeiro · Safra 2026/2027**. Não partimos de um município escolhido por conveniência: analisamos o arquivo nacional e escolhemos um recorte com cobertura municipal ampla, campos coerentes e combinações de solo e grupo de cultivar disponíveis.

| Indicador verificado | Resultado |
| --- | ---: |
| Registros no CSV nacional | 1.189.856 |
| Culturas / UFs no arquivo | 22 / 27 |
| Municípios identificados por nome e geocódigo no arquivo | 5.571 |
| Registros de Feijão/MG/Sequeiro | 8.025 |
| Municípios distintos do recorte | 853 |
| Classes de solo e grupos de cultivar presentes | 6 / 2 |
| Decêndios com alguma indicação (risco até 40%) | 28–36 |
| Municípios com pelo menos um período indicado até 20% / 30% / 40% | 663 / 774 / 853 |
| Pico de cobertura até 40% | Decêndio 31: 850 municípios |

Esses totais são calculados pelo código, registrados em [`reports/auditoria.json`](reports/auditoria.json) e [`reports/analise.json`](reports/analise.json), e **não** equivalem a número de produtores, área cultivada ou municípios integralmente aptos. Uma indicação municipal significa que há **ao menos uma combinação de solo e grupo de cultivar** indicada; um produtor precisa verificar sua combinação específica e a portaria vigente.

### Fontes oficiais

- [MAPA — Tábua de risco ZARC, safra 2026/2027 (CSV)](https://dados.agricultura.gov.br/dataset/6d3d141c-885e-41a4-ab7f-dc8ff323b96f/resource/139e5a60-1f43-4cc8-aeab-a35dbbf816c0/download/dados-abertos-tabua-de-risco-safra-2026-2027.csv)
- [MAPA — Dicionário de dados da tábua de risco (PDF)](https://dados.agricultura.gov.br/dataset/6d3d141c-885e-41a4-ab7f-dc8ff323b96f/resource/bebb0ebb-bc75-460c-b900-a7a1ebd87bee/download/dicionario-de-dados-tabua-de-risco-2026.pdf)
- Portaria registrada nos dados do recorte: `Port.13_de_16-03-2026`.
- SHA-256 do CSV nacional auditado: `87d50518bb0746acc32fe6160ded322a01221fe7749d4900cb01d7f7a0ea7543`.

O CSV nacional ocupa aproximadamente 249 MiB e **não** está no repositório. Incluímos a base **curada e compactada** de Feijão/MG/Sequeiro em `data/processed/zarc_feijao_mg_sequeiro.csv.gz`, suficiente para abrir o dashboard imediatamente. O arquivo `cobertura_cultura_uf.csv` documenta a análise comparativa de cobertura territorial por cultura/UF. A extração integral é reproduzível pelo script de ETL.

## Executar o painel Streamlit

Requer **Python 3.11+**.

```bash
git clone https://github.com/tamaracostadev/voz-da-terra.git
cd voz-da-terra
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
streamlit run dashboard/app.py
```

O painel contém **três tipos de gráfico** (linha, barras horizontais e mapa de calor), KPIs, três insights dinâmicos, download de CSV e filtros por município, classe de solo, grupo de cultivar, decêndio e limite de risco (20%/30%/40%).

### Layout em computador e celular

O mesmo endereço do Streamlit abre em navegadores de computador e celular. A partir de **1024 px**, os filtros ficam em uma **barra lateral** e os gráficos de ranking e solo aparecem lado a lado. Abaixo desse breakpoint, os filtros ficam **no topo do conteúdo**, e os gráficos são empilhados para aproveitar a largura da tela. As seleções são preservadas ao redimensionar a janela.

Municípios usam **seleção múltipla com busca**; sem seleção, a consulta considera todo o estado. O limite de risco aparece em opções de toque; solo e cultivar usam botões que podem ser selecionados/desmarcados.

**Limite importante:** este é um site responsivo, **não** um aplicativo Android/iOS nem um serviço offline. É preciso acesso à internet para consultar uma implantação remota. Ainda é necessário testar a usabilidade com pessoas e aparelhos reais; não temos validação de campo ou testes com produtores.

### Reproduzir a auditoria a partir do CSV original

1. Faça o download do CSV completo no link do MAPA acima, sem alterá-lo.
2. Execute, da raiz do repositório:

```bash
python -m voz_da_terra.pipeline --source /caminho/para/dados-abertos-tabua-de-risco-safra-2026-2027.csv
python -m voz_da_terra.analysis
python -m unittest discover -s tests -v
```

O ETL lê o CSV em **blocos**, valida campos e códigos de decêndio, exclui registros com município não identificado, seleciona o recorte e grava a base comprimida e os relatórios. A análise produz gráficos PNG em `reports/figuras/` e uma comparação exploratória por permutação. Não adicionamos os dados fictícios dos exemplos didáticos da disciplina.

## Organização

```text
dashboard/app.py                Aplicação interativa Streamlit + Plotly
dashboard/assets/              Logo e recursos visuais do painel
src/voz_da_terra/pipeline.py   Auditoria nacional e ETL em blocos (Pandas)
src/voz_da_terra/metrics.py    Indicadores e regras de agregação municipal
src/voz_da_terra/analysis.py   Estatística NumPy e gráficos Matplotlib
data/processed/               CSV curado compactado e tabela de cobertura
reports/                      Auditoria, resultados e figuras geradas
tests/                        Testes de agregação e filtros (dados artificiais)
docs/                         Orientações dos slides, pitch e metodologia
```

## O que foi desenvolvido e o que é visão futura

<table>
<tr><th>Implementado no MVP</th><th>Proposta para etapa posterior</th></tr>
<tr><td>Auditoria ZARC; ETL reproduzível; análise estatística; dashboard web com filtros e evidências.</td><td>Alertas por WhatsApp/SMS/áudio, previsão meteorológica em tempo quase real, personalização por produtor e recomendação em linguagem natural.</td></tr>
</table>

**O ZARC não é um serviço de previsão do tempo.** O protótipo **não** monitora geadas/chuvas em tempo real, **não** determina automaticamente se uma propriedade pode plantar e **não** comprova redução de perdas. Não há login nem coleta de dados pessoais no painel atual. Antes de qualquer uso operacional, é necessário validar portarias atualizadas, solo, ciclo, manejo, cultura, safra e interpretação agronômica.

## Entregáveis de apresentação

- [`docs/slides.md`](docs/slides.md): roteiro dos slides com textos, evidências e espaços para nomes/RMs.
- [`docs/pitch.md`](docs/pitch.md): roteiro de vídeo de até cinco minutos.
- [`docs/metodologia.md`](docs/metodologia.md): definições de indicadores, hipótese e limites da pesquisa.

**Pendente do grupo:** inserir nomes/RMs, capturar screenshots do Streamlit em execução, montar o PPT/PDF final usando o template FIAP, gravar e publicar o vídeo conforme o enunciado, revisar exigências e enviar tudo dentro do prazo da disciplina. **Código no GitHub não substitui a entrega no portal.**
