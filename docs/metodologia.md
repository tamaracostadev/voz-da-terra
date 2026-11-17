# Metodologia, rastreabilidade e cuidado com os dados

## 1. Origem e disponibilidade

Fonte: **Ministério da Agricultura e Pecuária (MAPA)**, tábua de risco ZARC para a **safra 2026/2027**. Links para CSV e dicionário no [README](../README.md). Os números desta documentação são referentes ao **arquivo específico auditado**, identificado por SHA-256 no relatório, e podem mudar se a fonte publicar revisão.

O arquivo tem 1.189.856 linhas, 55 colunas, 22 culturas e 27 unidades federativas. Há 5.573 geocódigos diferentes, mas 10 linhas de Girassol/RS se referem aos códigos `4300001` e `4300002` sem nome de município; o ETL contabiliza essas dez linhas como localização inválida e não as usa em agregações municipais. Restam **5.571 geocódigos com município identificado**.

**Granularidade original:** linha de combinação de cultura, safra, município identificado por geocódigo, grupo de ciclo/cultivar, classe de solo, manejo, portaria e 36 decêndios do calendário. **Não** se trata de observações por fazenda/propriedade ou de um registro meteorológico diário. A resolução territorial é **municipal**, nunca bairro ou coordenada da lavoura.

## 2. Seleção do recorte

Recorte escolhido: `Nome_cultura == "Feijão"`, `UF == "MG"`, `Nome_Outros_Manejos == "Sequeiro"`. A combinação possui **8.025 linhas, 853 municípios**, classes de solo `11–16` (AD1–AD6) e grupos `20` (I), `21` (II). A portaria é `Port.13_de_16-03-2026`. Os decêndios com alguma indicação de até 40% são **28 a 36** (outubro a dezembro). A escolha foi feita após avaliar cobertura real no arquivo, não pelo município de residência de integrantes do grupo.

## 3. Tratamento e indicadores

**Classes AD:** a classificação do MAPA considera a *água disponível no solo*, em milímetros de água por centímetro de solo. AD1 indica a faixa mais baixa (de 0,34 até menos de 0,46 mm/cm), enquanto AD6 indica valores a partir de 1,40 mm/cm. As faixas intermediárias são apresentadas no painel. Elas não representam uma escala de qualidade geral ou análise individual da propriedade. Fonte: [MAPA — classificação de solos por água disponível](https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/programa-nacional-de-zoneamento-agricola-de-risco-climatico/classificacao-de-solo).

**Janela do painel:** o intervalo selecionável é derivado dos decêndios com alguma indicação no recorte, atualmente 28–36. Os decêndios 1–27 não foram removidos da base bruta nem da base curada: os respectivos códigos não contêm indicação de plantio nesta combinação de cultura, UF e manejo.

O ETL faz leitura em blocos (`chunksize=50_000`), conserva geocódigos como strings, valida a safra, valida códigos de decêndio `{0, 20, 30, 40}` e descarta linhas com município vazio ou geocódigo fora do padrão de sete dígitos.

Para dado limite `R ∈ {20, 30, 40}`, um decêndio é considerado **indicado** se o código original for um dos valores em `{20, 30, 40}` **menores ou iguais a R**. Código `0` não é uma indicação. Para a contagem por município e decêndio, utilizamos `any()` sobre as combinações de solo/ciclo do município; ou seja, **cada município conta no máximo uma vez por decêndio**. A contagem geral de municípios com indicação usa `any()` sobre os 36 decêndios. Essa união é útil para cobertura territorial, mas **não determina aptidão para qualquer propriedade daquele município**.

Resultados para todo o recorte: 663 municípios com algum decêndio até 20%; 774 até 30%; 853 até 40%. No decêndio 31, 850 municípios têm alguma indicação até 40%. **Não somar os três totais**, pois representam conjuntos aninhados, não populações distintas.

## 4. Estatística descritiva e hipótese exploratória

As análises com **Pandas, NumPy e Matplotlib** incluem comparações entre limites de risco, série dos decêndios com recomendação, classes de solo e ranking de municípios. A hipótese exploratória fixa o **grupo de cultivar I (`Cod_Ciclo=20`)** e risco até 20%, comparando **AD1 (`Cod_Solo=11`)** com **AD3 (`Cod_Solo=13`)** para os **mesmos municípios** com os dois perfis de solo presentes.

- **H0:** média da diferença pareada na quantidade de decêndios indicados (AD3 − AD1) igual a zero, sob troca aleatória de sinais.
- **Amostra analítica:** 363 municípios pareados; não é uma amostra probabilística da agricultura brasileira.
- **Resultado observado:** média **+3,198 decêndios** para AD3 versus AD1; mediana **+3**.
- **Procedimento:** teste exploratório bilateral de permutação de sinais, **2.000 permutações**, semente fixa `2026`, com correção `(extremos+1)/(permutações+1)`.
- **p-valor exploratório:** `0,0005` (precisão limitada pelas 2.000 permutações).

**Interpretação honesta:** o resultado evidencia uma diferença estruturada nas indicações registradas entre classes de solo *neste recorte e configuração*. Não demonstra efeito causal do solo, não mede perdas evitadas, não garante que AD3 seja “melhor” em uma propriedade e não deve ser generalizado para outros grupos/culturas sem refazer a análise.

## 5. Fontes de viés e proteção de dados

- **Viés de cobertura:** o arquivo contém portarias e combinações técnicas, não todas as lavouras existentes ou dados de adesão ao ZARC.
- **Viés de agregação:** sumarizar um município pode ocultar diferenças entre solo, grupo de ciclo e propriedades rurais.
- **Viés de acesso:** pequenos produtores podem ter conexão, smartphone ou alfabetização digital limitados; mensagens de voz só seriam testadas em versão futura.
- **Privacidade:** o MVP usa somente dados públicos agregados, não solicita CPF, telefone, localização da propriedade nem informações pessoais. Um produto futuro de mensagens exigiria base legal, consentimento/alternativa apropriada e políticas de retenção e exclusão.
- **Atualização:** a análise é um retrato do arquivo auditado. Revisões normativas e novas safras requerem nova ingestão e validação agronômica.

## 6. Reprodutibilidade e evidências

- `reports/auditoria.json` registra fonte, SHA-256 e contagens verificáveis.
- `reports/analise.json` guarda métricas, hipótese e resultados reproduzíveis.
- `reports/figuras/*.png` contém três gráficos estáticos derivados do CSV.
- `tests/test_metrics.py` usa dados artificiais apenas para testar lógica, nunca para apresentar resultados do projeto.
- O dashboard permite refazer visualmente as contagens com filtros, com download dos registros selecionados.
