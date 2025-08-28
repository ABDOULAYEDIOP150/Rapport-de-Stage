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
            df = pd.read_csv(url, sep=sep)
            # Nettoyer les noms de colonnes
            df.columns = df.columns.str.strip().str.lower()
            dfs[f.replace(".csv", "").lower()] = df
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
# Calcul CA et Coût par Formation
# ===========================
def calculate_kpi(df_kpi):
    # Vérifier les colonnes essentielles
    required_cols = ['annee', 'id_formation', 'ca', 'cout']
    if not all(col in df_kpi.columns for col in required_cols):
        st.error(f"Le fichier Fait_KPI.csv doit contenir les colonnes : {required_cols}")
        st.write("Colonnes disponibles :", df_kpi.columns.tolist())
        return

    # Filtrer à partir de l'année 2023
    df_kpi = df_kpi[df_kpi['annee'] >= 2023]

    # Calcul du CA et du coût par formation
    kpi_summary = df_kpi.groupby(['id_formation', 'annee']).agg(
        CA=('ca', 'sum'),
        Cout=('cout', 'sum')
    ).reset_index()

    st.write("### 💰 Chiffre d'affaires et Coût par formation")
    st.dataframe(kpi_summary)

    # Graphiques interactifs
    fig_ca = px.bar(kpi_summary, x='id_formation', y='CA', color='annee', barmode='group', title="CA par formation")
    fig_cout = px.bar(kpi_summary, x='id_formation', y='Cout', color='annee', barmode='group', title="Coût par formation")
    
    st.plotly_chart(fig_ca, use_container_width=True)
    st.plotly_chart(fig_cout, use_container_width=True)

# ===========================
# Interface Streamlit
# ===========================
def main():
    st.markdown("<h1 style='text-align:center;color:#003366;'>📊 Dashboard Analytique</h1>", unsafe_allow_html=True)
    st.sidebar.title("📌 Menu")
    menu = st.sidebar.radio("Navigation", ["Données Brutes", "Données Traitées", "Exploration Graphique", "KPI Formations"])

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

    if menu == "Données Brutes":
        dfs = load_csv_from_github(repo, raw_files, sep=";")
        st.header("📂 Données Brutes")
        for name, df in dfs.items():
            with st.expander(name):
                st.button(f"Lignes : {df.shape[0]}", key=f"btn_{name}")
                st.dataframe(df.head(20))

    elif menu == "Données Traitées":
        dfs = load_csv_from_github(repo, proc_files, sep=",")
        st.header("📂 Données Traitées")
        for name, df in dfs.items():
            with st.expander(name):
                st.button(f"Lignes : {df.shape[0]}", key=f"btn_{name}")
                st.dataframe(df.head(20))

    elif menu == "Exploration Graphique":
        dfs = load_csv_from_github(repo, proc_files, sep=",")
        st.header("🔎 Exploration Graphique")
        for name, df in dfs.items():
            with st.expander(name):
                explore_data(df, name)

    else:  # KPI Formations
        dfs = load_csv_from_github(repo, ["Fait_KPI.csv"], sep=",")
        df_kpi = dfs.get("fait_kpi")
        if df_kpi is not None:
            calculate_kpi(df_kpi)
        else:
            st.error("❌ Fichier Fait_KPI.csv non trouvé.")


if __name__ == "__main__":
    main()
