import streamlit as st
import pandas as pd
from plotnine import ggplot
from matplotlib import pyplot as plt
from Scripts import plot_dual_bar, plot_semaforo

# Configuração da página
st.set_page_config(
    page_title="Visualizações Dinâmicas",
    layout="wide"
)

st.title("📊 Visualização de Indicadores")

# Seleção do conjunto de dados
dataset_option = st.selectbox(
    "Escolha o conjunto de dados:",
    options=["Hitachi - PSC"]
)

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Faça upload do arquivo CSV de dados", type="csv")

# Carregamento do dataset
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# Verifica se o arquivo foi enviado
if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.success(f"Dados carregados: {dataset_option}")
else:
    st.warning("Por favor, faça o upload de um arquivo CSV para continuar.")

# Escolha do tipo de gráfico
chart_type = st.radio(
    "Escolha o tipo de gráfico:",
    ["Gráfico Semáforo", "Gráfico Dual Bar"]
)

# Renderização do gráfico
if chart_type == "Gráfico Semáforo":
    st.subheader("🚦 Gráfico Semáforo")

    group_var = "question_dimension"  # fixo, conforme solicitado

    fig = plot_semaforo.plot_semaforo(df, group_var)
    
    fig_drawn = fig.draw()
    fig_drawn.set_size_inches(8, 5)  # largura, altura em polegadas
    fig_drawn.patch.set_facecolor('white')  # força o fundo branco
    st.pyplot(fig_drawn)

elif chart_type == "Gráfico Dual Bar":
    st.subheader("📍 Gráfico de Barras Duplas")
    
    allowed_group_vars = [
        "employee_manager",
        "question_subscale",
        "question_dimension",
        "employee_biological_sex",
        "employee_department",
        "employee_shift"
    ]

    group_var = st.selectbox("Selecione a variável de agrupamento:", allowed_group_vars)
    
    fig = plot_dual_bar.plot_dual_bar(df, group_var)
    
    fig_drawn = fig.draw()
    fig_drawn.set_size_inches(8, 5)  # largura, altura em polegadas
    fig_drawn.patch.set_facecolor('white')  # força o fundo branco
    st.pyplot(fig_drawn)

