import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis
import plotly.express as px
from scipy.stats import f_oneway

st.set_page_config(page_title="Felicidade Mundial 2019", layout="wide")

@st.cache_data
def load_and_prepare_data():
    # Carrega o dataset
    df = pd.read_csv("2019.csv")

    # Criar Score Category com base nos tercis do Score
    tercis = df['Score'].quantile([0.33, 0.66])
    def categorize(score):
        if score <= tercis[0.33]:
            return "Baixo"
        elif score <= tercis[0.66]:
            return "Médio"
        else:
            return "Alto"
    df['Score Category'] = df['Score'].apply(categorize)

    # Criar variável Riqueza baseado no GDP per capita (mediana)
    median_gdp = df['GDP per capita'].median()
    df['Riqueza'] = df['GDP per capita'].apply(lambda x: "Rico" if x >= median_gdp else "Pobre")

    # Verifica se 'Regional indicator' existe, se não cria coluna padrão
    if 'Regional indicator' not in df.columns:
        df['Regional indicator'] = "Desconhecido"

    # Mapear Continente a partir do Regional indicator
    continent_map = {
        'Western Europe': 'Europa', 'North America': 'América',
        'Sub-Saharan Africa': 'África', 'Central and Eastern Europe': 'Europa',
        'Middle East and North Africa': 'África/Oriente Médio',
        'Latin America and Caribbean': 'América Latina',
        'Southeast Asia': 'Ásia', 'East Asia': 'Ásia'
    }
    df['Continent'] = df['Regional indicator'].map(continent_map).fillna("Outro")

    return df

df = load_and_prepare_data()

# Barra lateral para navegação
st.sidebar.title("🔎 Navegação")
pages = [
    "Introdução",
    "1. Distribuição do Score",
    "2. Histogramas e Boxplots",
    "3. Assimetria e Curtose",
    "4. Score Category",
    "5. Score x Riqueza",
    "6. GDP vs Vida Saudável",
    "7. Dispersão: GDP x Score",
    "8. Heatmap de Correlações",
    "9. Generosidade por Continente",
    "10. Liberdade x Categoria de Felicidade"
]
choice = st.sidebar.radio("Escolha uma seção:", pages)

if choice == "Introdução":
    st.title("🌍 O Analista Socioeconômico Global")
    st.markdown("""
    Este relatório explora os fatores socioeconômicos associados à **felicidade mundial** com base no _World Happiness Report 2019_.

    Utilizando análise exploratória de dados, buscamos responder questões relacionadas à distribuição da felicidade, desigualdade entre países, fatores econômicos, sociais e culturais.

    **Tema:** Economia e Desenvolvimento Social  
    **Fonte:** [Kaggle - World Happiness Report 2019](https://www.kaggle.com/unsdsn/world-happiness)
    """)

elif choice == "1. Distribuição do Score":
    st.header("1️⃣ Distribuição do Score de Felicidade")
    st.write(df['Score'].describe())
    st.markdown("""
    As medidas de tendência central e dispersão mostram que a maioria dos países possuem uma pontuação de felicidade entre 4.5 e 6.5.
    """)

elif choice == "2. Histogramas e Boxplots":
    st.header("2️⃣ Histogramas e Boxplots do Score")
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(df['Score'], kde=True, ax=axs[0], color='skyblue')
    axs[0].set_title("Histograma do Score")
    sns.boxplot(y=df['Score'], ax=axs[1], color='lightgreen')
    axs[1].set_title("Boxplot do Score")
    st.pyplot(fig)

elif choice == "3. Assimetria e Curtose":
    st.header("3️⃣ Assimetria e Curtose do Score")
    skewness = skew(df['Score'])
    kurt = kurtosis(df['Score'])
    st.write(f"**Assimetria:** {skewness:.2f}")
    st.write(f"**Curtose:** {kurt:.2f}")
    st.markdown("""
    - Assimetria próxima de 0 indica uma distribuição quase simétrica.
    - Curtose próxima de 0 indica distribuição mesocúrtica (sem caudas pesadas).
    """)

elif choice == "4. Score Category":
    st.header("4️⃣ Classificação por Categoria de Felicidade")
    freq = df['Score Category'].value_counts()
    st.write(freq)
    st.bar_chart(freq)

elif choice == "5. Score x Riqueza":
    st.header("5️⃣ Felicidade x Riqueza do País")
    crosstab = pd.crosstab(df['Riqueza'], df['Score Category'])
    st.write(crosstab)
    st.bar_chart(crosstab)

elif choice == "6. GDP vs Vida Saudável":
    st.header("6️⃣ Correlação entre PIB per capita e Expectativa de Vida Saudável")
    corr = df[['GDP per capita', 'Healthy life expectancy']].corr().iloc[0, 1]
    st.write(f"Correlação de Pearson: {corr:.2f}")
    fig = px.scatter(df, x='GDP per capita', y='Healthy life expectancy',
                     color='Score Category', title='GDP vs Vida Saudável')
    st.plotly_chart(fig)

elif choice == "7. Dispersão: GDP x Score":
    st.header("7️⃣ Diagrama de Dispersão: GDP per capita x Score de Felicidade")
    fig = px.scatter(df, x='GDP per capita', y='Score',
                     color='Score Category', hover_name='Country or region')
    st.plotly_chart(fig)

elif choice == "8. Heatmap de Correlações":
    st.header("8️⃣ Mapa de Calor das Correlações")
    numeric_cols = df.select_dtypes(include=np.number)
    corr_matrix = numeric_cols.corr()
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
    st.pyplot(fig)

elif choice == "9. Generosidade por Continente":
    st.header("9️⃣ Generosidade Média por Continente")

  

    df_valid = df[(df['Continent'] != 'Outro') & (df['Generosity'].notna())]


    grouped = [group['Generosity'].values for name, group in df_valid.groupby('Continent') if len(group) > 1]

    if len(grouped) < 2:
        st.warning("Não há dados suficientes para realizar o teste ANOVA.")
    else:
        try:
            f_stat, p_value = f_oneway(*grouped)
            st.markdown(f"**Estatística F:** {f_stat:.4f}")
            st.markdown(f"**p-valor:** {p_value:.4f}")
            if p_value < 0.05:
                st.success("→ Há diferença estatisticamente significativa na generosidade entre os continentes.")
            else:
                st.info("→ Não há diferença estatisticamente significativa na generosidade entre os continentes.")
        except Exception as e:
            st.error(f"Erro ao executar ANOVA: {e}")


elif choice == "10. Liberdade x Categoria de Felicidade":
    st.header("🔟 Liberdade para cada Categoria de Felicidade")
    group_stats = df.groupby('Score Category')['Freedom to make life choices'].describe()
    st.write(group_stats)
    fig, ax = plt.subplots()
    sns.boxplot(data=df, x='Score Category', y='Freedom to make life choices', palette='pastel')
    ax.set_title("Liberdade x Categoria de Felicidade")
    st.pyplot(fig)
