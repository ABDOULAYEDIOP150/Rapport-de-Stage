import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ===========================
# Configuration globale
# ===========================
st.set_page_config(page_title="📊 Dashboard Analytique", layout="wide")
sns.set_theme(style="whitegrid")

st.markdown("""
<style>
  html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
  h1, h2, h3, h4 { color: #003366; }
  .stSidebar { background-color: #F4F6F8; }
</style>
""", unsafe_allow_html=True)

# ===========================
# ​​​ Charger CSV depuis GitHub (RAW)
# ===========================
def load_csv_from_github(repo_base_url, file_list):
    dfs = {}
    for f in file_list:
        url = f"{repo_base_url}/{f}"
        try:
            dfs[f.replace(".csv","").lower()] = pd.read_csv(url)
        except Exception as e:
            st.error(f"❌ Erreur chargement {f} : {e}")
    return dfs

# ===========================
# ​​​ Calcul des KPIs
# (identique à ton code précédent)
# ===========================
def calculate_kpis(dfs):
    kpis = {}
    if "table_inscription1" in dfs:
        df = dfs["table_inscription1"]
        if {'id_formation','CODE_ETUDIANT'}.issubset(df.columns):
            nb = df.groupby('id_formation')['CODE_ETUDIANT'].nunique().reset_index()
            nb.columns = ['id_formation','Nb_Etudiants']
            kpis["Étudiants par formation"] = nb
        if {'id_formation','Montant_Paye'}.issubset(df.columns):
            ca = df.groupby('id_formation')['Montant_Paye'].sum().reset_index()
            ca.columns = ['id_formation','CA_Total']
            kpis["Chiffre d'affaires"] = ca
        if {'id_formation','MOYENNE_GENERALE'}.issubset(df.columns):
            mg = df.groupby('id_formation')['MOYENNE_GENERALE'].mean().reset_index()
            mg.columns = ['id_formation','Moyenne_Generale']
            kpis["Moyenne générale"] = mg
            total = df.groupby('id_formation').size().reset_index(name='Total_Inscrits')
            reussis = df[df['MOYENNE_GENERALE']>=10].groupby('id_formation').size().reset_index(name='Total_Reussis')
            taux = total.merge(reussis, on='id_formation', how='left').fillna(0)
            taux['Taux_Reussite_%'] = (taux['Total_Reussis']/taux['Total_Inscrits']*100).round(2)
            kpis["Taux de réussite (%)"] = taux
    return kpis

# ===========================
# ​​​ Exploration graphique
# (idem que précédemment)
# ===========================
def explore_data(df, name):
    st.markdown(f"<h2 style='color:#0066CC;'>Analyse : {name}</h2>", unsafe_allow_html=True)
    st.write("### Aperçu")
    st.dataframe(df.head())
    st.write("### Stats descriptives")
    st.dataframe(df.describe(include='all'))
    miss = df.isnull().sum()
    if miss.any():
        st.write("### Valeurs manquantes")
        st.bar_chart(miss)
    num = df.select_dtypes(include=['int','float']).columns.tolist()
    if num:
        st.write("### Histogrammes")
        for col in num:
            fig, ax = plt.subplots(figsize=(5,3))
            sns.histplot(df[col], kde=True, ax=ax, color='#FF9933')
            st.pyplot(fig)
        st.write("### Boxplots")
        for col in num:
            fig, ax = plt.subplots(figsize=(5,3))
            sns.boxplot(x=df[col], ax=ax, color='#3399FF')
            st.pyplot(fig)
        if len(num)>1:
            st.write("### Corrélations")
            fig, ax = plt.subplots(figsize=(6,4))
            sns.heatmap(df[num].corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
            st.pyplot(fig)

# ===========================
# ​​​ Interface Streamlit
# ===========================
def main():
    st.markdown("<h1 style='text-align:center;color:#003366;'>Dashboard Analytique</h1>", unsafe_allow_html=True)
    st.sidebar.title("Menu")
    menu = st.sidebar.radio("Navigation", ["Données Brutes", "Données Traitées & KPIs"])

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
        dfs = load_csv_from_github(repo, raw_files)
        st.header("Données Brutes")
        for name, df in dfs.items():
            with st.expander(name):
                st.dataframe(df.head(20))

    else:
        dfs = load_csv_from_github(repo, proc_files)
        st.header("Données Traitées & KPIs")
        sub = st.sidebar.radio("Options", ["Visualisation", "KPIs", "Exploration Graphique"])
        if sub == "Visualisation":
            for name, df in dfs.items():
                with st.expander(name):
                    st.dataframe(df.head(20))
        elif sub == "KPIs":
            kpis = calculate_kpis(dfs)
            if not kpis:
                st.warning("Aucun KPI calculé")
            else:
                for title, df in kpis.items():
                    st.subheader(title)
                    st.dataframe(df)
        else:
            for name, df in dfs.items():
                with st.expander(name):
                    explore_data(df, name)

if __name__ == "__main__":
    main()
