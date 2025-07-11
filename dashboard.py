import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Dashboard Corpo Docente IPT", layout="wide")

def ler_csv_robusto(caminho):
    """Tenta abrir com vírgula, se falhar tenta com ponto e vírgula."""
    try:
        df = pd.read_csv(caminho, encoding="latin1", on_bad_lines='warn')
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception:
        df = pd.read_csv(caminho, encoding="latin1", delimiter=";", on_bad_lines='warn')
        df.columns = df.columns.str.strip().str.lower()
        return df

@st.cache_data
def carregar_e_preparar_dados():
    try:
        # Carrega todos os arquivos padronizando as colunas
        df_base = ler_csv_robusto('faculdade_completo.csv')
        
        # Quem é Quem: tenta com ;, se der erro tenta com ,
        try:
            df_quem_e_quem = pd.read_csv('scrapping_quem_e_quem.csv', encoding='latin1', delimiter=';')
        except Exception:
            df_quem_e_quem = pd.read_csv('scrapping_quem_e_quem.csv', encoding='latin1', delimiter=',', on_bad_lines='skip')
        df_quem_e_quem.columns = df_quem_e_quem.columns.str.strip().str.lower()
        
        df_scopus = pd.read_csv('scrapping_scopus_metrics_limpo.csv', encoding="latin1", delimiter=';')
        df_scopus.columns = df_scopus.columns.str.strip().str.lower()
        
        df_scholar = pd.read_csv('google_scholar_busca_automatica.csv', encoding='latin1', delimiter=';')
        df_scholar.columns = df_scholar.columns.str.strip().str.lower()

        # DEBUG: Veja nomes das colunas (remover depois que rodar OK)
        #st.write("faculdade_completo.csv:", list(df_base.columns))
        #st.write("scrapping_quem_e_quem.csv:", list(df_quem_e_quem.columns))
        #st.write("scrapping_scopus_metrics_limpo.csv:", list(df_scopus.columns))
        #st.write("google_scholar_busca_automatica.csv:", list(df_scholar.columns))

        # Checa colunas disponíveis para merge
        base_nome = 'nome' if 'nome' in df_base.columns else df_base.columns[0]
        quem_nome = 'nome_completo' if 'nome_completo' in df_quem_e_quem.columns else df_quem_e_quem.columns[0]
        orcid_col = 'orcid' if 'orcid' in df_scopus.columns else df_scopus.columns[0]

        # Merge dos dados
        df_final = pd.merge(df_base, df_quem_e_quem, left_on=base_nome, right_on=quem_nome, how='left')
        df_final = pd.merge(df_final, df_scopus, on=orcid_col, how='left')
        df_final = pd.merge(df_final, df_scholar, left_on=base_nome, right_on='nome', how='left')

        # Renomeando colunas para evitar conflitos
        df_final.rename(columns={
            'h-index_x': 'h_index_scopus',
            'h-index_y': 'h_index_scholar',
            'citations': 'citacoes_scopus',
            'citações': 'citacoes_scholar',
        }, inplace=True)

        # Convertendo colunas numéricas
        for col in ['h_index_scopus', 'h_index_scholar', 'citacoes_scopus', 'citacoes_scholar', 'documents']:
            if col in df_final.columns:
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)

        # Colunas finais
        df_final['h_index_final'] = df_final.get('h_index_scopus', 0)
        if 'h_index_scholar' in df_final.columns:
            df_final['h_index_final'] = df_final['h_index_final'].where(df_final['h_index_final'] > 0, df_final['h_index_scholar'])
        df_final['h_index_final'] = df_final['h_index_final'].fillna(0).astype(int)

        df_final['citacoes_final'] = df_final.get('citacoes_scopus', 0)
        if 'citacoes_scholar' in df_final.columns:
            df_final['citacoes_final'] = df_final['citacoes_final'].where(df_final['citacoes_final'] > 0, df_final['citacoes_scholar'])
        df_final['citacoes_final'] = df_final['citacoes_final'].fillna(0).astype(int)

        # Número de disciplinas
        if 'disciplinas_lecionadas' in df_final.columns:
            df_final['n_disciplinas'] = df_final['disciplinas_lecionadas'].fillna('').astype(str).str.count(',') + 1
            df_final.loc[df_final['disciplinas_lecionadas'].fillna('') == '', 'n_disciplinas'] = 0
        else:
            df_final['n_disciplinas'] = 0

        return df_final

    except Exception as e:
        st.error(f"Erro ao carregar/processar os dados: {e}")
        return None

