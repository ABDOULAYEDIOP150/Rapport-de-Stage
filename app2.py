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

# Style personnalisé
st.markdown("""
<style>
  html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
  h1, h2, h3, h4 { color: #003366; }
  .stSidebar { background-color: #F4F6F8; }
  .section-header { font-size: 1.6rem; color: #0066CC; margin-top: 1rem; }
  .info-box { background-color: #F0F8FF; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ===========================
# Résumé du projet ETL
# ===========================
def display_etl_summary():
    st.markdown("<h2 class='section-header'>📝 Résumé du Projet</h2>", unsafe_allow_html=True)
    st.info("""
    Ce projet collecte, nettoie et analyse les données de la HEM Dakar.
    **Objectif :** Transformer des données brutes en informations exploitables pour reporting et décision.
    
    **Processus ETL simplifié :**
    1. Collecte : étudiants, enseignants, cours depuis CSV.
    2. Nettoyage : suppression doublons, colonnes inutiles, harmonisation formats.
    3. Enrichissement : identifiants uniques, calcul volumes horaires et coûts.
    4. Agrégation : calcul CA, marges, taux de réussite.
    5. Modélisation : schéma en étoile pour analyse multidimensionnelle.
    """)

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
# KPI interactif avec nom de formation
# ===========================
def calculate_kpi_interactive(df_kpi, df_formation):
    # Vérification des colonnes
    required_cols = ['id_formation', 'annee_academique', 'ca_total_millions', 'cout_total_professeur_millions']
    if not all(col in df_kpi.columns for col in required_cols):
        st.error(f"Le fichier Fait_KPI.csv doit contenir les colonnes : {required_cols}")
        return
    
    # Fusion avec Table_Formation pour récupérer les noms
    df_kpi = df_kpi.merge(df_formation[['id_formation', 'formation']], on='id_formation', how='left')
    df_kpi['CA'] = df_kpi['ca_total_millions']
    df_kpi['Cout'] = df_kpi['cout_total_professeur_millions']
    df_kpi['Marge'] = df_kpi['CA'] - df_kpi['Cout']

    # Filtre année académique
    annees = st.multiselect("Sélectionner l'année académique", options=sorted(df_kpi['annee_academique'].unique()), default=[2023,2024])
    df_kpi_filtered = df_kpi[df_kpi['annee_academique'].isin(annees)]

    # Top formations par CA
    top_n = st.slider("Nombre de formations à afficher", min_value=1, max_value=len(df_kpi_filtered), value=min(10,len(df_kpi_filtered)))
    kpi_top = df_kpi_filtered.sort_values('CA', ascending=False).head(top_n)

    st.markdown("<h2 class='section-header'>💰 KPI par Formation</h2>", unsafe_allow_html=True)
    st.dataframe(kpi_top[['formation','annee_academique','CA','Cout','Marge']])

    # Graphique combiné CA, Coût, Marge
    fig = go.Figure()
    fig.add_trace(go.Bar(x=kpi_top['formation'] + " (" + kpi_top['annee_academique'].astype(str) + ")",
                         y=kpi_top['CA'], name='Chiffre d\'Affaires', marker_color='orange', text=kpi_top['CA'], textposition='auto'))
    fig.add_trace(go.Bar(x=kpi_top['formation'] + " (" + kpi_top['annee_academique'].astype(str) + ")",
                         y=kpi_top['Cout'], name='Coût', marker_color='blue', text=kpi_top['Cout'], textposition='auto'))
    fig.add_trace(go.Bar(x=kpi_top['formation'] + " (" + kpi_top['annee_academique'].astype(str) + ")",
                         y=kpi_top['Marge'], name='Marge', marker_color='green', text=kpi_top['Marge'], textposition='auto'))

    fig.update_layout(barmode='group', title="💹 KPIs par Formation et Année", xaxis_title="Formation (Année)", yaxis_title="Montants en millions", legend_title="Indicateurs")
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
    proc_files = ["Dim_Temps.csv","Etudiant_1.csv","Fait_KPI.csv","Table_Formation.csv","Table_Inscription1.csv"]

    if menu == "Résumé du Projet":
        display_etl_summary()
    elif menu == "Données Brutes":
        st.markdown("<h2 class='section-header'>📂 Données Brutes</h2>", unsafe_allow_html=True)
        dfs = load_csv_from_github(repo_base, raw_files, sep=";")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))
    elif menu == "Données Traitées":
        st.markdown("<h2 class='section-header'>🔄 Données Traitées</h2>", unsafe_allow_html=True)
        dfs = load_csv_from_github(repo_base, proc_files, sep=",")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))
    else:  # KPI Formations
        st.markdown("<h2 class='section-header'>📈 KPI Formations</h2>", unsafe_allow_html=True)
        dfs = load_csv_from_github(repo_base, ["Fait_KPI.csv","Table_Formation.csv"], sep=",")
        df_kpi = dfs.get("fait_kpi")
        df_formation = dfs.get("table_formation")
        if df_kpi is not None and df_formation is not None:
            calculate_kpi_interactive(df_kpi, df_formation)
        else:
            st.error("❌ Fichiers nécessaires non trouvés (Fait_KPI.csv et Table_Formation.csv).")

# ===========================
# Point d'entrée
# ===========================
if __name__ == "__main__":
    main()
