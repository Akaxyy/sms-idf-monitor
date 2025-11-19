# src/utils
# Funções auxiliares (Helpers, formatadores)

def normalizar_responsavel(x):
    """Transforma a coluna 'RESPONSAVEL' em uma lista limpa."""
    if isinstance(x, list):
        if len(x) == 1 and isinstance(x[0], list):  # caso [[...]]
            x = x[0]
        if len(x) == 1 and isinstance(x[0], str) and "/" in x[0]:
            x = x[0].replace(" ", "").split("/")
    elif isinstance(x, str):
        if "/" in x:
            x = x.replace(" ", "").split("/")
        else:
            x = [x]
    else:
        x = []
    return x

def limpar_id_item(item_str):
    """
    Extrai o ID real do item, iognorando caminhos de diretórios se existirem.
    """
    if not isinstance(item_str, str):
        return str(item_str)
    
    clean_id = item_str.replace("\\", "/").split("/")[-1]
    return clean_id.strip()

