import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ===========================
# Configuration globale
# ===========================
st.set_page_config(
    page_title="📊 Dashboard Analytique HEM Dakar",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
<style>
  html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
  h1, h2, h3, h4 { color: #003366; }
  .stSidebar { background-color: #F4F6F8; }
  .section-header { font-size: 1.6rem; color: #0066CC; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ===========================
# Chargement CSV
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
# KPI avec ID formation lisible
# ===========================
def calculate_kpi_with_id(df_kpi, df_formation, year_selected):
    required_kpi_cols = ['id_formation', 'annee_academique', 'ca_total_millions', 'cout_total_professeur_millions']
    if not all(col in df_kpi.columns for col in required_kpi_cols):
        st.error(f"Le fichier Fait_KPI.csv doit contenir : {required_kpi_cols}")
        return

    # Filtrer par année académique
    df_kpi_year = df_kpi[df_kpi['annee_academique'] == year_selected]

    # Jointure avec Table_Formation pour récupérer nom de formation et niveau
    df_kpi_year = df_kpi_year.merge(df_formation[['id_formation', 'formation', 'niveau']], on='id_formation', how='left')

    # Création de l'ID lisible : Libellé_Année_Niveau
    df_kpi_year['ID_Formation'] = df_kpi_year.apply(lambda x: f"{x['formation']}_{x['annee_academique']}_{x['niveau']}", axis=1)

    # Calcul des indicateurs
    df_kpi_year['CA'] = df_kpi_year['ca_total_millions']
    df_kpi_year['Cout'] = df_kpi_year['cout_total_professeur_millions']
    df_kpi_year['Marge'] = df_kpi_year['CA'] - df_kpi_year['Cout']

    # Top N formations
    top_n = st.slider("Nombre de formations à afficher", min_value=1, max_value=len(df_kpi_year), value=min(10,len(df_kpi_year)))
    df_top = df_kpi_year.sort_values('CA', ascending=False).head(top_n)

    st.markdown(f"<h2 class='section-header'>💰 KPI par Formation - Année {year_selected}</h2>", unsafe_allow_html=True)
    st.dataframe(df_top[['ID_Formation','CA','Cout','Marge']])

    # Graphique combiné
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_top['ID_Formation'], y=df_top['CA'], name='Chiffre d\'Affaires', marker_color='orange', text=df_top['CA'], textposition='auto'))
    fig.add_trace(go.Bar(x=df_top['ID_Formation'], y=df_top['Cout'], name='Coût', marker_color='blue', text=df_top['Cout'], textposition='auto'))
    fig.add_trace(go.Bar(x=df_top['ID_Formation'], y=df_top['Marge'], name='Marge', marker_color='green', text=df_top['Marge'], textposition='auto'))

    fig.update_layout(barmode='group', title=f"💹 KPIs par Formation - Année {year_selected}", xaxis_title="Formation", yaxis_title="Montants en millions", legend_title="Indicateurs")
    st.plotly_chart(fig, use_container_width=True)

# ===========================
# Interface principale
# ===========================
def main():
    st.markdown("<h1 style='text-align:center;color:#003366;'>📊 Dashboard Analytique HEM Dakar</h1>", unsafe_allow_html=True)
    st.sidebar.title("📌 Navigation")
    menu = st.sidebar.radio("Sélectionner une section", ["Résumé du Projet", "Données Brutes", "Données Traitées", "KPI Formations"])

    repo_base = "https://raw.githubusercontent.com/ABDOULAYEDIOP150/Rapport-de-Stage/main"
    raw_files = ["etudiants_annee_2021.csv","etudiants_annee_2022.csv","etudiants_annee_2023.csv","etudiants_annee_2024.csv","professeurs.csv","gestion_enseignements.csv"]
    proc_files = ["Fait_KPI.csv","Table_Formation.csv"]

    if menu == "Résumé du Projet":
        st.info("Projet ETL : collecte, nettoyage, enrichissement et analyse des données de la HEM Dakar.")
    elif menu == "Données Brutes":
        dfs = load_csv_from_github(repo_base, raw_files, sep=";")
        st.markdown("### 📂 Données Brutes")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))
    elif menu == "Données Traitées":
        dfs = load_csv_from_github(repo_base, proc_files, sep=",")
        st.markdown("### 🔄 Données Traitées")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))
    else:  # KPI Formations
        dfs = load_csv_from_github(repo_base, proc_files, sep=",")
        df_kpi = dfs.get("fait_kpi")
        df_formation = dfs.get("table_formation")
        if df_kpi is not None and df_formation is not None:
            year_selected = st.radio("Choisir l'année académique pour l'analyse", [2023, 2024], index=1)
            calculate_kpi_with_id(df_kpi, df_formation, year_selected)
        else:
            st.error("❌ Fichiers nécessaires non trouvés (Fait_KPI.csv et Table_Formation.csv).")

# ===========================
# Point d'entrée
# ===========================
if __name__ == "__main__":
    main()
