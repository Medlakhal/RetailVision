/*
===============================================================================
RetailVision — KPI SQL Guide (KPI 1 à KPI 6)
===============================================================================

Objectif
--------
Ce fichier contient les requêtes SQL d'analyse métier du projet RetailVision.
Il sert de guide reproductible : une autre personne peut ouvrir ce fichier dans
pgAdmin, DBeaver ou un client PostgreSQL compatible, sélectionner une requête
KPI et l'exécuter pour reproduire l'analyse.

Base de données : retailvision_dw
Schéma         : retailvision
SGBD           : PostgreSQL

Prérequis
---------
- Les tables du Data Warehouse doivent déjà être chargées.
- Le schéma doit contenir fact_ventes, dim_date, dim_produit, dim_vendeur
  et dim_geography.
- La table fact_ventes doit contenir sales_amount et customer_geo_key.
- sales_amount correspond au prix de l'article + les frais de livraison.
- Les résultats décrivent les lignes présentes dans le Data Warehouse, et
  peuvent différer de la source brute si certaines lignes n'ont pas été chargées.

Conseils d'utilisation
----------------------
1. Connectez-vous à la base retailvision_dw.
2. Exécutez SET search_path pour sélectionner le schéma retailvision.
3. Exécutez chaque section KPI séparément.
4. Pour les comparaisons temporelles, vérifiez si le mois est complet.
5. Les requêtes de performance utilisent le chiffre d'affaires, pas le bénéfice.

IMPORTANT — Grain de la table de faits
-------------------------------------
fact_ventes contient une ligne par article de commande (order_id, order_item_id).
COUNT(*) compte donc des articles/lignes de vente, pas des commandes.
Pour compter les commandes, utilisez COUNT(DISTINCT order_id).

===============================================================================
Configuration du schéma
===============================================================================
*/
SET search_path TO retailvision;


/*
===============================================================================
KPI 1 — Évolution mensuelle des ventes
===============================================================================
Question métier :
Comment évoluent le nombre de commandes et le chiffre d'affaires au fil des mois ?

Mesures :
- nombre_commandes : nombre de commandes distinctes ayant des lignes dans la table
- chiffre_affaires : somme de sales_amount (prix + frais de livraison)

Attention :
Les mois absents ne sont pas affichés. Certains mois au début et à la fin de la
période peuvent être incomplets. Il faut éviter d'interpréter directement ces
mois comme une baisse ou une hausse réelle.
===============================================================================
*/
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_id) AS nombre_commandes,
    ROUND(SUM(f.sales_amount), 2) AS chiffre_affaires
FROM fact_ventes AS f
JOIN dim_date AS d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


/*
===============================================================================
KPI 2 — Croissance mensuelle du chiffre d'affaires (Month-over-Month)
===============================================================================
Question métier :
Quel est le pourcentage de variation du chiffre d'affaires par rapport au
mois précédent disponible dans les données ?

Méthode :
1. Agréger les ventes par mois.
2. Utiliser LAG() pour récupérer le CA de la ligne mensuelle précédente.
3. Calculer (CA courant - CA précédent) / CA précédent * 100.

IMPORTANT :
LAG() compare au mois précédent présent dans le résultat, pas forcément au
mois calendaire précédent. Si un mois est absent, la comparaison saute ce mois.
Par exemple, si novembre 2024 est absent, décembre peut être comparé à octobre.
Les mois partiels peuvent aussi produire des variations trompeuses.
===============================================================================
*/
WITH ventes_mensuelles AS (
    SELECT
        DATE_TRUNC('month', d.full_date)::date AS mois,
        SUM(f.sales_amount) AS chiffre_affaires
    FROM fact_ventes AS f
    JOIN dim_date AS d
        ON f.date_key = d.date_key
    GROUP BY DATE_TRUNC('month', d.full_date)::date
),
ventes_avec_precedent AS (
    SELECT
        mois,
        chiffre_affaires,
        LAG(chiffre_affaires) OVER (ORDER BY mois) AS ca_mois_precedent
    FROM ventes_mensuelles
)
SELECT
    mois,
    ROUND(chiffre_affaires::numeric, 2) AS chiffre_affaires,
    ROUND(ca_mois_precedent::numeric, 2) AS ca_mois_precedent,
    CASE
        WHEN ca_mois_precedent IS NULL OR ca_mois_precedent = 0 THEN NULL
        ELSE ROUND(
            ((chiffre_affaires - ca_mois_precedent)
                / ca_mois_precedent * 100)::numeric,
            2
        )
    END AS croissance_mensuelle_pct
FROM ventes_avec_precedent
ORDER BY mois;


/*
===============================================================================
KPI 3 — Performance des produits
===============================================================================
Question métier :
Quels produits génèrent le plus de chiffre d'affaires ?

Mesures :
- nombre_articles_vendus : nombre de lignes d'articles dans fact_ventes
- nombre_commandes : nombre de commandes distinctes contenant le produit
- chiffre_affaires : somme de sales_amount pour le produit
- ca_moyen_par_article : CA total / nombre de lignes d'articles

IMPORTANT :
Le CA moyen par article inclut les frais de livraison inclus dans sales_amount.
Ce n'est ni le prix moyen du produit seul, ni une marge, ni un bénéfice.
La requête agrège par produit et limite le résultat aux 10 premiers produits.
===============================================================================
*/
SELECT
    p.product_id,
    p.product_category_name,
    COUNT(*) AS nombre_articles_vendus,
    COUNT(DISTINCT f.order_id) AS nombre_commandes,
    ROUND(SUM(f.sales_amount), 2) AS chiffre_affaires,
    ROUND(SUM(f.sales_amount) / NULLIF(COUNT(*), 0), 2)
        AS ca_moyen_par_article
