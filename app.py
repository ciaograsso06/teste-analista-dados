import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import base64
#Comandos para instalar as bibliotecas:
# pip install streamlit pandas plotly reportlab

st.set_page_config(
    page_title="Análise de Vendas e Marketing",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 2rem;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-top: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        margin: 1rem 0;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(db_path):
    try:
        conn = sqlite3.connect(db_path)
        tables = {}
        tables['clientes'] = pd.read_sql_query("SELECT * FROM Clientes", conn)
        tables['campanhas'] = pd.read_sql_query("SELECT * FROM Campanhas_Marketing", conn)
        tables['interacoes'] = pd.read_sql_query("SELECT * FROM Interacoes_Marketing", conn)
        tables['produtos'] = pd.read_sql_query("SELECT * FROM Produtos", conn)
        tables['vendas'] = pd.read_sql_query("SELECT * FROM Vendas", conn)
        conn.close()
        return tables
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

def execute_query(db_path, query):
    try:
        conn = sqlite3.connect(db_path)
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result
    except Exception as e:
        st.error(f"Erro na consulta: {str(e)}")
        return None

def analise_vendas_por_canal(tables):
    vendas = tables['vendas']
    vendas['data_venda'] = pd.to_datetime(vendas['data_venda'])
    data_limite = vendas['data_venda'].max() - timedelta(days=90)
    vendas_trimestre = vendas[vendas['data_venda'] >= data_limite]
    vendas_canal = vendas_trimestre.groupby('canal_aquisicao')['valor_total'].sum().reset_index()
    fig = px.bar(vendas_canal, x='canal_aquisicao', y='valor_total',
                 title='Total de Vendas por Canal (Último Trimestre)',
                 color='canal_aquisicao',
                 color_discrete_sequence=['#3498db', '#e74c3c'])
    return fig, vendas_canal

def top_produtos_analise(tables):
    vendas = tables['vendas']
    produtos = tables['produtos']
    vendas_produtos = vendas.groupby('id_produto').agg({
        'quantidade': 'sum',
        'valor_total': 'sum'
    }).reset_index()
    vendas_produtos = vendas_produtos.merge(produtos, left_on='id_produto', right_on='id_produto')
    vendas_produtos['margem_lucro'] = ((vendas_produtos['preco_unitario'] - vendas_produtos['custo_unitario']) / vendas_produtos['preco_unitario']) * 100
    top_5 = vendas_produtos.nlargest(5, 'quantidade')[['nome_produto', 'quantidade', 'valor_total', 'margem_lucro']]
    fig = px.bar(top_5, x='nome_produto', y='quantidade',
                 title='Top 5 Produtos por Volume de Vendas',
                 color='margem_lucro',
                 color_continuous_scale='viridis')
    return fig, top_5

def segmentacao_clientes(tables):
    vendas = tables['vendas']
    clientes = tables['clientes']
    vendas_clientes = vendas.merge(clientes, left_on='id_cliente', right_on='id_cliente')
    ticket_medio = vendas_clientes.groupby('segmento')['valor_total'].mean().reset_index()
    fig = px.bar(ticket_medio, x='segmento', y='valor_total',
                 title='Ticket Médio por Segmento de Cliente',
                 color='segmento',
                 color_discrete_sequence=['#9b59b6', '#f39c12'])
    return fig, ticket_medio

def analise_sazonalidade(tables):
    vendas = tables['vendas']
    vendas['data_venda'] = pd.to_datetime(vendas['data_venda'])
    vendas['mes'] = vendas['data_venda'].dt.month
    vendas['nome_mes'] = vendas['data_venda'].dt.strftime('%B')
    vendas_mensais = vendas.groupby('mes')['valor_total'].sum().reset_index()
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    vendas_mensais['nome_mes'] = [meses[i-1] for i in vendas_mensais['mes']]
    fig = px.line(vendas_mensais, x='nome_mes', y='valor_total',
                  title='Padrão de Vendas ao Longo do Ano',
                  markers=True)
    return fig, vendas_mensais

def eficiencia_campanhas(tables):
    campanhas = tables['campanhas']
    interacoes = tables['interacoes']
    conversoes = interacoes[interacoes['tipo_interacao'] == 'Conversão'].groupby('id_campanha').size().reset_index(name='conversoes')
    total_interacoes = interacoes.groupby('id_campanha').size().reset_index(name='total_interacoes')
    eficiencia = conversoes.merge(total_interacoes, on='id_campanha')
    eficiencia['taxa_conversao'] = (eficiencia['conversoes'] / eficiencia['total_interacoes']) * 100
    eficiencia = eficiencia.merge(campanhas, left_on='id_campanha', right_on='id_campanha')
    fig = px.scatter(eficiencia, x='orcamento', y='taxa_conversao',
                     size='conversoes', color='canal_marketing',
                     title='Eficiência das Campanhas (Taxa de Conversão vs Orçamento)',
                     hover_data=['nome_campanha'])
    return fig, eficiencia

def analise_canais_marketing(tables):
    campanhas = tables['campanhas']
    interacoes = tables['interacoes']
    camp_interacoes = interacoes.merge(campanhas, left_on='id_campanha', right_on='id_campanha')
    engajamento = camp_interacoes.groupby('canal_marketing').size().reset_index(name='total_interacoes')
    fig = px.pie(engajamento, values='total_interacoes', names='canal_marketing',
                 title='Engajamento por Canal de Marketing')
    return fig, engajamento

def relacao_temporal(tables):
    vendas = tables['vendas']
    campanhas = tables['campanhas']
    produtos = tables['produtos']
    vendas['data_venda'] = pd.to_datetime(vendas['data_venda'])
    campanhas['data_inicio'] = pd.to_datetime(campanhas['data_inicio'])
    vendas_produtos = vendas.merge(produtos, left_on='id_produto', right_on='id_produto')
    
    # Convertendo para string no formato YYYY-MM
    vendas_produtos['mes_ano'] = vendas_produtos['data_venda'].dt.strftime('%Y-%m')
    
    vendas_mensais = vendas_produtos.groupby(['mes_ano', 'nome_produto']).agg({
        'quantidade': 'sum'
    }).reset_index()
    
    top_produtos = vendas_produtos.groupby('nome_produto')['quantidade'].sum().nlargest(3).index
    vendas_top = vendas_mensais[vendas_mensais['nome_produto'].isin(top_produtos)]
    
    fig = px.line(vendas_top, x='mes_ano', y='quantidade', color='nome_produto',
                  title='Vendas de Top Produtos ao Longo do Tempo')
    return fig, vendas_top

def analise_regional(tables):
    vendas = tables['vendas']
    clientes = tables['clientes']
    interacoes = tables['interacoes']
    vendas_clientes = vendas.merge(clientes, left_on='id_cliente', right_on='id_cliente')
    vendas_cidade = vendas_clientes.groupby('cidade')['valor_total'].sum().reset_index()
    int_clientes = interacoes.merge(clientes, left_on='id_cliente', right_on='id_cliente')
    int_cidade = int_clientes.groupby('cidade').size().reset_index(name='interacoes')
    regional = vendas_cidade.merge(int_cidade, on='cidade')
    regional['vendas_por_interacao'] = regional['valor_total'] / regional['interacoes']
    fig = px.scatter(regional, x='interacoes', y='valor_total',
                     size='vendas_por_interacao', hover_data=['cidade'],
                     title='Análise Regional: Vendas vs Interações de Marketing')
    return fig, regional

def analise_churn(tables):
    vendas = tables['vendas']
    clientes = tables['clientes']
    
    # Convertendo datas
    vendas['data_venda'] = pd.to_datetime(vendas['data_venda'])
    
    # Encontrando última compra de cada cliente
    ultima_compra = vendas.groupby('id_cliente')['data_venda'].max().reset_index()
    ultima_compra.columns = ['id_cliente', 'ultima_compra']
    
    # Data atual (última data de venda no dataset)
    data_atual = vendas['data_venda'].max()
    
    # Calculando dias desde última compra
    ultima_compra['dias_sem_comprar'] = (data_atual - ultima_compra['ultima_compra']).dt.days
    
    # Definindo clientes inativos (sem compras nos últimos 90 dias)
    ultima_compra['status'] = ultima_compra['dias_sem_comprar'].apply(
        lambda x: 'Ativo' if x <= 90 else 'Inativo'
    )
    
    # Calculando métricas de churn
    total_clientes = len(ultima_compra)
    clientes_inativos = len(ultima_compra[ultima_compra['status'] == 'Inativo'])
    taxa_churn = (clientes_inativos / total_clientes) * 100
    
    # Criando gráfico de distribuição de dias sem comprar
    fig = px.histogram(ultima_compra, x='dias_sem_comprar',
                      title='Distribuição de Dias sem Comprar',
                      labels={'dias_sem_comprar': 'Dias desde última compra'},
                      color='status',
                      color_discrete_map={'Ativo': '#2ecc71', 'Inativo': '#e74c3c'})
    
    return fig, ultima_compra, taxa_churn

def analise_retencao(tables):
    vendas = tables['vendas']
    clientes = tables['clientes']
    
    # Convertendo datas
    vendas['data_venda'] = pd.to_datetime(vendas['data_venda'])
    vendas['mes_ano'] = vendas['data_venda'].dt.strftime('%Y-%m')
    
    # Encontrando primeiro mês de compra de cada cliente
    primeira_compra = vendas.groupby('id_cliente')['mes_ano'].min().reset_index()
    primeira_compra.columns = ['id_cliente', 'primeiro_mes']
    
    # Calculando retenção mensal
    meses_unicos = sorted(vendas['mes_ano'].unique())
    retencao = []
    
    for mes in meses_unicos:
        clientes_mes = vendas[vendas['mes_ano'] == mes]['id_cliente'].unique()
        novos_clientes = primeira_compra[primeira_compra['primeiro_mes'] == mes]['id_cliente'].unique()
        clientes_retidos = len(set(clientes_mes) - set(novos_clientes))
        total_clientes_anterior = len(primeira_compra[primeira_compra['primeiro_mes'] < mes])
        
        if total_clientes_anterior > 0:
            taxa_retencao = (clientes_retidos / total_clientes_anterior) * 100
        else:
            taxa_retencao = 0
            
        retencao.append({
            'mes': mes,
            'taxa_retencao': taxa_retencao,
            'novos_clientes': len(novos_clientes),
            'clientes_retidos': clientes_retidos
        })
    
    df_retencao = pd.DataFrame(retencao)
    
    # Criando gráfico de retenção
    fig = px.line(df_retencao, x='mes', y='taxa_retencao',
                  title='Taxa de Retenção Mensal',
                  labels={'taxa_retencao': 'Taxa de Retenção (%)', 'mes': 'Mês'})
    
    return fig, df_retencao

def classificacao_clientes(tables):
    vendas = tables['vendas']
    clientes = tables['clientes']
    
    # Calculando métricas por cliente
    metricas_clientes = vendas.groupby('id_cliente').agg({
        'valor_total': ['sum', 'mean', 'count'],
        'data_venda': ['min', 'max']
    }).reset_index()
    
    metricas_clientes.columns = ['id_cliente', 'valor_total', 'ticket_medio', 'frequencia', 'primeira_compra', 'ultima_compra']
    
    # Calculando RFM
    data_atual = vendas['data_venda'].max()
    metricas_clientes['recencia'] = (data_atual - metricas_clientes['ultima_compra']).dt.days
    
    # Classificando clientes
    def classificar_cliente(row):
        if row['valor_total'] > metricas_clientes['valor_total'].quantile(0.75) and \
           row['frequencia'] > metricas_clientes['frequencia'].quantile(0.75) and \
           row['recencia'] < metricas_clientes['recencia'].quantile(0.25):
            return 'Alto Valor'
        elif row['valor_total'] > metricas_clientes['valor_total'].quantile(0.5) and \
             row['frequencia'] > metricas_clientes['frequencia'].quantile(0.5):
            return 'Valor Médio'
        elif row['recencia'] > metricas_clientes['recencia'].quantile(0.75):
            return 'Em Risco'
        else:
            return 'Baixo Valor'
    
    metricas_clientes['segmento'] = metricas_clientes.apply(classificar_cliente, axis=1)
    
    # Criando gráfico de distribuição de segmentos
    fig = px.pie(metricas_clientes, names='segmento',
                 title='Distribuição de Clientes por Segmento',
                 color='segmento',
                 color_discrete_map={
                     'Alto Valor': '#2ecc71',
                     'Valor Médio': '#3498db',
                     'Em Risco': '#e74c3c',
                     'Baixo Valor': '#95a5a6'
                 })
    
    return fig, metricas_clientes

def main():
    st.markdown('<h1 class="main-header">📊 Análise de Vendas e Marketing</h1>', unsafe_allow_html=True)
    st.sidebar.header("📁 Carregar Banco de Dados")
    uploaded_file = st.sidebar.file_uploader(
        "Selecione o arquivo vendas_marketing.db",
        type=['db', 'sqlite', 'sqlite3'],
        help="Faça upload do arquivo SQLite com os dados de vendas e marketing"
    )
    if uploaded_file is not None:
        with open("temp_database.db", "wb") as f:
            f.write(uploaded_file.getbuffer())
        with st.spinner("Carregando dados..."):
            tables = load_data("temp_database.db")
        if tables is not None:
            st.sidebar.success("✅ Banco de dados carregado com sucesso!")
            st.sidebar.markdown("### 📊 Informações do Banco")
            for table_name, df in tables.items():
                st.sidebar.write(f"**{table_name.title()}**: {len(df)} registros")
            st.sidebar.markdown("### 🔍 Análises Disponíveis")
            menu_options = [
                "📋 Visão Geral",
                "💰 A. Análise de Vendas",
                "📈 B. Análise de Marketing", 
                "🔄 C. Análise Integrada",
                "🎯 D. Análises Adicionais"
            ]
            selected_section = st.sidebar.selectbox("Selecione uma seção:", menu_options)
            
            if selected_section == "📋 Visão Geral":
                st.markdown('<h2 class="section-header">Visão Geral dos Dados</h2>', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total de Clientes", len(tables['clientes']))
                with col2:
                    st.metric("Total de Produtos", len(tables['produtos']))
                with col3:
                    st.metric("Total de Campanhas", len(tables['campanhas']))
                with col4:
                    total_vendas = tables['vendas']['valor_total'].sum()
                    st.metric("Receita Total", f"R$ {total_vendas:,.2f}")
                st.markdown("### 📊 Preview das Tabelas")
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["Clientes", "Produtos", "Campanhas", "Vendas", "Interações"])
                with tab1:
                    st.dataframe(tables['clientes'].head(), use_container_width=True)
                with tab2:
                    st.dataframe(tables['produtos'].head(), use_container_width=True)
                with tab3:
                    st.dataframe(tables['campanhas'].head(), use_container_width=True)
                with tab4:
                    st.dataframe(tables['vendas'].head(), use_container_width=True)
                with tab5:
                    st.dataframe(tables['interacoes'].head(), use_container_width=True)
            
            elif selected_section == "💰 A. Análise de Vendas":
                st.markdown('<h2 class="section-header">A. Análise de Vendas</h2>', unsafe_allow_html=True)
                st.markdown("""
                ### 📊 Visão Geral da Seção
                Esta seção apresenta uma análise abrangente das vendas, permitindo entender:
                - Desempenho por canal de aquisição
                - Produtos mais vendidos e suas margens
                - Segmentação de clientes e ticket médio
                - Padrões sazonais de vendas
                
                #### 💡 Principais Insights
                - Identificação dos canais mais eficientes
                - Produtos com melhor desempenho
                - Comportamento de compra por segmento
                - Períodos de maior e menor volume de vendas
                """)
                
                st.markdown("### 1. Total de Vendas por Canal")
                fig1, data1 = analise_vendas_por_canal(tables)
                st.plotly_chart(fig1, use_container_width=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(data1, use_container_width=True)
                with col2:
                    st.markdown('<div class="insight-box"><h4>💡 Insights</h4><p>Análise do desempenho dos canais de aquisição no último trimestre.</p></div>', unsafe_allow_html=True)
                st.divider()
                
                st.markdown("### 2. Top 5 Produtos")
                fig2, data2 = top_produtos_analise(tables)
                st.plotly_chart(fig2, use_container_width=True)
                st.dataframe(data2, use_container_width=True)
                st.divider()
                
                st.markdown("### 3. Segmentação de Clientes")
                fig3, data3 = segmentacao_clientes(tables)
                st.plotly_chart(fig3, use_container_width=True)
                st.dataframe(data3, use_container_width=True)
                st.divider()
                
                st.markdown("### 4. Análise de Sazonalidade")
                fig4, data4 = analise_sazonalidade(tables)
                st.plotly_chart(fig4, use_container_width=True)
                st.dataframe(data4, use_container_width=True)
            
            elif selected_section == "📈 B. Análise de Marketing":
                st.markdown('<h2 class="section-header">B. Análise de Marketing</h2>', unsafe_allow_html=True)
                st.markdown("""
                ### 📊 Visão Geral da Seção
                Esta seção avalia a eficácia das campanhas de marketing, incluindo:
                - Taxa de conversão por campanha
                - ROI das campanhas
                - Engajamento por canal
                - Eficiência do orçamento
                
                #### 💡 Principais Insights
                - Campanhas com melhor desempenho
                - Canais mais engajados
                - Relação entre investimento e resultados
                - Oportunidades de otimização
                """)
                
                st.markdown("### 5. Eficiência das Campanhas")
                fig5, data5 = eficiencia_campanhas(tables)
                st.plotly_chart(fig5, use_container_width=True)
                st.dataframe(data5[['nome_campanha', 'canal_marketing', 'orcamento', 'taxa_conversao', 'conversoes']], use_container_width=True)
                st.divider()
                
                st.markdown("### 6. Análise de Canais de Marketing")
                fig6, data6 = analise_canais_marketing(tables)
                st.plotly_chart(fig6, use_container_width=True)
                st.dataframe(data6, use_container_width=True)
            
            elif selected_section == "🔄 C. Análise Integrada":
                st.markdown('<h2 class="section-header">C. Análise Integrada</h2>', unsafe_allow_html=True)
                st.markdown("""
                ### 📊 Visão Geral da Seção
                Esta seção integra dados de vendas e marketing para:
                - Correlação entre campanhas e vendas
                - Impacto regional das campanhas
                - Eficácia por segmento de cliente
                - Oportunidades de otimização
                
                #### 💡 Principais Insights
                - Relação entre investimento e resultados
                - Eficácia por região
                - Segmentos mais responsivos
                - Oportunidades de crescimento
                """)
                
                st.markdown("### 7. Relação Temporal")
                fig7, data7 = relacao_temporal(tables)
                st.plotly_chart(fig7, use_container_width=True)
                st.divider()
                
                st.markdown("### 8. Análise Regional")
                fig8, data8 = analise_regional(tables)
                st.plotly_chart(fig8, use_container_width=True)
                st.dataframe(data8, use_container_width=True)
            
            elif selected_section == "🎯 D. Análises Adicionais":
                st.markdown('<h2 class="section-header">D. Análises Adicionais</h2>', unsafe_allow_html=True)
                st.markdown("""
                ### 📊 Visão Geral da Seção
                Esta seção apresenta análises avançadas focadas em:
                - Taxa de churn e retenção
                - Segmentação RFM
                - Comportamento de compra
                - Oportunidades de crescimento
                
                #### 💡 Principais Insights
                - Identificação de clientes em risco
                - Padrões de retenção
                - Segmentação comportamental
                - Estratégias de fidelização
                """)
                
                # Adicionando abas para diferentes análises
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 Análise de Churn",
                    "📈 Retenção de Clientes",
                    "👥 Classificação de Clientes",
                    "🔍 Consulta SQL Personalizada"
                ])
                
                with tab1:
                    st.markdown("### 📊 Análise de Churn")
                    fig_churn, df_churn, taxa_churn = analise_churn(tables)
                    st.plotly_chart(fig_churn, use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Taxa de Churn", f"{taxa_churn:.1f}%")
                    with col2:
                        st.metric("Clientes Ativos", 
                                len(df_churn[df_churn['status'] == 'Ativo']))
                    
                    st.markdown("""
                    #### 💡 Insights sobre Churn
                    - **Definição**: Clientes considerados inativos após 90 dias sem compras
                    - **Ações Recomendadas**:
                        - Implementar programa de fidelidade
                        - Criar campanhas de reativação
                        - Analisar padrões de compra dos clientes ativos
                    """)
                
                with tab2:
                    st.markdown("### 📈 Análise de Retenção")
                    fig_retencao, df_retencao = analise_retencao(tables)
                    st.plotly_chart(fig_retencao, use_container_width=True)
                    
                    st.markdown("""
                    #### 💡 Insights sobre Retenção
                    - **Métrica**: Taxa de clientes que retornam mês a mês
                    - **Ações Recomendadas**:
                        - Identificar períodos de maior retenção
                        - Replicar estratégias bem-sucedidas
                        - Desenvolver programas de fidelização
                    """)
                
                with tab3:
                    st.markdown("### 👥 Classificação de Clientes")
                    fig_class, df_class = classificacao_clientes(tables)
                    st.plotly_chart(fig_class, use_container_width=True)
                    
                    st.markdown("""
                    #### 💡 Insights sobre Classificação
                    - **Segmentos**:
                        - **Alto Valor**: Maior frequência e valor de compras
                        - **Valor Médio**: Bom histórico de compras
                        - **Em Risco**: Baixa atividade recente
                        - **Baixo Valor**: Menor engajamento
                    - **Ações Recomendadas**:
                        - Personalizar comunicação por segmento
                        - Desenvolver programas específicos
                        - Identificar oportunidades de upsell
                    """)
                
                with tab4:
                    st.markdown("### 🔍 Consulta SQL Personalizada")
                    query = st.text_area(
                        "Digite sua consulta SQL:",
                        height=150,
                        placeholder="SELECT * FROM Vendas LIMIT 10"
                    )
                    if st.button("Executar Consulta"):
                        if query.strip():
                            result = execute_query("temp_database.db", query)
                            if result is not None:
                                st.dataframe(result, use_container_width=True)
                                if len(result.columns) >= 2:
                                    st.markdown("### 📊 Visualização dos Resultados")
                                    col_x = st.selectbox("Eixo X:", result.columns)
                                    col_y = st.selectbox("Eixo Y:", [col for col in result.columns if col != col_x])
                                    chart_type = st.selectbox("Tipo de Gráfico:", ["Bar", "Line", "Scatter"])
                                    if st.button("Gerar Gráfico"):
                                        if chart_type == "Bar":
                                            fig = px.bar(result, x=col_x, y=col_y)
                                        elif chart_type == "Line":
                                            fig = px.line(result, x=col_x, y=col_y)
                                        else:
                                            fig = px.scatter(result, x=col_x, y=col_y)
                                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👆 Faça upload do arquivo vendas_marketing.db na barra lateral para começar a análise.")
        st.markdown("""
        ### 📚 Sobre o Banco de Dados
        
        O banco deve conter as seguintes tabelas:
        - **Clientes**: id_cliente, nome, segmento (B2B/B2C), cidade
        - **Campanhas_Marketing**: id_campanha, nome_campanha, canal_marketing, data_inicio, data_fim, orcamento, custo
        - **Interacoes_Marketing**: id_interacao, id_cliente, id_campanha, data_interacao, tipo_interacao
        - **Produtos**: id_produto, nome_produto, categoria, preco_unitario, custo_unitario
        - **Vendas**: id_venda, id_cliente, id_produto, id_campanha, data_venda, quantidade, valor_total, canal_aquisicao
        """)

if __name__ == "__main__":
    main() 
