# Teste Técnico - Análise de Dados: Vendas e Marketing

## Visão Geral

Este repositório contém uma aplicação web interativa desenvolvida com Streamlit para análise de dados de vendas e marketing. A aplicação permite visualizar e analisar dados de forma dinâmica, com gráficos interativos e insights detalhados.

## Tecnologias Utilizadas

- **Python 3.x**
- **Streamlit**: Para criação da interface web interativa
- **Pandas**: Para manipulação e análise de dados
- **Plotly**: Para criação de gráficos interativos
- **SQLite**: Banco de dados

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install streamlit pandas plotly
```

## Banco de Dados

A aplicação utiliza um banco de dados SQLite (`vendas_marketing.db`) com 5 tabelas inter-relacionadas:

- **Clientes**: Informações sobre os clientes, como nome, segmento (B2B ou B2C) e cidade.
- **Campanhas_Marketing**: Informações sobre as campanhas de marketing realizadas.
- **Interacoes_Marketing**: Registros de interações dos clientes com as campanhas.
- **Produtos**: Dados dos produtos disponíveis para venda.
- **Vendas**: Registros de transações de vendas.

## Funcionalidades

A aplicação está dividida em 5 seções principais:

### 1. Visão Geral
- Dashboard com métricas principais
- Preview das tabelas do banco de dados
- Visão rápida dos principais indicadores

### 2. Análise de Vendas
- Total de vendas por canal de aquisição
- Top 5 produtos mais vendidos
- Segmentação de clientes (B2B vs B2C)
- Análise de sazonalidade
- Insights e recomendações específicas

### 3. Análise de Marketing
- Eficiência das campanhas
- Análise de canais de marketing
- Taxa de conversão
- ROI das campanhas
- Insights sobre performance

### 4. Análise Integrada
- Relação temporal entre campanhas e vendas
- Análise regional de performance
- Correlação entre marketing e vendas
- Oportunidades de otimização

### 5. Análises Adicionais
- **Análise de Churn**
  - Taxa de abandono de clientes
  - Identificação de clientes em risco
  - Estratégias de retenção

- **Análise de Retenção**
  - Taxa de retenção mensal
  - Padrões de comportamento
  - Programas de fidelização

- **Classificação de Clientes**
  - Segmentação RFM
  - Comportamento de compra
  - Oportunidades de upsell

- **Consulta SQL Personalizada**
  - Interface para consultas customizadas
  - Visualização de resultados
  - Geração de gráficos dinâmicos

## Como Usar

1. Execute a aplicação:
```bash
streamlit run app.py
```

2. Faça upload do arquivo `vendas_marketing.db` na barra lateral

3. Navegue pelas diferentes seções usando o menu lateral

4. Interaja com os gráficos e visualizações

5. Explore as análises adicionais para insights mais profundos

## Insights Principais

A aplicação fornece insights valiosos em várias áreas:

- **Vendas**
  - Canais mais eficientes
  - Produtos com melhor desempenho
  - Padrões sazonais
  - Segmentação de clientes

- **Marketing**
  - Campanhas mais efetivas
  - Canais com maior engajamento
  - ROI por campanha
  - Estratégias de otimização

- **Cliente**
  - Comportamento de compra
  - Taxa de retenção
  - Segmentação RFM
  - Oportunidades de crescimento
