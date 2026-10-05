"""
Simulateur Streamlit – Segmentation RFM GlobalShop Direct
Mission NexaData Consulting – Binôme : Suz & Laurie

Lancement :
    streamlit run app.py
"""

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------
# Configuration de la page
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Simulateur RFM – GlobalShop Direct",
    page_icon="🛍️",
    layout="wide",
)

# ---------------------------------------------------------------
# Identité visuelle et contenu métier des segments
# ---------------------------------------------------------------
ORDRE_SEGMENTS = ["Champions", "Clients fidèles", "Nouveaux clients", "Clients perdus"]

SEGMENTS = {
    "Champions": {
        "icone": "workspace_premium",
        "couleur": "#16A34A",
        "fond": "#F0FDF4",
        "accroche": "Achètent souvent, beaucoup et récemment",
        "objectif": "Retenir et récompenser",
        "priorite": "Priorité 1",
        "actions": [
            ("diamond", "Programme VIP et avantages exclusifs"),
            ("new_releases", "Accès en avant-première aux nouveautés"),
            ("mail", "Remerciements et offres personnalisés"),
        ],
    },
    "Clients fidèles": {
        "icone": "favorite",
        "couleur": "#2563EB",
        "fond": "#EFF6FF",
        "accroche": "Achètent régulièrement, panier intermédiaire",
        "objectif": "Faire monter en gamme",
        "priorite": "Priorité 2",
        "actions": [
            ("stairs", "Programme de fidélité à paliers"),
            ("add_shopping_cart", "Recommandations de produits complémentaires"),
            ("schedule", "Relance avant 60 jours sans achat"),
        ],
    },
    "Nouveaux clients": {
        "icone": "eco",
        "couleur": "#D97706",
        "fond": "#FFFBEB",
        "accroche": "Achat récent, encore peu de commandes",
        "objectif": "Déclencher le réachat",
        "priorite": "Priorité 3",
        "actions": [
            ("waving_hand", "Parcours de bienvenue par e-mail"),
            ("sell", "Code promo sur la 2e commande"),
            ("explore", "Découverte guidée du catalogue"),
        ],
    },
    "Clients perdus": {
        "icone": "bedtime",
        "couleur": "#DC2626",
        "fond": "#FEF2F2",
        "accroche": "Inactifs depuis environ 6 mois, souvent 1 seule commande",
        "objectif": "Réactiver à moindre coût",
        "priorite": "Priorité 4",
        "actions": [
            ("campaign", "Campagne « Vous nous manquez »"),
            ("percent", "Remise de réactivation limitée dans le temps"),
            ("savings", "Budget limité, mesurer le retour avant d'investir"),
        ],
    },
}

# Profils prêts à l'emploi pour la démonstration
EXEMPLES = {
    "Champion": (5, 15, 6000.0),
    "Fidèle": (50, 4, 1300.0),
    "Nouveau": (15, 1, 400.0),
    "Perdu": (200, 1, 250.0),
}

# Déclare la page en français : évite que Chrome la « traduise » et casse les icônes
components.html(
    """<script>
    const doc = window.parent.document;
    doc.documentElement.lang = "fr";
    doc.documentElement.setAttribute("translate", "no");
    if (!doc.querySelector('meta[name="google"]')) {
        const meta = doc.createElement("meta");
        meta.name = "google";
        meta.content = "notranslate";
        doc.head.appendChild(meta);
    }
    </script>""",
    height=0,
)

