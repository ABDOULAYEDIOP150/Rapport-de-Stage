import streamlit as st
import pandas as pd
import plotly.express as px
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
    Ce projet consiste à collecter, nettoyer et analyser les données de la HEM Dakar.  
    **Objectif :** Transformer des données brutes en informations exploitables pour le reporting et la prise de décision.

    **Processus ETL simplifié :**
    1. **Collecte :** Données d'étudiants, enseignants et cours depuis différents fichiers CSV.
    2. **Nettoyage :**
       - Suppression des doublons et colonnes inutiles.
       - Gestion des valeurs manquantes.
       - Harmonisation des formats de dates et des libellés.
    3. **Enrichissement :**
       - Création d'identifiants uniques pour les formations.
       - Calcul des volumes horaires annuels et coûts enseignants.
    4. **Agrégation :**
       - Calcul du chiffre d'affaires, des marges et des taux de réussite par formation.
    5. **Modélisation :**
       - Schéma en étoile optimisé pour analyse multidimensionnelle.
    """)

# ===========================
# Fonction de chargement CSV
# ===========================
def load_csv_from_github(repo_base_url, file_list, sep=","):
    """Charge des fichiers CSV depuis GitHub et normalise les colonnes."""
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
# Fonction d'exploration graphique
# ===========================
def explore_data(df, name):
    st.markdown(f"<h2 class='section-header'>📊 Analyse : {name}</h2>", unsafe_allow_html=True)
    st.info("💡 Explorez la distribution des variables numériques et la répartition des catégories.")

    st.write("### 👀 Aperçu des données")
    st.dataframe(df.head())

    st.write("### 📑 Statistiques descriptives")
    st.dataframe(df.describe(include='all'))

    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        col = st.selectbox(f"📌 Variable catégorielle ({name})", cat_cols, key=f"cat_{name}")
        if col:
            fig = px.pie(df, names=col, title=f"Répartition de {col}")
            st.plotly_chart(fig, use_container_width=True)

    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    if num_cols:
        col = st.selectbox(f"📌 Variable numérique ({name})", num_cols, key=f"num_{name}")
        if col:
            col1, col2 = st.columns(2)
            with col1:
                fig_hist = px.histogram(df, x=col, nbins=20, title=f"Distribution de {col}", color_discrete_sequence=['#FF9933'])
                st.plotly_chart(fig_hist, use_container_width=True)
                st.info("Histogramme : répartition des valeurs numériques.")
            with col2:
                fig_box = px.box(df, y=col, title=f"Boxplot de {col}", color_discrete_sequence=['#3399FF'])
                st.plotly_chart(fig_box, use_container_width=True)
                st.info("Boxplot : visualisation des valeurs atypiques et de la médiane.")

# ===========================
# Calcul KPI interactif amélioré
# ===========================
def calculate_kpi_interactive(df_kpi):
    required_cols = ['id_formation', 'ca_total_millions', 'cout_total_professeur_millions']
    if not all(col in df_kpi.columns for col in required_cols):
        st.error(f"Le fichier Fait_KPI.csv doit contenir les colonnes : {required_cols}")
        return

    df_kpi = df_kpi.rename(columns={'ca_total_millions':'CA','cout_total_professeur_millions':'Cout'})
    df_kpi['Marge'] = df_kpi['CA'] - df_kpi['Cout']

    st.markdown("<h2 class='section-header'>💰 KPI par Formation</h2>", unsafe_allow_html=True)
    st.info("💡 Analyse interactive du chiffre d'affaires, coût et marge pour chaque formation.")

    top_n = st.slider("Nombre de formations à afficher", min_value=1, max_value=len(df_kpi), value=min(10,len(df_kpi)))
    kpi_top = df_kpi.sort_values('CA', ascending=False).head(top_n)
    st.dataframe(kpi_top)

    # Graphique combiné CA, Coût et Marge
    fig = go.Figure()
    fig.add_trace(go.Bar(x=kpi_top['id_formation'], y=kpi_top['CA'], name='Chiffre d\'Affaires', marker_color='orange', text=kpi_top['CA'], textposition='auto'))
    fig.add_trace(go.Bar(x=kpi_top['id_formation'], y=kpi_top['Cout'], name='Coût', marker_color='blue', text=kpi_top['Cout'], textposition='auto'))
    fig.add_trace(go.Bar(x=kpi_top['id_formation'], y=kpi_top['Marge'], name='Marge', marker_color='green', text=kpi_top['Marge'], textposition='auto'))

    fig.update_layout(barmode='group', title="💹 KPIs par Formation", xaxis_title="Formation", yaxis_title="Montants en millions", legend_title="Indicateurs")
    st.plotly_chart(fig, use_container_width=True)

# ===========================
# Interface principale
# ===========================
def main():
    st.markdown("<h1 style='text-align:center;color:#003366;'>📊 Dashboard Analytique HEM Dakar</h1>", unsafe_allow_html=True)
    st.sidebar.title("📌 Navigation")
    menu = st.sidebar.radio("Sélectionner une section", ["Résumé du Projet", "Données Brutes", "Données Traitées", "Exploration Graphique", "KPI Formations"])

    repo_base = "https://raw.githubusercontent.com/ABDOULAYEDIOP150/Rapport-de-Stage/main"
    raw_files = ["etudiants_annee_2021.csv","etudiants_annee_2022.csv","etudiants_annee_2023.csv","etudiants_annee_2024.csv","professeurs.csv","gestion_enseignements.csv"]
    proc_files = ["Dim_Temps.csv","Etudiant_1.csv","Fait_KPI.csv","Table_Formation.csv","Table_Inscription1.csv"]

    if menu == "Résumé du Projet":
        display_etl_summary()
    elif menu == "Données Brutes":
        st.markdown("<h2 class='section-header'>📂 Données Brutes</h2>", unsafe_allow_html=True)
        st.info("💡 Fichiers originaux collectés, non nettoyés.")
        dfs = load_csv_from_github(repo_base, raw_files, sep=";")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))
    elif menu == "Données Traitées":
        st.markdown("<h2 class='section-header'>🔄 Données Traitées</h2>", unsafe_allow_html=True)
        st.info("💡 Données nettoyées, enrichies et prêtes pour l'analyse.")
        dfs = load_csv_from_github(repo_base, proc_files, sep=",")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))
    elif menu == "Exploration Graphique":
        st.markdown("<h2 class='section-header'>🔎 Exploration Graphique</h2>", unsafe_allow_html=True)
        st.info("💡 Explorez graphiquement les distributions et catégories.")
        dfs = load_csv_from_github(repo_base, proc_files, sep=",")
        for name, df in dfs.items():
            with st.expander(name):
                explore_data(df, name)
    else:
        st.markdown("<h2 class='section-header'>📈 KPI Formations</h2>", unsafe_allow_html=True)
        st.info("💡 Analyse interactive des indicateurs financiers par formation.")
        dfs = load_csv_from_github(repo_base, ["Fait_KPI.csv"], sep=",")
        df_kpi = dfs.get("fait_kpi")
        if df_kpi is not None:
            calculate_kpi_interactive(df_kpi)
        else:
            st.error("❌ Fichier Fait_KPI.csv non trouvé.")

# ===========================
# Point d'entrée
# ===========================
if __name__ == "__main__":
    main()
