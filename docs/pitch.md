# Roteiro de pitch — Voz da Terra (aprox. 4m20s)

Este texto serve como guia. O grupo deve adaptar vocabulário e pausas, testar a duração real e confirmar as regras de identificação de integrantes da disciplina. **Não mencionar que áudio/WhatsApp já estão integrados**: isso é visão futura.

## 0:00–0:35 — Problema (Pessoa 1)

“Olá! Nós somos a equipe do Voz da Terra, um projeto desenvolvido para a Global Solution da FIAP. O plantio agrícola envolve decisões que dependem da cultura, do solo, da época e do risco climático. No Brasil, existe informação pública para apoiar essas decisões, mas ela pode ser difícil de consultar quando está distribuída em tabelas técnicas. Nossa pergunta foi: como tornar esses dados mais acessíveis e úteis sem perder sua precisão?”

## 0:35–1:15 — Evidência e escolha do recorte (Pessoa 2)

“Começamos pelos dados, não pela interface. Auditamos o CSV público do Ministério da Agricultura sobre o ZARC para a safra de 2026 e 2027. Encontramos quase um milhão e duzentas mil linhas, 22 culturas e cobertura das 27 unidades federativas. Ao avaliar a granularidade e a disponibilidade reais, definimos o foco no feijão de sequeiro em Minas Gerais. Nesse recorte, temos 8.025 registros e 853 municípios identificados. É importante dizer que a informação é municipal e considera combinações de solo e grupo de cultivar, e não a situação exata de cada propriedade.”

## 1:15–2:10 — Solução e demo (Pessoa 3)

“O Voz da Terra transforma esse conjunto em um painel navegável. Usamos Python e Pandas para validar e preparar os dados, e Streamlit com Plotly para as visualizações. [MOSTRAR O DASHBOARD RODANDO.] Aqui podemos filtrar municípios, classe de solo, grupo de cultivar, decêndios e nível máximo de risco. A primeira visualização mostra as janelas ao longo do calendário. A segunda compara municípios pelo número de períodos indicados. E a terceira mostra como a cobertura varia por classe de solo. Os resultados são gerados a partir do arquivo oficial, e deixamos o link da fonte e seus metadados visíveis no painel.”

## 2:10–3:05 — Resultados e análise (Pessoa 1 ou 4)

“Nossa análise revelou diferenças importantes. Com limite de risco até 20%, encontramos 663 municípios com alguma combinação indicada; com limite até 40%, são 853. As indicações de plantio desse recorte aparecem entre os decêndios 28 e 36. Também realizamos uma análise exploratória, comparando duas classes de água disponível no solo nos mesmos municípios e em um grupo fixo de cultivar. O resultado mostrou diferença de aproximadamente 3,2 decêndios nas indicações. Isso não é uma promessa de ganho de produtividade: mostra como as regras do zoneamento podem variar com as características consideradas.”

## 3:05–3:45 — Impacto e responsabilidade (Pessoa 2)

“O impacto que queremos alcançar é ampliar o acesso à informação técnica confiável e incentivar decisões mais informadas, em apoio aos Objetivos de Desenvolvimento Sustentável 2 e 13. Para isso, também precisamos ser transparentes: o ZARC não é previsão meteorológica em tempo real; o painel não substitui orientação agronômica; e ainda não temos métricas de perdas evitadas ou usuários atendidos. O protótipo atual consulta apenas dados públicos e não coleta informações pessoais.”

## 3:45–4:20 — Futuro e encerramento (Pessoa 3)

“No futuro, queremos testar uma interface ainda mais inclusiva, com explicações por áudio e mensagens simples, em parceria com técnicos e produtores. Antes de implementar essa etapa, precisamos validar o entendimento das recomendações e cuidar da privacidade. O MVP que apresentamos já tem auditoria reproduzível, dashboard e análise estatística. Essa é a nossa proposta: fazer a informação chegar mais longe, com responsabilidade. Obrigado!”

**Observação para quem edita:** marque o momento de mostrar o dashboard real, inclua a identificação completa dos participantes conforme exigido pela FIAP e coloque a URL pública do vídeo na apresentação final. Não adicione testemunhos, números de impacto ou promessas de previsão que não foram medidos ou implementados.
