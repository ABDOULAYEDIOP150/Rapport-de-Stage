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

    st.write("### 📑 Statistiques descriptives")
    st.dataframe(df.describe(include='all'))

    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        col = st.selectbox(f"📌 Choisir une variable catégorielle ({name})", cat_cols, key=f"cat_{name}")
        if col:
            fig = px.pie(df, names=col, title=f"Répartition de {col}")
            st.plotly_chart(fig, use_container_width=True)
            st.info("💡 Ce graphique montre la proportion de chaque catégorie.")

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
# Calcul KPI interactif
# ===========================
def calculate_kpi_interactive(df_kpi):
    required_cols = ['id_formation', 'ca_total_millions', 'cout_total_professeur_millions']
    if not all(col in df_kpi.columns for col in required_cols):
        st.error(f"Le fichier Fait_KPI.csv doit contenir les colonnes : {required_cols}")
        st.write("Colonnes disponibles :", df_kpi.columns.tolist())
        return

    # Renommer les colonnes pour simplifier
    df_kpi = df_kpi.rename(columns={
        'ca_total_millions': 'ca',
        'cout_total_professeur_millions': 'cout'
    })

    # Somme par formation
    kpi_summary = df_kpi.groupby('id_formation').agg(
        CA=('ca', 'sum'),
        Cout=('cout', 'sum')
    ).reset_index()

    st.write("### 💰 KPI par Formation")

    # Filtre interactif Top N formations
    top_n = st.slider("Nombre de formations à afficher", min_value=1, max_value=len(kpi_summary), value=len(kpi_summary))
    kpi_top = kpi_summary.sort_values('CA', ascending=False).head(top_n)

    st.dataframe(kpi_top)

    # Graphiques interactifs
    col1, col2 = st.columns(2)
    with col1:
        fig_ca = px.bar(
            kpi_top, x='id_formation', y='CA',
            title="💹 Chiffre d'Affaires par Formation",
            color='CA', color_continuous_scale='Oranges',
            text='CA', hover_data=['Cout']
        )
        fig_ca.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_ca, use_container_width=True)
    with col2:
        fig_cout = px.bar(
            kpi_top, x='id_formation', y='Cout',
            title="💰 Coût par Formation",
            color='Cout', color_continuous_scale='Blues',
            text='Cout', hover_data=['CA']
        )
        fig_cout.update_traces(texttemplate='%{text:.2f}', textposition='outside')
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
            calculate_kpi_interactive(df_kpi)
        else:
            st.error("❌ Fichier Fait_KPI.csv non trouvé.")


if __name__ == "__main__":
    main()