FROM fact_ventes AS f
JOIN dim_produit AS p
    ON f.product_key = p.product_key
GROUP BY
    p.product_id,
    p.product_category_name
ORDER BY
    SUM(f.sales_amount) DESC
LIMIT 10;


/*
===============================================================================
KPI 4 — Performance des vendeurs
===============================================================================
Question métier :
Quels vendeurs génèrent le plus de chiffre d'affaires ?

Mesures :
- nombre_articles_vendus : nombre de lignes d'articles vendus
- nombre_commandes : nombre de commandes distinctes auxquelles le vendeur a
  contribué. Une commande peut contenir plusieurs vendeurs.
- chiffre_affaires : somme de sales_amount attribuée aux lignes du vendeur
- ca_moyen_par_article : CA total du vendeur / nombre de lignes d'articles

Attention :
Le classement par CA ne suffit pas pour évaluer toute la performance d'un
vendeur. Le volume, le CA moyen et d'autres indicateurs métier peuvent compléter
l'analyse. Ce KPI mesure le CA, pas la rentabilité.
===============================================================================
*/
SELECT
    s.seller_id,
    COUNT(*) AS nombre_articles_vendus,
    COUNT(DISTINCT f.order_id) AS nombre_commandes,
    ROUND(SUM(f.sales_amount), 2) AS chiffre_affaires,
    ROUND(SUM(f.sales_amount) / NULLIF(COUNT(*), 0), 2)
        AS ca_moyen_par_article
FROM fact_ventes AS f
JOIN dim_vendeur AS s
    ON f.seller_key = s.seller_key
GROUP BY s.seller_id
ORDER BY SUM(f.sales_amount) DESC
LIMIT 10;


/*
===============================================================================
KPI 5 — Répartition géographique des ventes par région du client
===============================================================================
Question métier :
Quelles régions des clients génèrent le plus de commandes, d'articles et de CA ?

Jointure :
fact_ventes.customer_geo_key -> dim_geography.geography_key

Prérequis métier :
La colonne dim_geography.region doit être alimentée avec les régions
brésiliennes. Dans ce projet, les états brésiliens ont été mappés vers :
Norte, Nordeste, Centro-Oeste, Sudeste et Sul. Les lignes sans région reconnue
restent dans le groupe Unknown ou Inconnue selon la valeur stockée.

Attention :
Ce KPI utilise la géographie du client, pas celle du vendeur.
Il faut que le mapping de région ait été appliqué après le chargement des
dimensions.
===============================================================================
*/
SELECT
    COALESCE(g.region, 'Inconnue') AS region_client,
    COUNT(DISTINCT f.order_id) AS nombre_commandes,
    COUNT(*) AS nombre_articles_vendus,
    ROUND(SUM(f.sales_amount), 2) AS chiffre_affaires
FROM fact_ventes AS f
JOIN dim_geography AS g
    ON f.customer_geo_key = g.geography_key
GROUP BY COALESCE(g.region, 'Inconnue')
ORDER BY SUM(f.sales_amount) DESC;


/*
===============================================================================
KPI 6 — Commandes par statut
===============================================================================
Question métier :
Combien de commandes sont représentées dans la table de faits pour chaque
statut, et quel CA est associé à leurs lignes de vente ?

Mesures :
- nombre_commandes : nombre de commandes distinctes
- chiffre_affaires : somme de sales_amount des lignes présentes pour ce statut

IMPORTANT :
Cette requête mesure les commandes représentées dans fact_ventes, pas
nécessairement toutes les commandes de la source brute. Les commandes sans
ligne chargée dans la table de faits ne seront pas comptées.
Le CA associé à un statut n'est pas nécessairement du revenu encaissé :
annulations, remboursements, paiements et coûts ne sont pas modélisés ici.
===============================================================================
*/
SELECT
    order_status,
    COUNT(DISTINCT order_id) AS nombre_commandes,
    ROUND(SUM(sales_amount), 2) AS chiffre_affaires
FROM fact_ventes
GROUP BY order_status
ORDER BY nombre_commandes DESC;


/*
===============================================================================
Contrôle qualité facultatif — Réconciliation du chiffre d'affaires
===============================================================================
Objectif :
Vérifier que le total global correspond à la somme du CA par statut.
Le total attendu dans l'exécution actuelle du projet était 15 840 025,74.
Le résultat peut changer si les données sont rechargées ou transformées.
===============================================================================
*/
SELECT
    ROUND(SUM(sales_amount), 2) AS chiffre_affaires_total,
    COUNT(DISTINCT order_id) AS nombre_commandes,
    COUNT(*) AS nombre_lignes_articles
FROM fact_ventes;
