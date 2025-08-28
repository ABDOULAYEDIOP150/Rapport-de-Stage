import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ===========================
# Configuration globale
# ===========================
st.set_page_config(page_title="📊 Dashboard Analytique", layout="wide")
sns.set_theme(style="whitegrid")

# CSS pour style et police
st.markdown("""
    <style>
        html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
        h1, h2, h3, h4 { color: #003366; }
        .stSidebar { background-color: #F4F6F8; }
    </style>
""", unsafe_allow_html=True)

# ===========================
# 1️⃣ Charger CSV depuis GitHub
# ===========================
def load_csv_from_github(repo_url, file_list):
    """
    repo_url : URL de base GitHub 'raw'
    file_list : liste des fichiers CSV à charger
    """
    dataframes = {}
    for file in file_list:
        try:
            url = f"{repo_url}/{file}"
            df = pd.read_csv(url)
            name = file.replace(".csv", "").lower()
            dataframes[name] = df
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement de {file} : {e}")
    return dataframes

# ===========================
# 2️⃣ Calcul des KPIs
# ===========================
def calculate_kpis(dataframes):
    kpi_results = {}
    if "table_inscription1" in dataframes:
        df = dataframes["table_inscription1"]

        if {'id_formation', 'CODE_ETUDIANT'}.issubset(df.columns):
            nb_etudiants = df.groupby('id_formation')['CODE_ETUDIANT'].nunique().reset_index()
            nb_etudiants.columns = ['id_formation', 'Nb_Etudiants']
            kpi_results["Nombre d'étudiants par formation"] = nb_etudiants

        if {'id_formation', 'Montant_Paye'}.issubset(df.columns):
            ca_total = df.groupby('id_formation')['Montant_Paye'].sum().reset_index()
            ca_total.columns = ['id_formation', 'CA_Total']
            kpi_results["Chiffre d'affaires par formation"] = ca_total

        if {'id_formation', 'MOYENNE_GENERALE'}.issubset(df.columns):
            moy_gen = df.groupby('id_formation')['MOYENNE_GENERALE'].mean().reset_index()
            moy_gen.columns = ['id_formation', 'Moyenne_Generale']
            kpi_results["Moyenne générale par formation"] = moy_gen

            total = df.groupby('id_formation').size().reset_index(name='Total_Inscrits')
            reussis = df[df['MOYENNE_GENERALE'] >= 10].groupby('id_formation').size().reset_index(name='Total_Reussis')
            taux = total.merge(reussis, on='id_formation', how='left')
            taux['Total_Reussis'] = taux['Total_Reussis'].fillna(0)
            taux['Taux_Reussite_%'] = (taux['Total_Reussis'] / taux['Total_Inscrits'] * 100).round(2)
            kpi_results["Taux de réussite par formation"] = taux
    return kpi_results

# ===========================
# 3️⃣ Exploration graphique
# ===========================
def explore_data(df, name):
    st.markdown(f"<h2 style='color:#0066CC;'>📊 Analyse : {name}</h2>", unsafe_allow_html=True)

    st.write("### 👀 Aperçu des données")
    st.dataframe(df.head())

    st.write("### 📋 Description statistique")
    st.dataframe(df.describe(include='all'))

    missing = df.isnull().sum()
    if missing.any():
        st.write("### ⚠ Valeurs manquantes")
        st.bar_chart(missing)

    numeric_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()
    if numeric_cols:
        st.write("### 📉 Histogrammes")
        for col in numeric_cols:
            fig, ax = plt.subplots(figsize=(6,4))
            sns.histplot(df[col], bins=20, kde=True, ax=ax, color='#FF9933')
            ax.set_title(f"Distribution de {col}")
            st.pyplot(fig)

        st.write("### 📦 Boxplots")
        for col in numeric_cols:
            fig, ax = plt.subplots(figsize=(6,4))
            sns.boxplot(x=df[col], ax=ax, color='#3399FF')
            ax.set_title(f"Boxplot de {col}")
            st.pyplot(fig)

        if len(numeric_cols) > 1:
            st.write("### 🔗 Corrélation")
            fig, ax = plt.subplots(figsize=(8,6))
            sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
            st.pyplot(fig)

# ===========================
# 4️⃣ Interface Streamlit
# ===========================
def main():
    st.markdown("<h1 style='text-align:center;color:#003366;'>📊 Dashboard Analytique</h1>", unsafe_allow_html=True)

    st.sidebar.title("📌 Menu Principal")
    menu = st.sidebar.radio("Navigation", ["📂 Données Brutes", "📊 Données Traitées & KPIs"])

    # Ton lien GitHub RAW (⚠️ remplace par le tien)
    repo_url = "https://raw.githubusercontent.com/ABDOULAYEDIOP150/ton_repo/main"

    # Données brutes (exemple avec étudiants/profs/enseignements)
    raw_files = [
        "etudiants_annee_2021.csv",
        "etudiants_annee_2022.csv",
        "etudiants_annee_2023.csv",
        "etudiants_annee_2024.csv",
        "professeurs.csv",
        "gestion_enseignements.csv"
    ]

    # Données traitées (les 5 tables)
    processed_files = [
        "Dim_Temps.csv",
        "Etudiant_1.csv",
        "Fait_KPI.csv",
        "Table_Formation.csv",
        "Table_Inscription1.csv"
    ]

    if menu == "📂 Données Brutes":
        dataframes = load_csv_from_github(repo_url, raw_files)
        st.header("📂 Données Brutes")
        for name, df in dataframes.items():
            with st.expander(f"📄 {name}"):
                st.dataframe(df.head(20))

    elif menu == "📊 Données Traitées & KPIs":
        dataframes = load_csv_from_github(repo_url, processed_files)
        st.header("📊 Données Traitées & KPIs")

        st.sidebar.subheader("🔍 Sous-menu")
        sub_menu = st.sidebar.radio("Options", ["📄 Visualisation", "📈 KPIs", "📊 Exploration Graphique"])

        if sub_menu == "📄 Visualisation":
            for name, df in dataframes.items():
                with st.expander(f"📄 {name}"):
                    st.dataframe(df.head(20))

        elif sub_menu == "📈 KPIs":
            kpis = calculate_kpis(dataframes)
            if not kpis:
                st.warning("Aucun KPI calculé.")
            else:
                for kpi_name, kpi_df in kpis.items():
                    st.subheader(kpi_name)
                    st.dataframe(kpi_df)

        elif sub_menu == "📊 Exploration Graphique":
            for name, df in dataframes.items():
                with st.expander(f"📈 Explorer {name}"):
                    explore_data(df, name)

if __name__ == "__main__":
    main()
