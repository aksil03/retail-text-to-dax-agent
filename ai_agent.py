import os
import queries
from config import client
from powerbi_connector import recuperer_schema_modele

# filtre les question hors sujet avec un model moins performant pour optimiser l'utilisation des tokens
def verifier_et_filtrer_question(question):
    prompt_guard = """
    Tu es un filtre de sécurité sémantique pour un assistant d'entreprise en Business Intelligence.
    Analyse la question de l'utilisateur. 
    - Si la question concerne de près ou de loin les données de vente, les performances, les produits ou la stratégie commerciale, réponds uniquement par le mot : VALIDE.
    - Si la question est totalement hors-sujet (météo, politique, cuisine, blagues, etc.), rédige un refus poli.
    """
    try:
        response = client.chat.completions.create(
            model=os.getenv("CHAT_DEPLOYMENT_NAME_BLOCK"),  # gpt-5-nano
            messages=[
                {"role": "system", "content": prompt_guard},
                {"role": "user", "content": question}
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erreur lors du filtrage : {e}")
        return "VALIDE"

# transforme la question en requete dax et en traitant la reponse du llm
def generer_requete_dax(question):
    # On récupère le schéma complet du modèle Power BI en direct
    schema_actuel = recuperer_schema_modele()

    prompt_systeme = f"""
    Tu es un expert en modélisation Power BI et en langage DAX.
    
    Voici la structure exacte du modèle de données de l'entreprise actuellement connecté :
    {schema_actuel}
    
    Tu as également accès à un catalogue de requêtes de référence classées par thèmes (Produits, Clients, Magasins, Ventes). 
    Voici quelques exemples clés de ce catalogue :
    
    - Par Catégorie de produits :
    {queries.CA_ET_BENEFICE_PAR_CATEGORIE}
    
    - Par Pays client :
    {queries.CLIENTS_ET_CA_PAR_PAYS}
    
    - Synthèse globale KPIs :
    {queries.VUE_ENSEMBLE_KPIS}

    Règles absolues : 
    1. Réponds UNIQUEMENT avec une requête DAX valide commençant par le mot EVALUATE. Pas de texte additionnel, pas de markdown.
    2. Ne place JAMAIS d'expression booléenne de filtre (ex: `'Products'[Category] = "Audio"`) directement comme une colonne de regroupement dans SUMMARIZECOLUMNS. 
    3. Si tu dois filtrer une valeur spécifique (comme une catégorie précise), utilise CALCULATE sur ta mesure avec le filtre (ex: `CALCULATE([Bénéfice], 'Products'[Category] = "Audio")`) ou utilise la fonction FILTER proprement, et n'utilise jamais FILTER seul à la suite de SUMMARIZECOLUMNS.
    4. Pour les filtres textuels (catégories, pays, etc.), fais attention aux subtilités de pluriel ou de casse. Analyse la formulation de l'utilisateur et ajuste le texte filtré pour qu'il corresponde aux dénominations standardisées du retail.
    5. Si la question de l'utilisateur cible explicitement une entité unique (ex: "dans la catégorie X", "pour le pays Y"), n'utilise PAS SUMMARIZECOLUMNS avec la colonne de groupement si tu veux juste un chiffre global. Utilise plutôt EVALUATE ROW(...) pour ne retourner qu'une seule valeur ciblée.
    6. Pour tous les filtres textuels (catégories, marques, pays), utilise STRICTEMENT les noms complets et exacts listés dans les sections de valeurs exactes du schéma (par exemple, si l'utilisateur dit "adventure work", tu dois utiliser "Adventure Works"). Ne raccourcis et ne modifie jamais un nom de dimension textuelle.
    7. Pour les classements (comme "le plus haut", "le plus bas" avec TOPN), utilise de préférence la structure EVALUATE TOPN(1, ADDCOLUMNS(VALUES('Table'[Column]), "NomMesure", [NomDeMesure]), [NomDeMesure], DESC).
    8. Pour les mesures, utilise STRICTEMENT les noms exacts listés dans la section "Mesures officielles disponibles dans le modèle à utiliser impérativement" (par exemple, utilise [Temps moyen de livraison (jours)] et non [Temps moyen de livraison]). N'invente et ne raccourcis jamais le nom d'une mesure.
    9. Pour filtrer par année ou par date, utilise les colonnes de date réelles de la table 'Sales' (comme 'Sales'[Order Date]) ou de la table dimensionnelle de temps disponible, et n'invente jamais de table 'Date' qui n'existe pas dans le modèle.
    """
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("CHAT_DEPLOYMENT_NAME"),  # gpt-4o
            messages=[
                {"role": "system", "content": prompt_systeme},
                {"role": "user", "content": question}
            ],
            temperature=0.0
        )
        
        resultat = response.choices[0].message.content.strip()
        
        # Nettoyage des balises markdown appliquer aux requetes dax
        if resultat.startswith("```"):
            parts = resultat.split("```")
            if len(parts) > 1:
                resultat = parts[1]
                if resultat.startswith("dax"):
                    resultat = resultat[3:]
                resultat = resultat.strip()
                
        return resultat
        
    except Exception as e:
        print(f"Erreur lors de la génération DAX : {e}")
        return None

# utilisation d'un model plus puissant pour construire une strategie d'entreprise en adéquation au resultat de la mesure
def analyser_resultats_avec_ia(question, df_result):
    prompt_analyse = f"""
    Tu es un analyste stratégique senior en Retail et Business Intelligence.
    L'utilisateur a posé la question suivante : "{question}"
    
    Voici les données réelles extraites de la base de données de l'entreprise :
    {df_result.to_string(index=False)}

    Rédige une réponse professionnelle, claire et argumentée en français qui répond à la question en te basant STRICTEMENT sur ces données chiffrées. Mets en valeur les points clés (produits en hausse, en baisse, opportunités, etc.).
    """
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("CHAT_DEPLOYMENT_NAME"),  # gpt-4o
            messages=[
                {"role": "system", "content": "Tu es un assistant BI expert en restitution de données."},
                {"role": "user", "content": prompt_analyse}
            ],
            temperature=0.2  # augmentation de la température pour etre plus souple et créatif dans la réponse
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erreur lors de l'analyse textuelle : {e}")
        return "Impossible de générer l'analyse stratégique à partir des données."