# --- DASHBOARD ---
df = carregar_e_preparar_dados()

if df is not None:
    st.title("Dashboard de Performance do Corpo Docente do IPT")
    st.markdown("Visualização corporativa do desempenho, perfis e análise institucional.")

    # -------- FILTROS AVANÇADOS --------
    st.sidebar.header("Filtros")
    categorias = sorted(df['categoria'].dropna().unique())
    departamentos = sorted(df['departamento'].dropna().unique()) if 'departamento' in df.columns else []
    categoria_sel = st.sidebar.multiselect("Categoria", categorias, default=categorias)
    dept_sel = st.sidebar.multiselect("Departamento", departamentos, default=departamentos) if departamentos else []
    h_index_min, h_index_max = int(df['h_index_final'].min()), int(df['h_index_final'].max())
    h_index_range = st.sidebar.slider("H-Index (range)", h_index_min, h_index_max, (h_index_min, h_index_max))

    # Aplicando os filtros
    df_filtrado = df[df['categoria'].isin(categoria_sel)]
    if departamentos:
        df_filtrado = df_filtrado[df_filtrado['departamento'].isin(dept_sel)]
    df_filtrado = df_filtrado[df_filtrado['h_index_final'].between(*h_index_range)]

    # --------- KPIs ---------
    st.subheader("Visão Geral")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Docentes", len(df_filtrado))
    col2.metric("H-Index Médio", round(df_filtrado['h_index_final'].mean(), 2))
    col3.metric("Total de Citações", int(df_filtrado['citacoes_final'].sum()))

    st.markdown("---")

    # --------- GRÁFICOS ---------
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("##### Docentes por Categoria")
        fig_cat = px.bar(df_filtrado['categoria'].value_counts().sort_values(ascending=True),
                         orientation='h', labels={'value': 'Nº de Docentes', 'index': 'Categoria'}, text_auto=True)
        st.plotly_chart(fig_cat, use_container_width=True)

        st.markdown("##### Distribuição do H-Index")
        fig_hidx = px.histogram(df_filtrado, x='h_index_final', nbins=20, title="Distribuição H-Index")
        st.plotly_chart(fig_hidx, use_container_width=True)

        if departamentos:
            st.markdown("##### Docentes por Departamento")
            fig_dept = px.pie(df_filtrado, names='departamento', title='Distribuição por Departamento')
            st.plotly_chart(fig_dept, use_container_width=True)

    with col_b:
        st.markdown("##### Top 10 Docentes por H-Index")
        top_10_h = df_filtrado[df_filtrado['h_index_final'] > 0].nlargest(10, 'h_index_final')
        fig_top10 = px.bar(
            top_10_h.sort_values('h_index_final'),
            x='h_index_final',
            y='nome',
            orientation='h',
            text='h_index_final',
            labels={'h_index_final': 'H-Index', 'nome': 'Docente'}
        )
        fig_top10.update_layout(yaxis_title=None)
        st.plotly_chart(fig_top10, use_container_width=True)

        st.markdown("##### Distribuição de Citações")
        fig_cit = px.histogram(df_filtrado, x='citacoes_final', nbins=20, title="Distribuição de Citações")
        st.plotly_chart(fig_cit, use_container_width=True)

    # --------- FACULTY PERFORMANCE TABLE ---------
    st.markdown("---")
    st.subheader("Pesquisa e Tabela dos Docentes")
    search_term = st.text_input("Buscar docente por nome")
    df_search = df_filtrado[df_filtrado['nome'].str.contains(search_term, case=False, na=False)] if search_term else df_filtrado
    st.dataframe(df_search[['nome', 'categoria', 'h_index_final', 'citacoes_final', 'orcid'] + 
                            ([ 'departamento'] if 'departamento' in df_search.columns else [])])

    # --------- ACTION ITEMS ---------
    st.markdown("---")
    st.subheader("Ações e Insights")
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        st.markdown("**Perfis incompletos (sem ORCID):**")
        st.write(df_filtrado[df_filtrado['orcid'].isnull() | (df_filtrado['orcid'] == '')][['nome', 'categoria']])

    with col_a2:
        st.markdown("**Underperformers (H-index < 2):**")
        st.write(df_filtrado[df_filtrado['h_index_final'] < 2][['nome', 'categoria', 'h_index_final']])

    with col_a3:
        st.markdown("**Top Performers (Top 10 H-Index):**")
        st.write(df_filtrado.nlargest(10, 'h_index_final')[['nome', 'categoria', 'h_index_final']])

else:
    st.error("Não foi possível carregar os dados para o dashboard.")