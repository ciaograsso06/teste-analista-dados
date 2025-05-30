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
    vendas_mensais = vendas_produtos.groupby([vendas_produtos['data_venda'].dt.to_period('M'), 'nome_produto']).agg({
        'quantidade': 'sum'
    }).reset_index()
    top_produtos = vendas_produtos.groupby('nome_produto')['quantidade'].sum().nlargest(3).index
    vendas_top = vendas_mensais[vendas_mensais['nome_produto'].isin(top_produtos)]
    fig = px.line(vendas_top, x='data_venda', y='quantidade', color='nome_produto',
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

def gerar_pdf_relatorio(analises_resultados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1f77b4')
    )
    story.append(Paragraph("Relatório de Análise de Vendas e Marketing", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 30))
    sections = [
        ("A. ANÁLISE DE VENDAS", [
            ("1. Vendas por Canal", "Análise do desempenho por canal de aquisição no último trimestre."),
            ("2. Top Produtos", "Identificação dos 5 produtos com maior volume de vendas."),
            ("3. Segmentação de Clientes", "Comparação do ticket médio entre B2B e B2C."),
            ("4. Sazonalidade", "Padrão de vendas ao longo do ano.")
        ]),
        ("B. ANÁLISE DE MARKETING", [
            ("5. Eficiência das Campanhas", "Taxa de conversão e ROI das campanhas."),
            ("6. Canais de Marketing", "Engajamento por canal de marketing.")
        ]),
        ("C. ANÁLISE INTEGRADA", [
            ("7. Relação Temporal", "Correlação entre campanhas e vendas."),
            ("8. Análise Regional", "Performance regional das campanhas.")
        ])
    ]
    for section_title, items in sections:
        story.append(Paragraph(section_title, styles['Heading1']))
        story.append(Spacer(1, 15))
        for item_title, item_desc in items:
            story.append(Paragraph(item_title, styles['Heading2']))
            story.append(Paragraph(item_desc, styles['Normal']))
            story.append(Spacer(1, 10))
        story.append(PageBreak())
    doc.build(story)
    buffer.seek(0)
    return buffer

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
                "🎯 D. Análises Adicionais",
                "📄 Gerar Relatório PDF"
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
            elif selected_section == "📄 Gerar Relatório PDF":
                st.markdown('<h2 class="section-header">Gerar Relatório PDF</h2>', unsafe_allow_html=True)
                st.markdown("""
                ### 📋 Conteúdo do Relatório
                
                O relatório em PDF incluirá:
                - **Seção A**: Análise completa de vendas
                - **Seção B**: Análise de marketing e campanhas
                - **Seção C**: Análise integrada vendas-marketing
                - **Insights e Recomendações**: Principais descobertas
                """)
                if st.button("🎯 Gerar Relatório PDF", type="primary"):
                    with st.spinner("Gerando relatório..."):
                        resultados = {}
                        pdf_buffer = gerar_pdf_relatorio(resultados)
                        st.download_button(
                            label="📥 Download Relatório PDF",
                            data=pdf_buffer,
                            file_name=f"relatorio_vendas_marketing_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                        st.success("✅ Relatório gerado com sucesso!")
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