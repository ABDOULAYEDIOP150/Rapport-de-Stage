import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# ===========================
# Configuration globale
# ===========================
st.set_page_config(page_title="📊 Dashboard Analytique", layout="wide")
sns.set_theme(style="whitegrid")  # Style moderne pour les graphiques

# Ajout d'une police Google Fonts via CSS
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
        }
        h1, h2, h3, h4 {
            color: #003366;
        }
        .stSidebar {
            background-color: #F4F6F8;
        }
    </style>
""", unsafe_allow_html=True)

# ===========================
# 1️⃣ Fonction : Charger les fichiers CSV avec détection du séparateur
# ===========================
def load_csv_files(data_folder):
    dataframes = {}
    try:
        for file in os.listdir(data_folder):
            if file.endswith(".csv"):
                path = os.path.join(data_folder, file)
                name = os.path.splitext(file)[0].lower()
                try:
                    df = pd.read_csv(path, sep=None, engine='python')
                    dataframes[name] = df
                except Exception as e:
                    st.error(f"Erreur lors du chargement de {file}: {e}")
    except FileNotFoundError:
        st.error("❌ Le dossier spécifié n'existe pas.")
    return dataframes

# ===========================
# 2️⃣ Fonction : Calculer les KPIs
# ===========================
def calculate_kpis(dataframes):
    kpi_results = {}

    if "table_inscription" in dataframes:
        table_inscription = dataframes["table_inscription"]

        # KPI : Nombre d'étudiants par formation
        if {'id_formation', 'CODE_ETUDIANT'}.issubset(table_inscription.columns):
            nb_etudiants = table_inscription.groupby('id_formation')['CODE_ETUDIANT'].nunique().reset_index()
            nb_etudiants.columns = ['id_formation', 'Nb_Etudiants']
            kpi_results['Nombre d\'étudiants par formation'] = nb_etudiants

        # KPI : Chiffre d'affaires par formation
        if {'id_formation', 'Montant_Paye'}.issubset(table_inscription.columns):
            ca_total = table_inscription.groupby('id_formation')['Montant_Paye'].sum().reset_index()
            ca_total.columns = ['id_formation', 'CA_Total']
            kpi_results['Chiffre d\'affaires par formation'] = ca_total

        # KPI : Moyenne générale par formation
        if {'id_formation', 'MOYENNE_GENERALE'}.issubset(table_inscription.columns):
            moy_gen = table_inscription.groupby('id_formation')['MOYENNE_GENERALE'].mean().reset_index()
            moy_gen.columns = ['id_formation', 'Moyenne_Generale']
            kpi_results['Moyenne générale par formation'] = moy_gen

        # KPI : Taux de réussite (>= 10)
        if {'id_formation', 'MOYENNE_GENERALE'}.issubset(table_inscription.columns):
            total_students = table_inscription.groupby('id_formation').size().reset_index(name='Total_Inscrits')
            succeeded = table_inscription[table_inscription['MOYENNE_GENERALE'] >= 10] \
                        .groupby('id_formation').size().reset_index(name='Total_Reussis')
            taux = total_students.merge(succeeded, on='id_formation', how='left')
            taux['Total_Reussis'] = taux['Total_Reussis'].fillna(0)
            taux['Taux_Reussite_%'] = (taux['Total_Reussis'] / taux['Total_Inscrits'] * 100).round(2)
            kpi_results['Taux de réussite par formation'] = taux

    return kpi_results

# ===========================
# 3️⃣ Fonction : Exploration Graphique
# ===========================
def explore_data(df, name):
    st.markdown(f"<h2 style='color:#0066CC;'>📊 Analyse détaillée : {name}</h2>", unsafe_allow_html=True)

    st.info("🔍 **Astuce** : Explorez les distributions pour détecter des anomalies ou des valeurs extrêmes.")
    
    # Aperçu
    st.write("### 👀 Aperçu des données")
    st.dataframe(df.head())

    # Description
    st.write("### 📋 Description statistique")
    st.dataframe(df.describe(include='all'))

    # Analyse des valeurs manquantes
    missing_values = df.isnull().sum()
    if missing_values.any():
        st.write("### ⚠ Valeurs manquantes")
        st.bar_chart(missing_values)

    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    if numeric_cols:
        # Histogrammes
        st.write("### 📉 Histogrammes")
        for col in numeric_cols:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.histplot(df[col], bins=20, kde=True, ax=ax, color='#FF9933')
            ax.set_title(f"Distribution de {col}")
            st.pyplot(fig)

        # Boxplots
        st.write("### 📦 Boxplots")
        for col in numeric_cols:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.boxplot(x=df[col], ax=ax, color='#3399FF')
            ax.set_title(f"Boxplot de {col}")
            st.pyplot(fig)

        # Heatmap des corrélations
        if len(numeric_cols) > 1:
            st.write("### 🔗 Corrélation entre variables numériques")
            fig, ax = plt.subplots(figsize=(8, 6))
            corr = df[numeric_cols].corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
            ax.set_title("Matrice de corrélation")
            st.pyplot(fig)
    else:
        st.warning("Aucune colonne numérique pour générer des graphiques.")

# ===========================
# 4️⃣ Interface Streamlit
# ===========================
def main():
    st.markdown("<h1 style='text-align:center;color:#003366;'>📊 Dashboard Analytique</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#666;'>Analyse complète des données brutes et traitées avec KPIs & visualisations</p>", unsafe_allow_html=True)

    st.sidebar.title("📌 Menu Principal")
    menu_principal = st.sidebar.radio("Navigation", ["📂 Données Brutes", "📊 Données Traitées & KPIs"])

    # SECTION 1 : DONNÉES BRUTES
    if menu_principal == "📂 Données Brutes":
        st.markdown("<h2 style='color:#0066CC;'>📂 Visualisation des Données Brutes</h2>", unsafe_allow_html=True)
        st.info("💡 Conseil : Chargez les fichiers CSV bruts pour un premier aperçu des données.")
        data_folder_brut = st.text_input("📁 Chemin du dossier des données brutes :", 
                                         r"C:\Users\Abdoulaye Diop\Desktop\Projet_Data_Scientist_AtoZ\data")

        if data_folder_brut and os.path.exists(data_folder_brut):
            dataframes_brut = load_csv_files(data_folder_brut)
            if not dataframes_brut:
                st.error("⚠ Aucun fichier CSV trouvé dans ce dossier.")
            else:
                for idx, (name, df) in enumerate(dataframes_brut.items()):
                    with st.expander(f"📄 {name}"):
                        st.dataframe(df.head(20))
        else:
            st.warning("Veuillez saisir un chemin valide pour les données brutes.")

    # SECTION 2 : DONNÉES TRAITÉES & KPIs
    elif menu_principal == "📊 Données Traitées & KPIs":
        st.markdown("<h2 style='color:#0066CC;'>📊 Visualisation & KPIs des Données Traitées</h2>", unsafe_allow_html=True)
        st.info("📌 Conseil : Les données traitées sont prêtes pour l'analyse et les KPIs.")
        data_folder_traite = st.text_input("📁 Chemin du dossier des données traitées :", 
                                           r"C:\Users\Abdoulaye Diop\Desktop\Projet_Data_Scientist_AtoZ\ok_Pipeline_Data_Analyst")

        if data_folder_traite and os.path.exists(data_folder_traite):
            dataframes_traite = load_csv_files(data_folder_traite)

            if not dataframes_traite:
                st.error("⚠ Aucun fichier CSV trouvé dans ce dossier.")
            else:
                st.sidebar.subheader("🔍 Sous-menu")
                sous_menu = st.sidebar.radio("Options", ["📄 Visualisation", "📈 KPIs", "📊 Exploration Graphique"])

                if sous_menu == "📄 Visualisation":
                    st.header("📂 Tables Traitées")
                    for idx, (name, df) in enumerate(dataframes_traite.items()):
                        with st.expander(f"📄 {name}"):
                            st.dataframe(df.head(20))

                elif sous_menu == "📈 KPIs":
                    st.header("📈 Indicateurs Clés de Performance")
                    kpis = calculate_kpis(dataframes_traite)
                    if not kpis:
                        st.warning("Aucun KPI calculé. Vérifiez que vos fichiers contiennent les colonnes nécessaires.")
                    else:
                        for kpi_name, kpi_df in kpis.items():
                            st.subheader(kpi_name)
                            st.dataframe(kpi_df)

                elif sous_menu == "📊 Exploration Graphique":
                    st.header("📊 Analyse Statistique et Graphique")
                    for idx, (name, df) in enumerate(dataframes_traite.items()):
                        with st.expander(f"📈 Explorer {name}"):
                            explore_data(df, name)
        else:
            st.warning("Veuillez saisir un chemin valide pour les données traitées.")

if __name__ == "__main__":
    main()
