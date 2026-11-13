
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================================
# 1. Configuration de l'interface
# =========================================

st.set_page_config(
    page_title="SmartHeat & Plumbing",
    page_icon="🔥",
    layout="wide"
)

# =========================================
# 2. Chemin des données
# =========================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data/processed"

PRODUCTS_FILE = DATA_DIR / "products_features.csv"
RECOMMENDATIONS_FILE = DATA_DIR / "hybrid_recommendations.csv"


# =========================================
# 3. Chargement des données
# =========================================

@st.cache_data
def load_data():

    products = pd.read_csv(
        PRODUCTS_FILE,
        encoding="utf-8-sig"
    )

    recommendations = pd.read_csv(
        RECOMMENDATIONS_FILE,
        encoding="utf-8-sig"
    )

    return products, recommendations


# =========================================
# 4. Titre
# =========================================

st.title("🔥 SmartHeat & Plumbing Recommender")

st.write(
    "Système intelligent de recommandation "
    "des équipements de chauffage et plomberie."
)

st.divider()


# =========================================
# 5. Vérification des fichiers
# =========================================

if not PRODUCTS_FILE.exists():
    st.error(f"Fichier introuvable : {PRODUCTS_FILE}")
    st.stop()

if not RECOMMENDATIONS_FILE.exists():
    st.error(f"Fichier introuvable : {RECOMMENDATIONS_FILE}")
    st.stop()


# =========================================
# 6. Charger les données
# =========================================

try:
    products, recommendations = load_data()

except Exception as error:
    st.error(f"Erreur de chargement : {error}")
    st.stop()


# =========================================
# 7. Statistiques générales
# =========================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "Nombre de produits",
    len(products)
)

col2.metric(
    "Nombre de recommandations",
    len(recommendations)
)

col3.metric(
    "Produits sources",
    recommendations["source_product_id"].nunique()
    if "source_product_id" in recommendations.columns
    else 0
)

st.divider()


# =========================================
# 8. Catalogue des produits
# =========================================

st.subheader("📦 Catalogue des produits")

st.dataframe(
    products,
    use_container_width=True,
    hide_index=True
)

st.divider()


# =========================================
# 8. Recherche de produits par nom
# =========================================

st.subheader("🔎 Rechercher un produit")

if "name" not in products.columns:
    st.error("La colonne 'name' est absente du fichier products_features.csv")

elif "product_id" not in products.columns:
    st.error("La colonne 'product_id' est absente du fichier products_features.csv")

else:

    search_query = st.text_input(
        "Entrez le nom du produit :",
        placeholder="Exemple : Radiateur, chaudière, robinet..."
    )

    if search_query.strip():

        # Recherche sans tenir compte des majuscules/minuscules
        matching_products = products[
            products["name"]
            .fillna("")
            .astype(str)
            .str.contains(
                search_query.strip(),
                case=False,
                regex=False
            )
        ].drop_duplicates(subset=["product_id"])

        if matching_products.empty:

            st.warning("Aucun produit trouvé.")

        else:

            st.success(
                f"{len(matching_products)} produit(s) trouvé(s)."
            )

            # Choisir le produit recherché
            selected_product_id = st.selectbox(
                "Sélectionnez le produit :",
                matching_products["product_id"].tolist(),
                format_func=lambda pid: matching_products.loc[
                    matching_products["product_id"] == pid,
                    "name"
                ].iloc[0]
            )

            # Informations sur le produit sélectionné
            selected_product = matching_products[
                matching_products["product_id"] == selected_product_id
            ].iloc[0]

            st.markdown("### 📦 Produit sélectionné")

            st.write("**Nom :**", selected_product["name"])

            for column in ["brand", "category", "domain", "price_dzd"]:
                if column in products.columns:
                    st.write(
                        f"**{column} :**",
                        selected_product[column]
                    )

            st.divider()

            # =========================================
            # 9. Recommandations hybrides
            # =========================================

            st.subheader("🎯 Produits recommandés")

            results = recommendations[
                recommendations["source_product_id"].astype(str)
                == str(selected_product_id)
            ].copy()

            if results.empty:

                st.info(
                    "Aucune recommandation disponible pour ce produit."
                )

            else:

                results = results.sort_values(
                    by="hybrid_score",
                    ascending=False
                )

                st.success(
                    f"{len(results)} recommandation(s) trouvée(s)."
                )

                st.dataframe(
                    results,
                    use_container_width=True,
                    hide_index=True
                )

    else:

        st.info(
            "Saisissez le nom d'un produit pour obtenir ses recommandations."
        )


# =========================================
# 9. Recommandations hybrides
# =========================================

st.subheader("🎯 Recommandations hybrides")

if "source_product_id" not in recommendations.columns:
    st.error("La colonne source_product_id est absente.")
    st.stop()

product_ids = recommendations[
    "source_product_id"
].dropna().unique()

if len(product_ids) == 0:
    st.warning("Aucune recommandation disponible.")

else:
    selected_product = st.selectbox(
        "Choisir un produit de départ",
        product_ids
    )

    results = recommendations[
        recommendations["source_product_id"] == selected_product
    ].sort_values(
        "hybrid_score",
        ascending=False
    )

    st.write(
        f"Résultats pour le produit : {selected_product}"
    )

    st.dataframe(
        results,
        use_container_width=True,
        hide_index=True
    )

# =========================================
# 10. Pied de page
# =========================================

st.divider()

st.caption(
    "SmartHeat & Plumbing Recommender | "
    "Content-Based + Knowledge-Based"
)