# ---------------------------------------------------------------
# Style CSS
# ---------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,500,1,0');

    html, body, [class*="css"], .stMarkdown, .stNumberInput label {
        font-family: 'Inter', sans-serif;
    }
    .stApp { background: #F5F7FB; }
    .block-container { padding-top: 3.5rem; max-width: 1250px; }

    .ms {
        font-family: 'Material Symbols Rounded';
        font-weight: normal; font-style: normal; line-height: 1;
        display: inline-block; vertical-align: middle;
        -webkit-font-feature-settings: 'liga'; font-feature-settings: 'liga';
    }

    /* Bandeau d'en-tête */
    .hero {
        background: linear-gradient(120deg, #0F172A 0%, #1E3A8A 60%, #2563EB 100%);
        color: white; border-radius: 18px; padding: 28px 32px; margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, .18);
    }
    .hero h1 { color: white; font-size: 2rem; font-weight: 800; margin: 0 0 6px 0; padding: 0; }
    .hero p { color: #CBD5E1; margin: 0 0 14px 0; font-size: 1rem; }
    .badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.25);
        color: white; border-radius: 999px; padding: 5px 12px; margin: 0 6px 6px 0;
        font-size: .82rem; font-weight: 500;
    }
    .badge .ms { font-size: 18px; }

    /* Titres de section */
    .section {
        display: flex; align-items: center; gap: 10px;
        font-size: 1.25rem; font-weight: 700; color: #0F172A; margin: 18px 0 12px 0;
    }
    .section .ms { color: #2563EB; font-size: 26px; }

    /* Cartes KPI */
    .kpi {
        background: white; border-radius: 14px; padding: 18px 20px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, .06); border: 1px solid #E2E8F0;
        display: flex; align-items: center; gap: 16px;
    }
    .kpi-icone {
        width: 48px; height: 48px; border-radius: 12px; display: flex;
        align-items: center; justify-content: center; background: #EFF6FF; color: #2563EB;
    }
    .kpi-icone .ms { font-size: 28px; }
    .kpi-label { color: #64748B; font-size: .85rem; font-weight: 500; }
    .kpi-valeur { color: #0F172A; font-size: 1.55rem; font-weight: 800; line-height: 1.2; }

    /* Cartes profils */
    .profil {
        background: white; border-radius: 14px; padding: 18px; height: 100%;
        box-shadow: 0 2px 10px rgba(15, 23, 42, .06); border: 1px solid #E2E8F0;
        border-top: 5px solid var(--c);
    }
    .profil-tete { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
    .profil-icone {
        width: 40px; height: 40px; border-radius: 10px; display: flex;
        align-items: center; justify-content: center; background: var(--f); color: var(--c);
    }
    .profil-nom { font-weight: 700; font-size: 1.05rem; color: #0F172A; }
    .profil-accroche { color: #64748B; font-size: .82rem; min-height: 38px; margin: 6px 0 10px 0; }
    .profil-chiffres { display: flex; gap: 10px; margin-bottom: 10px; }
    .chiffre { flex: 1; background: var(--f); border-radius: 10px; padding: 8px 10px; }
    .chiffre-valeur { font-size: 1.35rem; font-weight: 800; color: var(--c); }
    .chiffre-label { font-size: .72rem; color: #475569; }
    .chips { display: flex; flex-wrap: wrap; gap: 6px; }
    .chip {
        display: inline-flex; align-items: center; gap: 4px; font-size: .74rem;
        background: #F1F5F9; color: #334155; border-radius: 999px; padding: 3px 9px;
    }
    .chip .ms { font-size: 15px; }

    /* Résultat du simulateur */
    .resultat {
        background: var(--f); border: 2px solid var(--c); border-radius: 16px; padding: 22px 24px;
    }
    .resultat-tete { display: flex; align-items: center; gap: 14px; }
    .resultat-icone {
        width: 60px; height: 60px; border-radius: 14px; background: var(--c); color: white;
        display: flex; align-items: center; justify-content: center;
    }
    .resultat-icone .ms { font-size: 36px; }
    .resultat-sur { color: #475569; font-size: .8rem; font-weight: 600;
                    text-transform: uppercase; letter-spacing: .06em; }
    .resultat-nom { color: var(--c); font-size: 1.8rem; font-weight: 800; line-height: 1.1; }
    .priorite {
        display: inline-block; background: var(--c); color: white; border-radius: 999px;
        padding: 3px 10px; font-size: .75rem; font-weight: 600; margin-left: 6px;
    }
    .objectif { margin: 14px 0 8px 0; color: #0F172A; font-weight: 600; }
    .action {
        display: flex; align-items: center; gap: 10px; background: white;
        border-radius: 10px; padding: 9px 12px; margin-bottom: 7px; color: #1E293B;
        font-size: .92rem; border: 1px solid #E2E8F0;
    }
    .action .ms { color: var(--c); font-size: 22px; }

    /* Comparaison et proximité */
    .comp {
        background: white; border-radius: 12px; padding: 12px 14px; border: 1px solid #E2E8F0;
        text-align: center;
    }
    .comp-label { color: #64748B; font-size: .78rem; font-weight: 500; }
    .comp-valeur { color: #0F172A; font-size: 1.3rem; font-weight: 800; }
    .comp-ref { color: #64748B; font-size: .75rem; }
    .barre-ligne { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: .85rem; }
    .barre-nom { width: 130px; color: #334155; font-weight: 500; }
    .barre-fond { flex: 1; background: #E2E8F0; border-radius: 999px; height: 10px; overflow: hidden; }
    .barre-plein { height: 10px; border-radius: 999px; }
    .barre-val { width: 44px; text-align: right; color: #0F172A; font-weight: 700; }

    .pied { color: #94A3B8; font-size: .8rem; text-align: center; margin-top: 30px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def icone(nom, taille=None):
    """Renvoie le HTML d'une icône Material Symbols."""
    style = f' style="font-size:{taille}px"' if taille else ""
    return f'<span class="ms notranslate" translate="no"{style}>{nom}</span>'


def section(nom_icone, titre):
    """Affiche un titre de section avec son icône."""
    st.markdown(f'<div class="section">{icone(nom_icone)} {titre}</div>',
                unsafe_allow_html=True)


def nombre(valeur, decimales=0):
    """Formate un nombre à la française (espace comme séparateur de milliers)."""
    return f"{valeur:,.{decimales}f}".replace(",", " ").replace(".", ",")


# ---------------------------------------------------------------
# Chargement des modèles et des données (mis en cache)
# ---------------------------------------------------------------
@st.cache_resource
def charger_modeles():
    """Charge le scaler, le K-means et la correspondance cluster → segment."""
    scaler = joblib.load("models/scaler.pkl")
    kmeans = joblib.load("models/kmeans.pkl")
    noms_segments = joblib.load("models/noms_segments.pkl")
    return scaler, kmeans, noms_segments


@st.cache_data
def charger_donnees():
    """Charge la table RFM finale (un client par ligne, avec son segment)."""
    return pd.read_csv("models/rfm_segments.csv", index_col="CustomerID")


scaler, kmeans, noms_segments = charger_modeles()
rfm = charger_donnees()


def predire_segment(recence, frequence, montant):
    """Applique le même prétraitement que le notebook (log1p + standardisation),
    prédit le segment et calcule la proximité avec chaque segment."""
    client = pd.DataFrame({"Recency": [recence],
                           "Frequency": [frequence],
                           "Monetary": [montant]})
    client_scaled = pd.DataFrame(scaler.transform(np.log1p(client)), columns=client.columns)
    cluster = int(kmeans.predict(client_scaled)[0])

    # Proximité : inverse de la distance aux centres des clusters, normalisée à 100 %
    distances = kmeans.transform(client_scaled)[0]
    similarite = 1 / (distances + 1e-6)
    proximite = {noms_segments[i]: s / similarite.sum() for i, s in enumerate(similarite)}
    return noms_segments[cluster], proximite


# ---------------------------------------------------------------
# 1. En-tête
# ---------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <h1>{icone("insights", 34)} Simulateur de segmentation client</h1>
        <p>GlobalShop Direct · Qualifiez un client en quelques secondes et obtenez
        l'action marketing adaptée à son profil.</p>
        <span class="badge">{icone("hub")} K-means · 4 segments</span>
        <span class="badge">{icone("query_stats")} Modèle RFM (Récence, Fréquence, Montant)</span>
        <span class="badge">{icone("calendar_month")} Déc. 2010 → déc. 2011</span>
        <span class="badge">{icone("business_center")} NexaData Consulting</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# 2. KPI clés
# ---------------------------------------------------------------
ca_total = rfm["Monetary"].sum()
kpis = [
    ("groups", "Clients analysés", nombre(len(rfm))),
    ("payments", "Chiffre d'affaires", f"{nombre(ca_total / 1e6, 2)} M£"),
    ("shopping_cart", "Panier moyen", f"{nombre(ca_total / rfm['Frequency'].sum())} £"),
    ("hourglass_bottom", "Inactifs > 90 jours", f"{(rfm['Recency'] > 90).mean():.0%}"),
]
for col, (ic, label, valeur) in zip(st.columns(4), kpis):
    col.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-icone">{icone(ic)}</div>
            <div><div class="kpi-label">{label}</div><div class="kpi-valeur">{valeur}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# 3. Résumé des profils
# ---------------------------------------------------------------
section("diversity_3", "Nos 4 profils clients")
for col, nom in zip(st.columns(4), ORDRE_SEGMENTS):
    seg = SEGMENTS[nom]
    donnees = rfm[rfm["Segment"] == nom]
    col.markdown(
        f"""
        <div class="profil" style="--c:{seg['couleur']}; --f:{seg['fond']};">
            <div class="profil-tete">
                <div class="profil-icone">{icone(seg['icone'])}</div>
                <div class="profil-nom">{nom}</div>
            </div>
            <div class="profil-accroche">{seg['accroche']}</div>
            <div class="profil-chiffres">
                <div class="chiffre">
                    <div class="chiffre-valeur">{len(donnees) / len(rfm):.0%}</div>
                    <div class="chiffre-label">des clients</div>
                </div>
                <div class="chiffre">
                    <div class="chiffre-valeur">{donnees['Monetary'].sum() / ca_total:.0%}</div>
                    <div class="chiffre-label">du CA</div>
                </div>
            </div>
            <div class="chips">
                <span class="chip">{icone("history")} {donnees['Recency'].median():.0f} j</span>
                <span class="chip">{icone("repeat")} {donnees['Frequency'].median():.0f} cmd</span>
                <span class="chip">{icone("currency_pound")} {nombre(donnees['Monetary'].median())} £</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# 4. Simulateur
# ---------------------------------------------------------------
section("person_search", "Qualifier un client")

# Valeurs par défaut des champs de saisie
for cle, valeur in zip(["recence", "frequence", "montant"], (30, 3, 800.0)):
    st.session_state.setdefault(cle, valeur)


def charger_exemple(nom):
    """Remplit les champs avec un profil d'exemple."""
    r, f, m = EXEMPLES[nom]
    st.session_state.recence, st.session_state.frequence, st.session_state.montant = r, f, m


col_saisie, col_resultat = st.columns([2, 3], gap="large")

with col_saisie:
    with st.container(border=True):
        st.markdown("**Profil RFM du client**")
        st.number_input(":material/history: Récence — jours depuis le dernier achat",
                        min_value=1, max_value=400, step=1, key="recence")
        st.number_input(":material/repeat: Fréquence — nombre de commandes",
                        min_value=1, max_value=250, step=1, key="frequence")
        st.number_input(":material/payments: Montant — total dépensé (£)",
                        min_value=1.0, max_value=300000.0, step=50.0, key="montant")

        st.caption("Ou chargez un profil d'exemple :")
        icones_exemples = [":material/workspace_premium:", ":material/favorite:",
                           ":material/eco:", ":material/bedtime:"]
        boutons = st.columns(2) + st.columns(2)
        for bouton, nom, ic in zip(boutons, EXEMPLES, icones_exemples):
            bouton.button(nom, icon=ic, on_click=charger_exemple, args=(nom,),
                          width="stretch")

segment, proximite = predire_segment(st.session_state.recence,
                                     st.session_state.frequence,
                                     st.session_state.montant)
seg = SEGMENTS[segment]

with col_resultat:
    actions_html = "".join(
        f'<div class="action">{icone(ic)} {texte}</div>' for ic, texte in seg["actions"]
    )
    st.markdown(
        f"""
        <div class="resultat" style="--c:{seg['couleur']}; --f:{seg['fond']};">
            <div class="resultat-tete">
                <div class="resultat-icone">{icone(seg['icone'])}</div>
                <div>
                    <div class="resultat-sur">Segment attribué</div>
                    <div class="resultat-nom">{segment}<span class="priorite">{seg['priorite']}</span></div>
                </div>
            </div>
            <div class="objectif">{icone("flag", 20)} Objectif : {seg['objectif']}</div>
            {actions_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Comparaison avec le client type et proximité des segments ---
col_comp, col_prox = st.columns([3, 2], gap="large")

with col_comp:
    section("compare_arrows", f"Comparaison avec le client type « {segment} »")
    medianes = rfm.loc[rfm["Segment"] == segment, ["Recency", "Frequency", "Monetary"]].median()
    comparaisons = [
        ("Récence", f"{st.session_state.recence} j", f"{medianes['Recency']:.0f} j"),
        ("Fréquence", f"{st.session_state.frequence} cmd", f"{medianes['Frequency']:.0f} cmd"),
        ("Montant", f"{nombre(st.session_state.montant)} £", f"{nombre(medianes['Monetary'])} £"),
    ]
    for col, (label, val_client, val_ref) in zip(st.columns(3), comparaisons):
        col.markdown(
            f"""
            <div class="comp">
                <div class="comp-label">{label}</div>
                <div class="comp-valeur">{val_client}</div>
                <div class="comp-ref">médiane du segment : {val_ref}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_prox:
    section("radar", "Proximité avec chaque segment")
    barres = "".join(
        f"""
        <div class="barre-ligne">
            <div class="barre-nom">{nom}</div>
            <div class="barre-fond">
                <div class="barre-plein" style="width:{proximite[nom]:.0%};
                     background:{SEGMENTS[nom]['couleur']};"></div>
            </div>
            <div class="barre-val">{proximite[nom]:.0%}</div>
        </div>
        """
        for nom in ORDRE_SEGMENTS
    )
    st.markdown(barres, unsafe_allow_html=True)
    st.caption("Calculée à partir de la distance du client au centre de chaque segment.")

# ---------------------------------------------------------------
# 5. Explorer les segments (PCA + boxplots)
# ---------------------------------------------------------------
section("analytics", "Explorer les segments")
COULEURS = {nom: SEGMENTS[nom]["couleur"] for nom in ORDRE_SEGMENTS}

with st.expander("Afficher la projection PCA et la distribution R, F, M par segment"):
    # --- Projection PCA des 4 333 clients ---
    st.markdown("**Projection PCA des clients** — les 2 composantes expliquent 94 % de la variance")
    fig_pca = px.scatter(
        rfm.reset_index(), x="PCA1", y="PCA2", color="Segment",
        color_discrete_map=COULEURS, category_orders={"Segment": ORDRE_SEGMENTS},
        opacity=0.55, hover_data=["CustomerID", "Recency", "Frequency", "Monetary"],
        labels={"PCA1": "PC1 – Valeur client (75,2 %)",
                "PCA2": "PC2 – Ancienneté du dernier achat (18,7 %)"},
    )
    fig_pca.update_layout(height=480, legend_title_text="", plot_bgcolor="white",
                          margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_pca, width="stretch")

    # --- Boxplots R, F, M par segment ---
    st.markdown("**Distribution de R, F et M par segment** (Fréquence et Montant en échelle log)")
    graphes = st.columns(3)
    for colonne, variable, titre in zip(
        graphes,
        ["Recency", "Frequency", "Monetary"],
        ["Récence (jours)", "Fréquence (commandes)", "Montant (£)"],
    ):
        fig_box = px.box(
            rfm.reset_index(), x="Segment", y=variable, color="Segment",
            color_discrete_map=COULEURS, category_orders={"Segment": ORDRE_SEGMENTS},
            points=False, log_y=(variable != "Recency"), title=titre,
        )
        fig_box.update_layout(showlegend=False, xaxis_title="", yaxis_title="",
                              height=380, plot_bgcolor="white",
                              margin=dict(l=10, r=10, t=40, b=10))
        colonne.plotly_chart(fig_box, width="stretch")

st.markdown(
    '<div class="pied">Segmentation RFM · K-means (K = 4) · Projet NexaData Consulting · '
    'Suz & Laurie — Les KPI détaillés sont disponibles dans le dashboard Looker Studio.</div>',
    unsafe_allow_html=True,
)
