# Roteiro de pitch V2 — Voz da Terra (uma pessoa apresentando)

**Objetivo:** vídeo de até **5 minutos**, apresentado integralmente por **um(a) integrante** em nome do grupo, alinhado a `docs/slides_v2.md` e ao template oficial FIAP CitizenTech 2026.2.

**Duração planejada:** aproximadamente **4min30s a 4min45s**, com pausas curtas para mudar de tela. O tempo é uma estimativa: ensaiar e cronometrar antes de gravar. As instruções entre colchetes são **orientações de edição, não devem ser narradas**.

**Antes de gravar:** preencher `[SEU NOME]` e `[TURMA]`, confirmar que os nomes e RMs de **todos os integrantes** aparecem no slide de identificação e preparar uma captura **real** do painel funcionando. O roteiro usa **“nós”** para representar o trabalho do grupo, mesmo com uma só pessoa falando.

## 0:00–0:35 — Apresentação e problema

**Na tela:** slides 1–3, com nome do projeto e contextualização.

> Olá! Eu sou **[SEU NOME]**, da turma **[TURMA]**, e apresento o **Voz da Terra** em nome do nosso grupo da FIAP.
>
> Nosso desafio é facilitar o acesso a informações para planejar o plantio. O Ministério da Agricultura publica o Zoneamento Agrícola de Risco Climático, o **ZARC**, mas sua consulta exige cruzar município, solo, cultivar, período e risco em tabelas técnicas. Queremos tornar essa consulta mais clara, sem perder as condições oficiais.

## 0:35–1:15 — Evidências, território e público

**Na tela:** slides 3 e 5; destacar os números sem transformar a persona em entrevista fictícia.

> Auditamos a base oficial e escolhemos **feijão de sequeiro em Minas Gerais** na safra **2026/2027**. São **8.025 registros** em **853 municípios**, com seis classes de solo e dois grupos de cultivar.
>
> O Censo Agropecuário de 2017 apontou **441,8 mil estabelecimentos de agricultura familiar** no estado. A TIC Domicílios 2025 mostrou que **85% dos lares rurais brasileiros não tinham computador**; esse dado é nacional. Usamos essas pesquisas para construir uma persona de referência. **Não entrevistamos produtores.**

## 1:15–2:20 — Solução, tecnologia e demonstração

**Na tela:** slides 4, 8 e 9 rapidamente; depois **dashboard real** (slide 10 ou gravação do Streamlit).

> Construímos um painel web com **Streamlit e Plotly**. **Python e Pandas** tratam o CSV; **NumPy e Matplotlib** apoiam a análise.
>
> [ABRIR O PAINEL.] Para consultar, busco um município, escolho limite de risco, classe de solo, cultivar e decêndios. [MOSTRAR OS GRÁFICOS.] O painel exibe indicadores, uma linha ao longo do calendário, um ranking de municípios e um mapa de calor por solo. Um decêndio é um período de cerca de dez dias.
>
> Atenção: **a indicação para um município significa que existe alguma combinação de solo e cultivar naquele período**. Não garante aptidão para toda propriedade.

## 2:20–3:20 — Resultados e três insights

**Na tela:** slide 12 e, se possível, os gráficos de `reports/figuras/` ou o painel ao vivo.

> Três resultados chamaram nossa atenção.
>
> Primeiro, **663 municípios** têm alguma indicação até 20% de risco, **774** até 30% e **853** até 40%. Esses totais se sobrepõem.
>
> Segundo, as indicações do recorte vão dos **decêndios 28 a 36**, com pico no **31**: **850 municípios** até 40%.
>
> Terceiro, em uma comparação exploratória entre **363 municípios**, mantendo grupo de cultivar e risco fixos, **AD3 teve cerca de 3,2 decêndios indicados a mais que AD1**. É uma diferença do arquivo, **não efeito causal nem recomendação para uma fazenda**.

## 3:20–4:05 — Impacto, inclusão e responsabilidade

**Na tela:** slides 6, 7 e 11.

> Esperamos beneficiar **pequenos produtores, agricultores familiares e técnicos de extensão**. O MAPA fornece os dados oficiais; cooperativas e extensionistas são possíveis apoiadores futuros, sem parceria firmada.
>
> O benefício esperado é facilitar a consulta e a compreensão do ZARC. Em um piloto, mediríamos o tempo para encontrar a informação e quantas pessoas a interpretam corretamente. **Ainda não medimos perdas evitadas nem testamos com produtores.**
>
> A proposta se relaciona aos **ODS 2 e 13**. O painel não pede dados pessoais, mas ainda precisa ser avaliado quanto à acessibilidade e às barreiras de conexão.

## 4:05–4:40 — Limites, próximos passos e encerramento

**Na tela:** slides 9, 10 e 13; encerrar com o nome Voz da Terra e o endereço do repositório.

> Entregamos um protótipo funcional, com **pipeline reproduzível, análise de dados e painel**. O ZARC **não é previsão meteorológica em tempo real**, e a ferramenta não substitui orientação técnica.
>
> Nos próximos passos, queremos testar a interface com produtores e estudar explicações por áudio. **Áudio, WhatsApp e alertas automáticos ainda não fazem parte do MVP.**
>
> O **Voz da Terra** quer tornar dados públicos mais compreensíveis, com responsabilidade. Obrigado!

---

## Guia rápido para uma gravação individual

1. **Uma única voz do início ao fim:** não alternar “Pessoa 1/Pessoa 2”. Apresente-se uma vez e use “nosso grupo” ao falar do desenvolvimento.
2. **Mostrar o que existe:** prefira uma gravação real do Streamlit. Se usar uma captura estática, ela também precisa ser real e corresponder ao código. Não apresentar mockup como sistema rodando.
3. **Evitar pausas longas na demo:** deixe o dashboard aberto e os filtros preparados antes de começar a gravar. Fale enquanto aponta ou destaca cada visualização.
4. **Exibir as fontes em tela:** MAPA/ZARC para o recorte; Agência Minas/Censo 2017 e Cetic.br 2025 para o contexto da persona. O roteiro não precisa ler URLs longas em voz alta.
5. **Não extrapolar os dados:** os **853 municípios não são 853 produtores**; a diferença entre solos é exploratória; o ZARC não prevê chuva futura nem comprova redução de perdas.
6. **Checagem final:** revisar pronúncia de *ZARC*, *decêndio* e *AD3*, ensaiar com cronômetro, exportar vídeo de até cinco minutos, publicar no YouTube com acesso público e inserir o link no slide 13.

## Fontes e apoio à apresentação

- Base factual e requisitos: [`slides_v2.md`](slides_v2.md), [`metodologia.md`](metodologia.md), `reports/auditoria.json` e `reports/analise.json`.
- Dados oficiais: [MAPA/ZARC 2026/2027](https://dados.agricultura.gov.br/dataset/6d3d141c-885e-41a4-ab7f-dc8ff323b96f/resource/139e5a60-1f43-4cc8-aeab-a35dbbf816c0/download/dados-abertos-tabua-de-risco-safra-2026-2027.csv).
- Contexto da persona: [Agência Minas, Censo Agropecuário 2017](https://www.agenciaminas.mg.gov.br/noticia/minas-gerais-e-o-2-estado-brasileiro-com-mais-agricultores-familiares-114590) e [Cetic.br, TIC Domicílios 2025, indicador A1](https://cetic.br/pt/tics/domicilios/2025/domicilios/A1/).
- Entrega oficial: pitch **público no YouTube**, **até 5 minutos**, com link no slide final do template FIAP.
