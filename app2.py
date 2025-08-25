import streamlit as st
import pandas as pd
import zipfile
import matplotlib.pyplot as plt
import seaborn as sns
import os

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
# 1️⃣ Charger CSV depuis ZIP
# ===========================
def load_csv_from_zip(zip_path):
    dataframes = {}
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            for file in z.namelist():
                if file.endswith('.csv'):
                    with z.open(file) as f:
                        df = pd.read_csv(f, sep=None, engine='python')
                        name = os.path.splitext(os.path.basename(file))[0].lower()
                        dataframes[name] = df
    except Exception as e:
        st.error(f"Erreur lors du traitement de {zip_path}: {e}")
    return dataframes

# ===========================
# 2️⃣ Calcul des KPIs
# ===========================
def calculate_kpis(dataframes):
    kpi_results = {}
    if "table_inscription" in dataframes:
        df = dataframes["table_inscription"]

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
    st.info("🔍 Astuce : Explorez les distributions pour détecter des anomalies.")

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
    else:
        st.warning("Aucune colonne numérique pour générer des graphiques.")

# ===========================
# 4️⃣ Interface Streamlit
# ===========================
def main():
    st.markdown("<h1 style='text-align:center;color:#003366;'>📊 Dashboard Analytique</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#666;'>Analyse complète des données brutes et traitées avec KPIs & visualisations</p>", unsafe_allow_html=True)

    st.sidebar.title("📌 Menu Principal")
    menu = st.sidebar.radio("Navigation", ["📂 Données Brutes", "📊 Données Traitées & KPIs"])

    # =================
    # Données Brutes
    # =================
    if menu == "📂 Données Brutes":
        st.markdown("<h2 style='color:#0066CC;'>📂 Visualisation des Données Brutes</h2>", unsafe_allow_html=True)
        st.info("💡 Conseil : Uploadez votre fichier ZIP contenant les CSV bruts.")
        uploaded_zip = st.file_uploader("📁 Upload fichier ZIP des données brutes", type="zip")
        if uploaded_zip:
            dataframes = load_csv_from_zip(uploaded_zip)
            if not dataframes:
                st.warning("Aucun CSV trouvé dans le ZIP.")
            else:
                for name, df in dataframes.items():
                    with st.expander(f"📄 {name}"):
                        st.dataframe(df.head(20))

    # =================
    # Données traitées
    # =================
    elif menu == "📊 Données Traitées & KPIs":
        st.markdown("<h2 style='color:#0066CC;'>📊 Données Traitées & KPIs</h2>", unsafe_allow_html=True)
        st.info("📌 Conseil : Uploadez votre ZIP des données traitées.")
        uploaded_zip = st.file_uploader("📁 Upload fichier ZIP des données traitées", type="zip")
        if uploaded_zip:
            dataframes = load_csv_from_zip(uploaded_zip)
            if not dataframes:
                st.warning("Aucun CSV trouvé dans le ZIP.")
            else:
                st.sidebar.subheader("🔍 Sous-menu")
                sub_menu = st.sidebar.radio("Options", ["📄 Visualisation", "📈 KPIs", "📊 Exploration Graphique"])

                if sub_menu == "📄 Visualisation":
                    st.header("📂 Tables Traitées")
                    for name, df in dataframes.items():
                        with st.expander(f"📄 {name}"):
                            st.dataframe(df.head(20))

                elif sub_menu == "📈 KPIs":
                    st.header("📈 KPIs")
                    kpis = calculate_kpis(dataframes)
                    if not kpis:
                        st.warning("Aucun KPI calculé.")
                    else:
                        for kpi_name, kpi_df in kpis.items():
                            st.subheader(kpi_name)
                            st.dataframe(kpi_df)

                elif sub_menu == "📊 Exploration Graphique":
                    st.header("📊 Exploration Graphique")
                    for name, df in dataframes.items():
                        with st.expander(f"📈 Explorer {name}"):
                            explore_data(df, name)

if __name__ == "__main__":
    main()
