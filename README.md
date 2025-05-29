# Teste Técnico - Análise de Dados: Vendas e Marketing

## Visão Geral

Este repositório contém um teste técnico para avaliação de candidatos à vaga de Analista de Dados. O objetivo é verificar habilidades de manipulação de dados, criação e execução de consultas SQL, análise exploratória e interpretação dos resultados, utilizando uma base de dados multimodal de vendas e marketing.

## Banco de Dados

No repositório pode ser encontrado o arquivo `vendas_marketing.db` já populado com dados randômicos gerados conforme o formato do teste.

A base de dados foi construída em **SQLite**. e possui 5 tabelas inter-relacionadas:

- **Clientes**: Informações sobre os clientes, como nome, segmento (B2B ou B2C) e cidade.
- **Campanhas_Marketing**: Informações sobre as campanhas de marketing realizadas.
- **Interacoes_Marketing**: Registros de interações dos clientes com as campanhas.
- **Produtos**: Dados dos produtos disponíveis para venda.
- **Vendas**: Registros de transações de vendas.

## Tarefas do Teste Técnico

O candidato deverá desenvolver análises a partir desta base, abordando os seguintes pontos:

### A. Análise de Vendas

1. **Total de Vendas por Canal:**  
   Calcule o valor total de vendas por canal de aquisição (Outbound vs Inbound) em um período específico (por exemplo, no último trimestre).

2. **Top Produtos:**  
   Identifique os 5 produtos com maior volume de vendas e calcule a margem de lucro média para esses produtos.

3. **Segmentação de Clientes:**  
   Compare o ticket médio entre os clientes dos segmentos B2B e B2C.

4. **Sazonalidade:**  
   Analise o padrão de vendas ao longo do ano, identificando picos e quedas, e proponha possíveis explicações baseadas no comportamento de compra.

### B. Análise de Marketing

5. **Eficiência das Campanhas:**  
   Determine quais campanhas tiveram maior taxa de conversão, relacionando o número de interações do tipo "Conversão" com o orçamento e custo das campanhas.

6. **Canais de Marketing:**  
   Analise qual canal de marketing (Email, Google Ads, Meta Ads, etc.) gera maior engajamento dos clientes, baseado nas interações registradas.

### C. Análise Integrada (Vendas e Marketing)

7. **Relação Temporal:**  
   Investigue se há um aumento nas vendas de determinados produtos logo após o início de uma campanha de marketing.

8. **Análise Regional:**  
    Explore se determinadas cidades apresentam melhor resposta às campanhas de marketing e como isso se reflete nas vendas.

### D. Agora é com você!

Esta seção é fundamental e faz parte dos critérios de avaliação do teste. Esperamos que você:

- **Proponha análises adicionais:**
Vá além dos pontos solicitados nas seções A, B e C. Sugira outras análises que possam trazer insights valiosos para o negócio, como análises de performance por período, comportamento do cliente, análise de churn ou outras métricas relevantes.

- **Entregue visualizações de dados:**
Apresente suas análises de forma visual, criando gráficos, dashboards ou outras formas de visualização que facilitem a comunicação dos resultados para o stakeholder. Essas visualizações devem evidenciar os insights obtidos e tornar o relatório mais intuitivo e atrativo.


## Abordagem e Ferramentas

Você tem total liberdade para resolver o teste utilizando **SQL** ou **Python** (ou uma combinação de ambos). Algumas sugestões:
- **SQL:** Utilize consultas diretas no banco de dados SQLite para extrair, agrupar e sumarizar os dados.
- **Python:** Utilize bibliotecas como `sqlite3`, `pandas`, `matplotlib` ou `seaborn` para realizar a análise e visualizações dos dados.

## Acesso ao Banco de Dados

O arquivo do banco de dados (`vendas_marketing.db`) será fornecido juntamente com este teste. Você pode utilizar ferramentas de visualização ou scripts Python para conectar e consultar a base de dados.

## Entrega e Considerações Finais

- Documente todas as suas consultas, análises e insights obtidos.
- Apresente um relatório e/ou uma apresentação com suas conclusões, incluindo as visualizações que facilitarão o entendimento dos resultados pelo stakeholder.
- Lembre-se: análises que vão além dos pontos solicitados serão **bastante** valorizadas e podem render pontos adicionais.

Ao finalizar o teste, envie um e-mail para [petro.cardoso@growthmachine.com.br](mailto:petro.cardoso@growthmachine.com.br?cc=leonardo.alexandre@growthmachine.com.br&subject=Teste%20T%C3%A9cnico%20-%20An%C3%A1lise%20de%20Dados%3A%20Vendas%20e%20Marketing) com cópia para [leonardo.alexandre@growthmachine.com.br](mailto:petro.cardoso@growthmachine.com.br?cc=leonardo.alexandre@growthmachine.com.br&subject=Teste%20T%C3%A9cnico%20-%20An%C3%A1lise%20de%20Dados%3A%20Vendas%20e%20Marketing) contendo o link do seu repositório no GitHub contendo a solução do teste.

> Obs.: Caso você tenha alguma dúvida sobre o teste, entre em contato conosco pelos mesmos e-mails acima.

Boa sorte e esperamos ver uma solução criativa, analítica e visualmente atraente!
