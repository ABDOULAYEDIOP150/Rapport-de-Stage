import streamlit as st
import pandas as pd
import plotly.express as px

# ===========================
# CONFIGURATION GLOBALE
# ===========================
st.set_page_config(
    page_title="📊 Dashboard Analytique HEM Dakar", 
    layout="wide",
    page_icon="📊"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #003366; font-weight: bold; text-align: center;}
    .section-header {font-size: 1.8rem; color: #0066CC; margin-top: 2rem;}
    .info-box {background-color: #F0F8FF; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;}
    .data-source {font-style: italic; color: #666; margin-bottom: 1rem;}
</style>
""", unsafe_allow_html=True)

# ===========================
# FONCTIONS UTILITAIRES
# ===========================
def load_csv_from_github(repo_base_url, file_list, sep=","):
    """
    Charge les fichiers CSV depuis GitHub et retourne un dictionnaire de DataFrames
    
    Args:
        repo_base_url (str): URL de base du dépôt GitHub
        file_list (list): Liste des noms de fichiers à charger
        sep (str): Séparateur CSV (par défaut ',')
    
    Returns:
        dict: Dictionnaire de DataFrames avec les noms de fichiers comme clés
    """
    dfs = {}
    for filename in file_list:
        url = f"{repo_base_url}/{filename}"
        try:
            df = pd.read_csv(url, sep=sep)
            # Normalisation des noms de colonnes
            df.columns = df.columns.str.strip().str.lower()
            dfs[filename.replace(".csv", "").lower()] = df
            st.sidebar.success(f"✅ {filename} chargé")
        except Exception as e:
            st.sidebar.error(f"❌ Erreur chargement {filename} : {e}")
    return dfs

def display_data_info(df, name):
    """
    Affiche des informations détaillées sur un DataFrame
    
    Args:
        df (DataFrame): DataFrame à analyser
        name (str): Nom du dataset
    """
    st.markdown(f"<div class='section-header'>📊 Dataset: {name}</div>", unsafe_allow_html=True)
    
    # Informations de base
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lignes", df.shape[0])
    with col2:
        st.metric("Colonnes", df.shape[1])
    with col3:
        st.metric("Valeurs manquantes", df.isna().sum().sum())
    
    # Aperçu des données
    with st.expander("👀 Aperçu des données"):
        st.dataframe(df.head(10))
    
    # Statistiques descriptives
    with st.expander("📊 Statistiques descriptives"):
        st.dataframe(df.describe(include='all'))
    
    # Informations sur les types de données
    with st.expander("🔍 Types de données"):
        dtype_df = pd.DataFrame({
            'Colonne': df.columns,
            'Type': df.dtypes.values,
            'Valeurs uniques': [df[col].nunique() for col in df.columns]
        })
        st.dataframe(dtype_df)

def explore_categorical_data(df, col, name):
    """
    Explore les données catégorielles avec visualisations
    
    Args:
        df (DataFrame): DataFrame source
        col (str): Colonne catégorielle à analyser
        name (str): Nom du dataset
    """
    st.markdown(f"#### 📌 Analyse de: {col}")
    
    # Répartition des valeurs
    value_counts = df[col].value_counts()
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Répartition des valeurs:**")
        st.dataframe(value_counts)
    
    with col2:
        fig = px.pie(
            values=value_counts.values, 
            names=value_counts.index,
            title=f"Répartition de {col} ({name})"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 Ce graphique circulaire montre la proportion de chaque catégorie dans la variable sélectionnée.")

def explore_numerical_data(df, col, name):
    """
    Explore les données numériques avec visualisations
    
    Args:
        df (DataFrame): DataFrame source
        col (str): Colonne numérique à analyser
        name (str): Nom du dataset
    """
    st.markdown(f"#### 📌 Analyse de: {col}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogramme
        fig_hist = px.histogram(
            df, x=col, 
            title=f"Distribution de {col}",
            color_discrete_sequence=['#FF9933'],
            nbins=20
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        st.info("💡 L'histogramme montre la distribution des valeurs et leur fréquence.")
    
    with col2:
        # Boxplot
        fig_box = px.box(
            df, y=col, 
            title=f"Boxplot de {col}",
            color_discrete_sequence=['#3399FF']
        )
        st.plotly_chart(fig_box, use_container_width=True)
        st.info("💡 Le boxplot montre la médiane, les quartiles et les valeurs aberrantes.")

def calculate_kpi_interactive(df_kpi):
    """
    Calcule et affiche les KPI de manière interactive
    
    Args:
        df_kpi (DataFrame): DataFrame contenant les indicateurs de performance
    """
    st.markdown("<div class='section-header'>💰 Indicateurs de Performance par Formation</div>", unsafe_allow_html=True)
    
    # Vérification des colonnes requises
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
    
    # Calcul des agrégations par formation
    kpi_summary = df_kpi.groupby('id_formation').agg(
        CA=('ca', 'sum'),
        Cout=('cout', 'sum'),
        Marge=('ca', 'sum') - ('cout', 'sum')
    ).reset_index()
    
    # Filtre interactif
    st.sidebar.markdown("### 🔧 Filtres KPI")
    top_n = st.sidebar.slider(
        "Nombre de formations à afficher", 
        min_value=1, 
        max_value=len(kpi_summary), 
        value=min(10, len(kpi_summary))
    
    kpi_top = kpi_summary.sort_values('CA', ascending=False).head(top_n)
    
    # Métriques globales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CA Total (millions)", f"{kpi_summary['CA'].sum():.2f}")
    with col2:
        st.metric("Coût Total (millions)", f"{kpi_summary['Cout'].sum():.2f}")
    with col3:
        marge_totale = kpi_summary['CA'].sum() - kpi_summary['Cout'].sum()
        st.metric("Marge Totale (millions)", f"{marge_totale:.2f}")
    
    # Tableau de données
    with st.expander("📋 Données détaillées"):
        st.dataframe(kpi_top)
    
    # Visualisations
    col1, col2 = st.columns(2)
    
    with col1:
        fig_ca = px.bar(
            kpi_top, x='id_formation', y='CA',
            title="💹 Chiffre d'Affaires par Formation",
            color='CA', 
            color_continuous_scale='Oranges',
            text='CA'
        )
        fig_ca.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_ca, use_container_width=True)
    
    with col2:
        fig_marge = px.bar(
            kpi_top, x='id_formation', y='Marge',
            title="📈 Marge par Formation",
            color='Marge',
            color_continuous_scale='Greens',
            text='Marge'
        )
        fig_marge.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_marge, use_container_width=True)

# ===========================
# INTERFACE PRINCIPALE
# ===========================
def main():
    # En-tête principal
    st.markdown("<div class='main-header'>📊 Tableau de Bord Analytique - HEM Dakar</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='info-box'>
    Ce tableau de bord interactif permet d'explorer les données académiques et financières de la Haute École de Management de Dakar.
    Utilisez le menu latéral pour naviguer entre les différentes sections.
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration de la barre latérale
    st.sidebar.title("📌 Navigation")
    menu = st.sidebar.radio("Sélectionnez une section:", [
        "Introduction", 
        "Données Brutes", 
        "Données Traitées", 
        "Exploration des Données", 
        "Indicateurs de Performance"
    ])
    
    # URLs des données
    repo_base = "https://raw.githubusercontent.com/ABDOULAYEDIOP150/Rapport-de-Stage/main"
    
    # Liste des fichiers
    raw_files = [
        "etudiants_annee_2021.csv", "etudiants_annee_2022.csv",
        "etudiants_annee_2023.csv", "etudiants_annee_2024.csv",
        "professeurs.csv", "gestion_enseignements.csv"
    ]
    
    processed_files = [
        "Dim_Temps.csv", "Etudiant_1.csv", "Fait_KPI.csv",
        "Table_Formation.csv", "Table_Inscription1.csv"
    ]
    
    # Section Introduction
    if menu == "Introduction":
        st.markdown("""
        ## 🎯 Contexte du Projet
        
        Ce projet s'inscrit dans le cadre de la transformation numérique de la Haute École de Management (HEM) de Dakar.
        L'objectif principal est de développer un système d'analyse des performances académiques et financières pour
        améliorer le pilotage stratégique de l'établissement.
        
        ### 📋 Objectifs Spécifiques:
        
        1. **Centralisation des données** : Intégrer les données dispersées dans plusieurs systèmes
        2. **Nettoyage et préparation** : Assurer la qualité et la cohérence des données
        3. **Création d'indicateurs** : Développer des KPIs académiques et financiers
        4. **Visualisation** : Créer des tableaux de bord interactifs pour la prise de décision
        
        ### 🔄 Processus de traitement des données:
        
        Le traitement des données suit un processus ETL (Extract, Transform, Load):
        
        1. **Extraction** : Collecte des données brutes depuis diverses sources (fichiers CSV, Excel)
        2. **Transformation** : 
           - Nettoyage (valeurs manquantes, doublons)
           - Standardisation (formats, normalisation)
           - Enrichissement (calcul d'indicateurs, création de dimensions)
        3. **Chargement** : Stockage des données transformées pour analyse
        
        ### 🛠️ Technologies utilisées:
        
        - **PySpark** : Pour le traitement distribué des données
        - **Python** : Pour l'analyse et la visualisation
        - **Power BI** : Pour les tableaux de bord avancés
        - **Streamlit** : Pour cette application interactive
        """)
    
    # Section Données Brutes
    elif menu == "Données Brutes":
        st.markdown("<div class='section-header'>📂 Données Brutes</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='info-box'>
        Cette section présente les données brutes telles qu'elles sont collectées depuis les différents systèmes sources.
        Ces données nécessitent un important travail de nettoyage et de transformation avant analyse.
        </div>
        """, unsafe_allow_html=True)
        
        # Chargement des données brutes
        raw_dfs = load_csv_from_github(repo_base, raw_files, sep=";")
        
        # Affichage des datasets
        for name, df in raw_dfs.items():
            display_data_info(df, name)
    
    # Section Données Traitées
    elif menu == "Données Traitées":
        st.markdown("<div class='section-header'>🔄 Données Traitées</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='info-box'>
        Cette section présente les données après le processus de nettoyage et de transformation. Ces données sont
        structurées selon un schéma en étoile optimisé pour l'analyse et la création d'indicateurs.
        </div>
        """, unsafe_allow_html=True)
        
        # Chargement des données traitées
        processed_dfs = load_csv_from_github(repo_base, processed_files, sep=",")
        
        # Affichage des datasets
        for name, df in processed_dfs.items():
            display_data_info(df, name)
    
    # Section Exploration des Données
    elif menu == "Exploration des Données":
        st.markdown("<div class='section-header'>🔎 Exploration des Données</div>", unsafe_allow_html=True)
        
        # Chargement des données
        processed_dfs = load_csv_from_github(repo_base, processed_files, sep=",")
        
        # Sélection du dataset
        dataset_name = st.selectbox(
            "Sélectionnez un dataset à explorer:",
            list(processed_dfs.keys())
        )
        
        df = processed_dfs[dataset_name]
        
        # Exploration des variables catégorielles
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            st.markdown("### 📊 Variables Catégorielles")
            selected_cat_col = st.selectbox(
                "Sélectionnez une variable catégorielle:",
                categorical_cols
            )
            explore_categorical_data(df, selected_cat_col, dataset_name)
        
        # Exploration des variables numériques
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        if numerical_cols:
            st.markdown("### 📈 Variables Numériques")
            selected_num_col = st.selectbox(
                "Sélectionnez une variable numérique:",
                numerical_cols
            )
            explore_numerical_data(df, selected_num_col, dataset_name)
    
    # Section Indicateurs de Performance
    elif menu == "Indicateurs de Performance":
        st.markdown("<div class='section-header'>📈 Indicateurs de Performance</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='info-box'>
        Cette section présente les indicateurs clés de performance (KPI) calculés à partir des données traitées.
        Les indicateurs incluent le chiffre d'affaires, les coûts et la marge par formation.
        </div>
        """, unsafe_allow_html=True)
        
        # Chargement des données KPI
        kpi_dfs = load_csv_from_github(repo_base, ["Fait_KPI.csv"], sep=",")
        df_kpi = kpi_dfs.get("fait_kpi")
        
        if df_kpi is not None:
            calculate_kpi_interactive(df_kpi)
        else:
            st.error("❌ Fichier Fait_KPI.csv non trouvé.")

# ===========================
# POINT D'ENTREE
# ===========================
if __name__ == "__main__":
    main()
