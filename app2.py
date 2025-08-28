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
    dfs = {}
    for filename in file_list:
        url = f"{repo_base_url}/{filename}"
        try:
            df = pd.read_csv(url, sep=sep)
            df.columns = df.columns.str.strip().str.lower()
            dfs[filename.replace(".csv", "").lower()] = df
            st.sidebar.success(f"✅ {filename} chargé")
        except Exception as e:
            st.sidebar.error(f"❌ Erreur chargement {filename} : {e}")
    return dfs

def display_data_info(df, name):
    st.markdown(f"<div class='section-header'>📊 Dataset: {name}</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lignes", df.shape[0])
    with col2:
        st.metric("Colonnes", df.shape[1])
    with col3:
        st.metric("Valeurs manquantes", df.isna().sum().sum())
    with st.expander("👀 Aperçu des données"):
        st.dataframe(df.head(10))
    with st.expander("📊 Statistiques descriptives"):
        st.dataframe(df.describe(include='all'))
    with st.expander("🔍 Types de données"):
        dtype_df = pd.DataFrame({
            'Colonne': df.columns,
            'Type': df.dtypes.values,
            'Valeurs uniques': [df[col].nunique() for col in df.columns]
        })
        st.dataframe(dtype_df)

def explore_categorical_data(df, col, name):
    st.markdown(f"#### 📌 Analyse de: {col}")
    value_counts = df[col].value_counts()
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Répartition des valeurs:**")
        st.dataframe(value_counts)
    with col2:
        fig = px.pie(values=value_counts.values, names=value_counts.index, title=f"Répartition de {col} ({name})")
        st.plotly_chart(fig, use_container_width=True)
    st.info("💡 Ce graphique circulaire montre la proportion de chaque catégorie.")

def explore_numerical_data(df, col, name):
    st.markdown(f"#### 📌 Analyse de: {col}")
    col1, col2 = st.columns(2)
    with col1:
        fig_hist = px.histogram(df, x=col, title=f"Distribution de {col}", color_discrete_sequence=['#FF9933'], nbins=20)
        st.plotly_chart(fig_hist, use_container_width=True)
        st.info("💡 L'histogramme montre la distribution des valeurs et leur fréquence.")
    with col2:
        fig_box = px.box(df, y=col, title=f"Boxplot de {col}", color_discrete_sequence=['#3399FF'])
        st.plotly_chart(fig_box, use_container_width=True)
        st.info("💡 Le boxplot montre la médiane, les quartiles et les valeurs aberrantes.")

# ===========================
# Calcul KPI interactif
# ===========================
def calculate_kpi_interactive(df_kpi):
    st.markdown("<div class='section-header'>💰 Indicateurs de Performance par Formation</div>", unsafe_allow_html=True)
    required_cols = ['id_formation', 'ca_total_millions', 'cout_total_professeur_millions']
    if not all(col in df_kpi.columns for col in required_cols):
        st.error(f"Le fichier Fait_KPI.csv doit contenir les colonnes : {required_cols}")
        st.write("Colonnes disponibles :", df_kpi.columns.tolist())
        return
    df_kpi = df_kpi.rename(columns={
        'ca_total_millions': 'ca',
        'cout_total_professeur_millions': 'cout'
    })
    kpi_summary = df_kpi.groupby('id_formation').agg(
        CA=('ca', 'sum'),
        Cout=('cout', 'sum')
    ).reset_index()
    kpi_summary['Marge'] = kpi_summary['CA'] - kpi_summary['Cout']

    # Filtre interactif
    st.sidebar.markdown("### 🔧 Filtres KPI")
    top_n = st.sidebar.slider(
        "Nombre de formations à afficher", 
        min_value=1, 
        max_value=len(kpi_summary), 
        value=min(10, len(kpi_summary))
    )
    kpi_top = kpi_summary.sort_values('CA', ascending=False).head(top_n)

    # Métriques globales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CA Total (millions)", f"{kpi_summary['CA'].sum():.2f}")
    with col2:
        st.metric("Coût Total (millions)", f"{kpi_summary['Cout'].sum():.2f}")
    with col3:
        st.metric("Marge Totale (millions)", f"{kpi_summary['Marge'].sum():.2f}")

    # Tableau de données
    with st.expander("📋 Données détaillées"):
        st.dataframe(kpi_top)

    # Visualisations
    col1, col2 = st.columns(2)
    with col1:
        fig_ca = px.bar(kpi_top, x='id_formation', y='CA', title="💹 Chiffre d'Affaires par Formation",
                        color='CA', color_continuous_scale='Oranges', text='CA')
        fig_ca.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_ca, use_container_width=True)
    with col2:
        fig_marge = px.bar(kpi_top, x='id_formation', y='Marge', title="📈 Marge par Formation",
                           color='Marge', color_continuous_scale='Greens', text='Marge')
        fig_marge.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_marge, use_container_width=True)

# ===========================
# INTERFACE PRINCIPALE
# ===========================
def main():
    st.markdown("<div class='main-header'>📊 Tableau de Bord Analytique - HEM Dakar</div>", unsafe_allow_html=True)
    st.markdown("""<div class='info-box'>Ce tableau de bord interactif permet d'explorer les données académiques et financières de la HEM Dakar.</div>""", unsafe_allow_html=True)
    st.sidebar.title("📌 Navigation")
    menu = st.sidebar.radio("Sélectionnez une section:", [
        "Introduction", "Données Brutes", "Données Traitées", "Exploration des Données", "Indicateurs de Performance"
    ])
    repo_base = "https://raw.githubusercontent.com/ABDOULAYEDIOP150/Rapport-de-Stage/main"
    raw_files = ["etudiants_annee_2021.csv","etudiants_annee_2022.csv","etudiants_annee_2023.csv","etudiants_annee_2024.csv","professeurs.csv","gestion_enseignements.csv"]
    processed_files = ["Dim_Temps.csv","Etudiant_1.csv","Fait_KPI.csv","Table_Formation.csv","Table_Inscription1.csv"]

    if menu == "Données Brutes":
        raw_dfs = load_csv_from_github(repo_base, raw_files, sep=";")
        for name, df in raw_dfs.items():
            display_data_info(df, name)
    elif menu == "Données Traitées":
        processed_dfs = load_csv_from_github(repo_base, processed_files, sep=",")
        for name, df in processed_dfs.items():
            display_data_info(df, name)
    elif menu == "Exploration des Données":
        processed_dfs = load_csv_from_github(repo_base, processed_files, sep=",")
        dataset_name = st.selectbox("Sélectionnez un dataset à explorer:", list(processed_dfs.keys()))
        df = processed_dfs[dataset_name]
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        numerical_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()
        if categorical_cols:
            selected_cat_col = st.selectbox("Sélectionnez une variable catégorielle:", categorical_cols)
            explore_categorical_data(df, selected_cat_col, dataset_name)
        if numerical_cols:
            selected_num_col = st.selectbox("Sélectionnez une variable numérique:", numerical_cols)
            explore_numerical_data(df, selected_num_col, dataset_name)
    elif menu == "Indicateurs de Performance":
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
