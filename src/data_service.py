# src/data_service.py
# Lógica de dados, API e JSON

import pandas as pd
import streamlit as st

def processar_merge_api(df_principal, api_data):
    """
    Extrai 'status', 'soma_total' (PERCENTUAL) e 'diretorios' da API
    e faz o merge com o df_principal. (VERSÃO ATUALIZADA)
    """
    dados_api_chatos = []
    try:
        itens_por_setor = api_data.get('result', {})
        
        if not itens_por_setor:
            if 'STATUS' not in df_principal.columns:
                df_principal['STATUS'] = 'N/A'
            if 'PERCENTUAL' not in df_principal.columns:
                df_principal['PERCENTUAL'] = 0
            if 'DIRETORIOS' not in df_principal.columns:
                df_principal['DIRETORIOS'] = [[]] * len(df_principal)
            return df_principal

        for setor_nome, itens in itens_por_setor.items():
            for item_codigo, detalhes in itens.items():
                dados_api_chatos.append({
                    "ITEM": item_codigo,
                    "STATUS_API": detalhes.get("status"),
                    "TOTAL_API" : detalhes.get("soma_total"),
                    "PREVISAO_API" : detalhes.get("previsao_pastas"),
                    "PERCENTUAL_API": detalhes.get("percentual_conclusao"),
                    "DIRETORIOS_API": detalhes.get("diretorios", []) 
                })
        
        # 2. Criar um DataFrame dos dados da API
        df_api = pd.DataFrame(dados_api_chatos)
        
        # 3. Fazer o Merge
        df_merged = pd.merge(
            df_principal,
            df_api,
            on="ITEM",
            how="left"
        )
        
        # 4. Atualizar as colunas
        df_merged['STATUS'] = df_merged['STATUS_API']
        df_merged['PERCENTUAL'] = df_merged['PERCENTUAL_API']
        df_merged['TOTAL'] = df_merged['TOTAL_API']
        df_merged['PREVISAO'] = df_merged['PREVISAO_API']
        df_merged['DIRETORIOS'] = df_merged['DIRETORIOS_API']
        
        # 5. Limpar colunas temporárias
        df_merged = df_merged.drop(columns=['STATUS_API', 'PERCENTUAL_API', 'DIRETORIOS_API', 'TOTAL_API', 'PREVISAO_API'])
        
        # 6. Tratar Nulos pós-merge
        df_merged['PERCENTUAL'] = df_merged['PERCENTUAL'].fillna(0)
        df_merged['DIRETORIOS'] = df_merged['DIRETORIOS'].apply(lambda x: x if isinstance(x, list) else [])

        return df_merged

    except Exception as e:
        st.error(f"Erro ao processar dados da API em juntar_dataframe: {e}")
        # Retorna o DF original com colunas padrão em caso de falha
        if 'STATUS' not in df_principal.columns:
            df_principal['STATUS'] = 'Erro'
        if 'PERCENTUAL' not in df_principal.columns:
            df_principal['PERCENTUAL'] = 0
        if 'DIRETORIOS' not in df_principal.columns:
            df_principal['DIRETORIOS'] = [[]] * len(df_principal)
        return df_principal
    