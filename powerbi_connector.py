import os
import glob
import win32com.client
import pandas as pd

def get_powerbi_port():
    # Chemins ou est stockée nativement le fichier du port local pour Analysis Services
    paths = [
        os.path.expanduser(r"~\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces"),
        os.path.expanduser(r"~\Microsoft\Power BI Desktop Store App\AnalysisServicesWorkspaces")
    ]
    
    # On parcourt chaque chemin possible pour trouver le fichier du port
    for base_path in paths:
        if os.path.exists(base_path):
            # Recherche récursive du fichier msmdsrv.port.txt contenant le port
            port_files = glob.glob(os.path.join(base_path, "**/Data/msmdsrv.port.txt"), recursive=True)
            for pf in port_files:
                try:
                    # lit le fichier de port
                    with open(pf, "r", encoding="utf-16le", errors="ignore") as f:
                        port = f.read().strip()
                        if port:
                            return port  # Retourne le port
                except Exception:
                    continue 
                    
    return None 

def executer_requete_dax(dax_query):
    
    # récupération du port local de Power BI
    port = get_powerbi_port()
    if not port:
        print("Aucun fichier Power BI Desktop actif détecté")
        return None
    
    # construction de la chaine de connexion grace au port récuperer
    conn_str = f"Provider=MSOLAP;Data Source=localhost:{port};"
    
    try:
        # Initialisation des objets de connexion et de stockage ADODB via Windows COM
        connection = win32com.client.Dispatch("ADODB.Connection")
        recordset = win32com.client.Dispatch("ADODB.Recordset")
        
        # Ouverture de la connexion et exécution de la requête DAX
        connection.Open(conn_str)
        recordset.Open(dax_query, connection)
        
        # Extraction des noms des colonnes du résultat
        columns = [recordset.Fields(i).Name for i in range(recordset.Fields.Count)]
        rows = []
        
        # Parcours de l'ensemble des lignes retournés par Power BI
        while not recordset.EOF:
            row = [recordset.Fields(i).Value for i in range(recordset.Fields.Count)]
            rows.append(row)
            recordset.MoveNext()  # ligne suivante
            
        # Fermeture des objets ADODB
        recordset.Close()
        connection.Close()
        
        # Conversion et retour des données sous forme de DataFrame Pandas
        return pd.DataFrame(rows, columns=columns)
        
    except Exception as e:
        print(f"Erreur lors de l'exécution DAX : {e}")
        return None

def recuperer_schema_modele():
    # Interroge le modèle Power BI et récupère les colonnes, mesures et valeurs textuelles clés
    requete_cols_info = "EVALUATE INFO.VIEW.COLUMNS()"
    
    try:
        df_cols = executer_requete_dax(requete_cols_info)
        
        if df_cols is not None and not df_cols.empty:
            schema_texte = "Tables, Colonnes et Types disponibles dans le modèle :\n"
            
            col_table = 'TableName' if 'TableName' in df_cols.columns else ('Table' in df_cols.columns and 'Table' or None)
            col_name = 'ExplicitName' if 'ExplicitName' in df_cols.columns else ('Name' in df_cols.columns and 'Name' or None)
            col_type = 'DataType' if 'DataType' in df_cols.columns else ('PrimitiveType' in df_cols.columns and 'PrimitiveType' or None)
            
            if col_table and col_name:
                for table, group in df_cols.groupby(col_table):
                    if table and not str(table).startswith('$'):
                        cols_types = []
                        for _, row in group.iterrows():
                            c_name = row[col_name]
                            if pd.notna(c_name):
                                c_type = f" ({row[col_type]})" if col_type and pd.notna(row[col_type]) else ""
                                cols_types.append(f"{c_name}{c_type}")
                        
                        if cols_types:
                            schema_texte += f"- Table '{table}' : {', '.join(cols_types)}\n"
                
                # récuperation des mesures
                try:
                    df_meas = executer_requete_dax("EVALUATE INFO.VIEW.MEASURES()")
                    if df_meas is not None and not df_meas.empty:
                        col_meas_name = 'ExplicitName' if 'ExplicitName' in df_meas.columns else 'Name'
                        if col_meas_name:
                            measures = df_meas[col_meas_name].dropna().tolist()
                            schema_texte += f"\n Mesures officielles disponibles : {measures}\n"
                except Exception:
                    pass

                # récupération ciblée des valeurs textuelles clés (Catégories, Pays, Marques)
                try:
                    df_cat = executer_requete_dax("EVALUATE VALUES('Products'[Category])")
                    if df_cat is not None and not df_cat.empty:
                        categories = df_cat.iloc[:, 0].dropna().tolist()
                        schema_texte += f" Valeurs 'Products'[Category] : {categories}\n"
                        
                    df_brand = executer_requete_dax("EVALUATE VALUES('Products'[Brand])")
                    if df_brand is not None and not df_brand.empty:
                        brands = df_brand.iloc[:, 0].dropna().tolist()
                        schema_texte += f" Valeurs 'Products'[Brand] : {brands}\n"
                        
                    df_country = executer_requete_dax("EVALUATE VALUES('Customers'[Country])")
                    if df_country is not None and not df_country.empty:
                        countries = df_country.iloc[:, 0].dropna().tolist()
                        schema_texte += f" Valeurs 'Customers'[Country] : {countries}\n"
                except Exception:
                    pass

                return schema_texte
    except Exception as e:
        print(f"Avertissement lors de la récupération DAX INFO : {e}")
        
    return "Modèle Power BI standard."