import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ===========================
# Configuration globale
# ===========================
st.set_page_config(page_title="📊 Dashboard Analytique", layout="wide")
sns.set_theme(style="whitegrid")

st.markdown("""
<style>
  html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
  h1, h2, h3, h4 { color: #003366; }
  .stSidebar { background-color: #F4F6F8; }
</style>
""", unsafe_allow_html=True)

# ===========================
# Charger CSV depuis GitHub (RAW)
# ===========================
def load_csv_from_github(repo_base_url, file_list):
    dfs = {}
    for f in file_list:
        url = f"{repo_base_url}/{f}"
        try:
            dfs[f.replace(".csv","").lower()] = pd.read_csv(url)
        except Exception as e:
            st.error(f"❌ Erreur chargement {f} : {e}")
    return dfs

# ===========================
# Exploration graphique
# ===========================
def explore_data(df, name):
    st.markdown(f"<h2 style='color:#0066CC;'>Analyse : {name}</h2>", unsafe_allow_html=True)
    st.write("### Aperçu")
    st.dataframe(df.head())
    
    st.write("### Stats descriptives")
    st.dataframe(df.describe(include='all'))
    
    # Valeurs manquantes
    miss = df.isnull().sum()
    if miss.any():
        st.write("### Valeurs manquantes")
        st.bar_chart(miss)
    
    # Variables numériques
    num = df.select_dtypes(include=['int','float']).columns.tolist()
    if num:
        st.write("### Histogrammes")
        for col in num:
            fig, ax = plt.subplots(figsize=(5,3))
            sns.histplot(df[col], kde=True, ax=ax, color='#FF9933')
            st.pyplot(fig)

        st.write("### Boxplots")
        for col in num:
            fig, ax = plt.subplots(figsize=(5,3))
            sns.boxplot(x=df[col], ax=ax, color='#3399FF')
            st.pyplot(fig)

        if len(num) > 1:
            st.write("### Corrélations")
            fig, ax = plt.subplots(figsize=(6,4))
            sns.heatmap(df[num].corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
            st.pyplot(fig)

# ===========================
# Interface Streamlit
# ===========================
def main():
    st.markdown("<h1 style='text-align:center;color:#003366;'>Dashboard Analytique</h1>", unsafe_allow_html=True)
    st.sidebar.title("Menu")
    menu = st.sidebar.radio("Navigation", ["Données Brutes", "Données Traitées", "Exploration Graphique"])

    repo = "https://raw.githubusercontent.com/ABDOULAYEDIOP150/Rapport-de-Stage/main"
    raw_files = [
        "etudiants_annee_2021.csv", "etudiants_annee_2022.csv",
        "etudiants_annee_2023.csv", "etudiants_annee_2024.csv",
        "professeurs.csv", "gestion_enseignements.csv"
    ]
    proc_files = [
        "Dim_Temps.csv", "Etudiant_1.csv", "Fait_KPI.csv",
        "Table_Formation.csv", "Table_Inscription1.csv"
    ]

    # ================= Données brutes =================
    if menu == "Données Brutes":
        dfs = load_csv_from_github(repo, raw_files)
        st.header("Données Brutes")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))

    # ================= Données traitées =================
    elif menu == "Données Traitées":
        dfs = load_csv_from_github(repo, proc_files)
        st.header("Données Traitées")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))

    # ================= Exploration =================
    else:
        dfs = load_csv_from_github(repo, proc_files)
        st.header("Exploration Graphique")
        for name, df in dfs.items():
            with st.expander(name):
                explore_data(df, name)

if __name__ == "__main__":
    main()
