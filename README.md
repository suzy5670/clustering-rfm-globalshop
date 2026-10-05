# 🛍️ Segmentation client RFM – GlobalShop Direct

Mission **NexaData Consulting** · Binôme : **Suz & Laurie**
🚀 **Application :** [globalshop-rfm.streamlit.app](https://globalshop-rfm.streamlit.app)

## 🎯 Objectif
Segmenter les clients de la plateforme e-commerce **GlobalShop Direct** selon leur comportement d'achat, afin de proposer des actions marketing adaptées à chaque profil.

## 🧭 Démarche
1. **Nettoyage** des transactions (`online_retail.csv`, déc. 2010 → déc. 2011) : clients inconnus, doublons, annulations, prix/quantités négatifs → **391 148 transactions, 4 333 clients**.
2. **Matrice RFM** : Récence, Fréquence et Montant par client.
3. **Prétraitement** : `log1p` contre l'asymétrie, puis standardisation.
4. **Clustering K-means** : **K = 4**, choisi avec la méthode du coude et le score de silhouette, comparé au clustering hiérarchique.
5. **PCA** : 2 composantes expliquent **94 %** de la variance.
6. **Profilage** : 4 personas et leurs actions marketing.

## 👥 Résultats
| Segment | % clients | % CA | Action |
|---|---:|---:|---|
| 🏆 Champions | 16 % | 64 % | Programme VIP |
| 💙 Clients fidèles | 27 % | 24 % | Fidélité, ventes croisées |
| 🌱 Nouveaux clients | 19 % | 5 % | Promo sur la 2ᵉ commande |
| 💤 Clients perdus | 38 % | 7 % | Campagne de réactivation |

👉 **16 % des clients génèrent 64 % du chiffre d'affaires.**

## 🖥️ Application Streamlit
KPI clés, profils des segments et **simulateur** : on saisit le profil RFM d'un client, l'appli lui attribue instantanément un segment et recommande des actions marketing.
Les KPI détaillés sont dans le dashboard **Looker Studio**.

## ⚙️ Lancer l'application
`pip install -r requirements.txt` puis `streamlit run app.py`

## 🛠️ Outils
Python · pandas · scikit-learn · Streamlit · Plotly · Looker Studio
