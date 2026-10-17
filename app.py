from powerbi_connector import get_powerbi_port, executer_requete_dax
from ai_agent import verifier_et_filtrer_question, generer_requete_dax, analyser_resultats_avec_ia

def main():
    print("Assistant Intelligent Power BI - Prêt")
    port = get_powerbi_port()
    
    if not port:
        print("Aucun Power BI Desktop actif détecté. Ouvre ton fichier .pbix sur ton PC")
        return

    print(f"Connecté au moteur local sur le port : {port}\n")
    print("Tape 'q' pour fermer le programme.\n")
    
    while True:
        question = input("Pose ta question sur tes données ou ta stratégie : ")
        
        if question.lower() in ['q']:
            print("Au revoir !")
            break
            
        if not question.strip():
            continue
            
        print("Analyse de la question par l'IA...")
        
        # Filtre de sécurité 
        filtre_resultat = verifier_et_filtrer_question(question)
        if filtre_resultat != "VALIDE":
            print(f"\n Réponse de l'assistant :\n{filtre_resultat}\n")
            print("-" * 60 + "\n")
            continue
            
        # Génération de la requête DAX 
        dax_query = generer_requete_dax(question)
        if not dax_query or not dax_query.startswith("EVALUATE"):
            print("L'IA n'a pas pu générer une requête DAX valide pour cette question.\n")
            continue
            
        print(f"\n Requête DAX générée :\n{dax_query}\n")
        print("Interrogation du modèle Power BI...")
        
        # Exécution dans Power BI
        df_result = executer_requete_dax(dax_query)
        
        if df_result is not None and not df_result.empty:
            print("\n Données brutes récupérées :")
            print(df_result.to_string(index=False))
            print("\n Rédaction de l'analyse stratégique par l'IA...")
            
            # Analyse des résultats par l'IA
            analyse_finale = analyser_resultats_avec_ia(question, df_result)
            print(f"\n{analyse_finale}\n")
            print("-" * 60 + "\n")
        else:
            print(" Aucun résultat renvoyé par Power BI pour cette requête.\n")

if __name__ == "__main__":
    main()