import streamlit as st
import pandas as pd
import plotly.express as px

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
    """Exploration interactive des données avec graphiques simples."""
    st.markdown(f"<h2 class='section-header'>📊 Analyse : {name}</h2>", unsafe_allow_html=True)
    st.info("💡 Vous pouvez explorer les distributions des variables numériques et la répartition des catégories.")
    
    # Aperçu des données
    st.write("### 👀 Aperçu des données")
    st.dataframe(df.head())

    # Statistiques descriptives
    st.write("### 📑 Statistiques descriptives")
    st.dataframe(df.describe(include='all'))

    # Variables catégorielles
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        col = st.selectbox(f"📌 Choisir une variable catégorielle ({name})", cat_cols, key=f"cat_{name}")
        if col:
            fig = px.pie(df, names=col, title=f"Répartition de {col}")
            st.plotly_chart(fig, use_container_width=True)

    # Variables numériques
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    if num_cols:
        col = st.selectbox(f"📌 Choisir une variable numérique ({name})", num_cols, key=f"num_{name}")
        if col:
            col1, col2 = st.columns(2)
            with col1:
                fig_hist = px.histogram(df, x=col, nbins=20, title=f"Distribution de {col}", color_discrete_sequence=['#FF9933'])
                st.plotly_chart(fig_hist, use_container_width=True)
                st.info("💡 Histogramme : répartition des valeurs numériques.")
            with col2:
                fig_box = px.box(df, y=col, title=f"Boxplot de {col}", color_discrete_sequence=['#3399FF'])
                st.plotly_chart(fig_box, use_container_width=True)
                st.info("💡 Boxplot : visualisation des valeurs atypiques et de la médiane.")

# ===========================
# Calcul KPI interactif
# ===========================
def calculate_kpi_interactive(df_kpi):
    """Calcul et visualisation des KPIs financiers par formation."""
    required_cols = ['id_formation', 'ca_total_millions', 'cout_total_professeur_millions']
    if not all(col in df_kpi.columns for col in required_cols):
        st.error(f"Le fichier Fait_KPI.csv doit contenir les colonnes : {required_cols}")
        st.write("Colonnes disponibles :", df_kpi.columns.tolist())
        return

    # Renommage des colonnes pour simplification
    df_kpi = df_kpi.rename(columns={'ca_total_millions': 'ca', 'cout_total_professeur_millions': 'cout'})
    
    # Somme par formation et calcul marge
    kpi_summary = df_kpi.groupby('id_formation').agg(CA=('ca','sum'), Cout=('cout','sum')).reset_index()
    kpi_summary['Marge'] = kpi_summary['CA'] - kpi_summary['Cout']

    st.markdown("<h2 class='section-header'>💰 KPI par Formation</h2>", unsafe_allow_html=True)
    st.info("💡 Les KPIs affichent le chiffre d'affaires, le coût et la marge pour chaque formation.")

    # Filtre Top N
    top_n = st.slider("Nombre de formations à afficher", min_value=1, max_value=len(kpi_summary), value=min(10,len(kpi_summary)))
    kpi_top = kpi_summary.sort_values('CA', ascending=False).head(top_n)
    st.dataframe(kpi_top)

    # Graphiques
    col1, col2 = st.columns(2)
    with col1:
        fig_ca = px.bar(kpi_top, x='id_formation', y='CA', title="💹 Chiffre d'Affaires par Formation",
                        color='CA', color_continuous_scale='Oranges', text='CA', hover_data=['Cout'])
        fig_ca.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_ca, use_container_width=True)
    with col2:
        fig_cout = px.bar(kpi_top, x='id_formation', y='Cout', title="💰 Coût par Formation",
                          color='Cout', color_continuous_scale='Blues', text='Cout', hover_data=['CA'])
        fig_cout.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_cout, use_container_width=True)

# ===========================
# Interface principale
# ===========================
def main():
    st.markdown("<h1 style='text-align:center;color:#003366;'>📊 Dashboard Analytique HEM Dakar</h1>", unsafe_allow_html=True)
    st.sidebar.title("📌 Navigation")
    menu = st.sidebar.radio("Sélectionner une section", ["Données Brutes", "Données Traitées", "Exploration Graphique", "KPI Formations"])

    repo_base = "https://raw.githubusercontent.com/ABDOULAYEDIOP150/Rapport-de-Stage/main"
    
    raw_files = [
        "etudiants_annee_2021.csv","etudiants_annee_2022.csv","etudiants_annee_2023.csv",
        "etudiants_annee_2024.csv","professeurs.csv","gestion_enseignements.csv"
    ]
    proc_files = [
        "Dim_Temps.csv","Etudiant_1.csv","Fait_KPI.csv","Table_Formation.csv","Table_Inscription1.csv"
    ]

    # ===========================
    # Données Brutes
    # ===========================
    if menu == "Données Brutes":
        st.markdown("<h2 class='section-header'>📂 Données Brutes</h2>", unsafe_allow_html=True)
        st.info("💡 Ces données représentent les fichiers originaux collectés à la HEM Dakar. Elles nécessitent un traitement avant analyse.")
        dfs = load_csv_from_github(repo_base, raw_files, sep=";")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))

    # ===========================
    # Données Traitées
    # ===========================
    elif menu == "Données Traitées":
        st.markdown("<h2 class='section-header'>🔄 Données Traitées</h2>", unsafe_allow_html=True)
        st.info("💡 Ces données ont été nettoyées, enrichies et préparées pour l'analyse et les KPI.")
        dfs = load_csv_from_github(repo_base, proc_files, sep=",")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))

    # ===========================
    # Exploration Graphique
    # ===========================
    elif menu == "Exploration Graphique":
        st.markdown("<h2 class='section-header'>🔎 Exploration Graphique</h2>", unsafe_allow_html=True)
        st.info("💡 Visualisez la distribution des variables et explorez les données de manière interactive.")
        dfs = load_csv_from_github(repo_base, proc_files, sep=",")
        for name, df in dfs.items():
            with st.expander(name):
                explore_data(df, name)

    # ===========================
    # KPI Formations
    # ===========================
    else:
        st.markdown("<h2 class='section-header'>📈 KPI Formations</h2>", unsafe_allow_html=True)
        st.info("💡 Analyse des indicateurs clés financiers par formation (CA, coût, marge).")
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
