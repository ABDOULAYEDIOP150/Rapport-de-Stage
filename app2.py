import streamlit as st
import pandas as pd
import plotly.express as px

# ===========================
# Configuration globale
# ===========================
st.set_page_config(page_title="📊 Dashboard Analytique", layout="wide")

st.markdown("""
<style>
  html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
  h1, h2, h3, h4 { color: #003366; }
  .stSidebar { background-color: #F4F6F8; }
</style>
""", unsafe_allow_html=True)


# ===========================
# Fonction de chargement CSV
# ===========================
def load_csv_from_github(repo_base_url, file_list, sep=","):
    dfs = {}
    for f in file_list:
        url = f"{repo_base_url}/{f}"
        try:
            dfs[f.replace(".csv", "").lower()] = pd.read_csv(url, sep=sep)
        except Exception as e:
            st.error(f"❌ Erreur chargement {f} : {e}")
    return dfs


# ===========================
# Exploration graphique simple
# ===========================
def explore_data(df, name):
    st.markdown(f"<h2 style='color:#0066CC;'>📊 Analyse : {name}</h2>", unsafe_allow_html=True)
    st.write("### 👀 Aperçu des données")
    st.dataframe(df.head())

    # Statistiques descriptives simples
    st.write("### 📑 Statistiques descriptives")
    st.dataframe(df.describe(include='all'))

    # Variables catégorielles -> graphique circulaire
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        col = st.selectbox(f"📌 Choisir une variable catégorielle ({name})", cat_cols, key=f"cat_{name}")
        if col:
            fig = px.pie(df, names=col, title=f"Répartition de {col}")
            st.plotly_chart(fig, use_container_width=True)
            st.info("💡 Ce graphique montre la proportion de chaque catégorie.")

    # Variables numériques -> histogramme et boxplot
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    if num_cols:
        col = st.selectbox(f"📌 Choisir une variable numérique ({name})", num_cols, key=f"num_{name}")
        if col:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.histogram(df, x=col, nbins=20, title=f"Distribution de {col}", color_discrete_sequence=['#FF9933'])
                st.plotly_chart(fig, use_container_width=True)
                st.info("💡 L’histogramme montre la répartition des valeurs.")
            with col2:
                fig = px.box(df, y=col, title=f"Boxplot de {col}", color_discrete_sequence=['#3399FF'])
                st.plotly_chart(fig, use_container_width=True)
                st.info("💡 Le boxplot met en évidence la médiane et les valeurs atypiques (outliers).")


# ===========================
# Interface Streamlit
# ===========================
def main():
    st.markdown("<h1 style='text-align:center;color:#003366;'>📊 Dashboard Analytique</h1>", unsafe_allow_html=True)
    st.sidebar.title("📌 Menu")
    menu = st.sidebar.radio("Navigation", ["Données Brutes", "Données Traitées", "Exploration Graphique"])

    repo = "https://raw.githubusercontent.com/ABDOULAYEDIOP150/Rapport-de-Stage/main"
    
    # fichiers
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
        dfs = load_csv_from_github(repo, raw_files, sep=";")
        st.header("📂 Données Brutes")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))

    # ================= Données traitées =================
    elif menu == "Données Traitées":
        dfs = load_csv_from_github(repo, proc_files, sep=",")
        st.header("📂 Données Traitées")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))

    # ================= Exploration =================
    else:
        dfs = load_csv_from_github(repo, proc_files, sep=",")
        st.header("🔎 Exploration Graphique")
        for name, df in dfs.items():
            with st.expander(name):
                explore_data(df, name)


if __name__ == "__main__":
    main()
