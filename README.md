# 📊 Dashboard de Análise de Vendas e Marketing

Esta é uma aplicação web interativa construída com Streamlit para realizar análises detalhadas de dados de vendas e marketing. A ferramenta permite o upload de um banco de dados SQLite e oferece visualizações dinâmicas, insights e a capacidade de gerar relatórios em PDF.

## ✨ Funcionalidades Principais

* **Upload de Banco de Dados**: Carregue facilmente seu arquivo de banco de dados SQLite (`.db`, `.sqlite`, `.sqlite3`) contendo os dados de vendas e marketing.
* **Visão Geral dos Dados**:
    * Métricas chave: Total de Clientes, Total de Produtos, Total de Campanhas, Receita Total.
    * Preview das tabelas de dados: Clientes, Produtos, Campanhas, Vendas, Interações.
* **Análise de Vendas Detalhada**:
    * **Vendas por Canal**: Visualize o total de vendas por canal de aquisição no último trimestre.
    * **Top 5 Produtos**: Identifique os produtos mais vendidos por volume, incluindo valor total e margem de lucro.
    * **Segmentação de Clientes**: Analise o ticket médio por segmento de cliente (B2B/B2C).
    * **Análise de Sazonalidade**: Observe o padrão de vendas ao longo dos meses do ano.
* **Análise de Marketing Abrangente**:
    * **Eficiência das Campanhas**: Avalie a taxa de conversão versus o orçamento das campanhas, segmentado por canal de marketing.
    * **Análise de Canais de Marketing**: Entenda o engajamento total por canal de marketing.
* **Análise Integrada**:
    * **Relação Temporal**: Acompanhe as vendas dos top 3 produtos ao longo do tempo.
    * **Análise Regional**: Compare vendas versus interações de marketing por cidade.
* **Consultas SQL Personalizadas**:
    * Execute suas próprias consultas SQL diretamente na interface.
    * Gere gráficos (barra, linha, dispersão) a partir dos resultados da consulta.
* **Geração de Relatórios em PDF**:
    * Crie um relatório resumido em PDF contendo as principais seções de análise.

## ⚙️ Pré-requisitos

1.  **Python**: Versão 3.7 ou superior.
2.  **Bibliotecas Python**:
    * `streamlit`
    * `pandas`
    * `plotly`
    * `reportlab`
    * `numpy` (geralmente instalado como dependência do pandas)
3.  **Banco de Dados SQLite**: Um arquivo `vendas_marketing.db` (ou similar) com a seguinte estrutura de tabelas e colunas:
    * **Clientes**:
        * `id_cliente` (Chave Primária)
        * `nome`
        * `segmento` (Ex: 'B2B', 'B2C')
        * `cidade`
    * **Campanhas_Marketing**:
        * `id_campanha` (Chave Primária)
        * `nome_campanha`
        * `canal_marketing`
        * `data_inicio` (Formato: YYYY-MM-DD HH:MM:SS ou similar)
        * `data_fim` (Formato: YYYY-MM-DD HH:MM:SS ou similar)
        * `orcamento`
        * `custo`
    * **Interacoes_Marketing**:
        * `id_interacao` (Chave Primária)
        * `id_cliente` (Chave Estrangeira para Clientes)
        * `id_campanha` (Chave Estrangeira para Campanhas_Marketing)
        * `data_interacao` (Formato: YYYY-MM-DD HH:MM:SS ou similar)
        * `tipo_interacao` (Ex: 'Clique', 'Visualização', 'Conversão')
    * **Produtos**:
        * `id_produto` (Chave Primária)
        * `nome_produto`
        * `categoria`
        * `preco_unitario`
        * `custo_unitario`
    * **Vendas**:
        * `id_venda` (Chave Primária)
        * `id_cliente` (Chave Estrangeira para Clientes)
        * `id_produto` (Chave Estrangeira para Produtos)
        * `id_campanha` (Chave Estrangeira para Campanhas_Marketing, pode ser nulo)
        * `data_venda` (Formato: YYYY-MM-DD HH:MM:SS ou similar)
        * `quantidade`
        * `valor_total`
        * `canal_aquisicao` (Ex: 'Online', 'Loja Física')

## 🚀 Instalação

1.  **Clone o repositório (se aplicável) ou salve o código Python em um arquivo (ex: `app.py`).**

2.  **Navegue até o diretório do projeto pelo terminal.**

3.  **Instale as dependências necessárias:**
    ```bash
    pip install streamlit pandas plotly reportlab
    ```

## 🛠️ Como Usar

1.  **Prepare seu arquivo de banco de dados SQLite** (`vendas_marketing.db`) com a estrutura de tabelas e colunas descrita em "Pré-requisitos".

2.  **Execute a aplicação Streamlit através do terminal:**
    ```bash
    streamlit run seu_arquivo.py
    ```
    (Substitua `seu_arquivo.py` pelo nome do arquivo onde você salvou o código Python).

3.  **Acesse a aplicação no seu navegador**: Geralmente, o Streamlit abrirá automaticamente o endereço `http://localhost:8501`.

4.  **Carregue o Banco de Dados**:
    * Na barra lateral esquerda, clique em "Selecione o arquivo vendas\_marketing.db".
    * Faça o upload do seu arquivo `.db`.

5.  **Navegue pelas Análises**:
    * Utilize o menu suspenso na barra lateral ("Selecione uma seção:") para escolher a análise desejada:
        * 📋 Visão Geral
        * 💰 A. Análise de Vendas
        * 📈 B. Análise de Marketing
        * 🔄 C. Análise Integrada
        * 🎯 D. Análises Adicionais (para consultas SQL)
        * 📄 Gerar Relatório PDF

6.  **Interaja com os Gráficos**:
    * Passe o mouse sobre os gráficos para ver detalhes.
    * Utilize as ferramentas do Plotly (zoom, pan, download de imagem) disponíveis nos gráficos.

7.  **Gerar Relatório PDF**:
    * Selecione a opção "📄 Gerar Relatório PDF" na barra lateral.
    * Clique no botão "🎯 Gerar Relatório PDF".
    * Faça o download do arquivo PDF gerado.
