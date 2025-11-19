import re
from pathlib import Path
from typing import Dict, Any

# --- HELPERS DE REGEX (sem alteração) ---
def get_first_num(text: str) -> str | None:
    match = re.search(r"(\d+)", text)
    return match.group(1) if match else None

def get_second_num(text: str) -> str | None:
    match = re.search(r"\d+\.(\d+)", text)
    return match.group(1) if match else None
# ------------------------------------

# --- NOME DO ARQUIVO ESPECIAL ---
SPECIAL_FILENAME_STEM = "Não houveram registros no período"
# ------------------------------------

# --- O "GABARITO" (Corrigido) ---
MASTER_TREE = {
    "1. SMS": {
        "1. Incidentes": {
            "1.1  Abrangencia das Ocorrencias": {},
            "1.2 Tratamento das Ocorrencias": {
                "1. Plano de Ação": {},
                "2. Evidencias do Plano de Ação": {},
            },
            "1.3 Ocorrencias": {"1. Relatório": {}, "2. CAT": {}},
        },
        "2. Normas Regulamentadoras": {
            "2.1  Matriz de Treinamento e NR 01": {
                "Controle de Treinam": {},
                "Cronog. de Treinamentos SMS_CQ": {},
                "Horas de Treinament": {},
                "Indice de Treinamen": {},
                "Integração/AVALIAÇÃO": {},
                "Integração/LISTA DE PRESENÇA": {},
                "Matriz de Treinamento": {},
                "NR06/AVALIAÇÃO": {},
                "NR06/LISTA DE PRESENÇA": {},
                "NR20/AVALIAÇÃO": {},
                "NR20/LISTA DE PRESENÇA": {},
                "NR33/AVALIAÇÃO": {},
                "NR33/LISTA DE PRESENÇA": {},
                "NR35/AVALIAÇÃO": {},
                "NR35/LISTA DE PRESENÇA": {},
                "Procedi. Operac/CQ": {},
            }
        },
        "3. Gestão de SMS": {
            "3.1 Inventário e Manutenção - Maquinas e Equipamentos": {
                "Cronograma Preventiva": {},
                "Evidencia do Cronogra": {},
            },
            "3.2 Avaliações Iniciais (PGR e PCMSO)": {
                "C3/Periodicas": {},
                "Subcontratada/Periodicas/BWAR - PMOC": {},
                "Subcontratada/Periodicas/POINT THERMIC": {},
                "Subcontratada/Periodicas/R3 USINAGEM": {},
                "Subcontratada/Periodicas/RITER": {},
                "Subcontratada/Periodicas/SUED VAZIL": {},
            },
            "3.3 Ferramentas Proativas": {
                "Campanhas e Boas Práticas": {},
                "RAC": {},
            },
            "3.4 Tratamento de NC e Desvios": {
                "Audicomp Petrobrás": {},
                "Plano de Ação Gestão": {}, 
                "Plano de Ação Gestão/Evidencias": {}, 
                "SAMC": {},
            },
        },
    },
    "2. Qualidade": {
        "2.1 Registros de NC": {
            "1. Não conformidades registradas": {},
        },
        "2.2 Tratamento de NC (fornecedor)": {
            "1. Evidencias": {},
            "2. Plano de Ação": {},
        },
        "2.3 Retrabalho": {
            "1. Evidencia": {}, 
            "2. Plano de Ação": {}
        },
        "2.4 Disponibilidade de Recursos Técnicos": {
            "1. Evidencia": {},
            "2. Plano de Ação": {},
        },
        "2.5 Paralisação de Serviços": {
            "1. Evidencia": {}, 
            "2. Plano de Ação": {}
        },
    },
    "3. Prazo": {
        "3.1 Entrega Antecipada e Atendimento de Urgência": {
            "1. SAMC": {},
        },
        "3.2 Atendimento aos Prazos Contratuais": {
            "1. Notificação no SAMC": {},
            "2. Realizado Pacotes/1. Curva": {},
            "2. Realizado Pacotes/2. Efetivo": {},
            "3. Realizado Rotina/1. Curva": {},
            "3. Realizado Rotina/2. Efetivo": {},
            "4. Realizado Tanques/1. Curva": {},
            "4. Realizado Tanques/2. Efetivo": {},
            "5. Realizado Total": {},
        },
    },
    "4. Gestão": {
        "1. Adequação dos Recursos Humanos": {
            "1. Doc. (habilitação e qualificação)/Planilha Qualifi": {},
            "2. Recursos Humanos": {},
        },
        "2. Cumprimento das Obrigações Legais": {
            "1. Documentação Legal C3/C3/Periodicas": {},
            "2. Documentação Legal Sub/Subcontratada/Periodicas/BWAR - PMOC": {},
            "2. Documentação Legal Sub/Subcontratada/Periodicas/POINT THERMIC": {},
            "2. Documentação Legal Sub/Subcontratada/Periodicas/R3 USINAGEM": {},
            "2. Documentação Legal Sub/Subcontratada/Periodicas/RITER": {},
            "2. Documentação Legal Sub/Subcontratada/Periodicas/SUED VAZIL": {},
            "3. Lista das Subcontratadas": {},
        },
        "3. Estrutura Administrativa Disponibilizada": {
            "1. Fiscalização (SAMC)": {},
            "2. Reuniões Gerenciais": {},
        },
    },
}
# ------------------------------------


def calculate_item_id(num_X_categoria, rel_path_parts):
    # (Função sem alteração)
    num_X_final, num_Y_final, num_Z_final = "0", "0", "0"
    subLvl1 = rel_path_parts[0] if len(rel_path_parts) > 0 else ""
    subLvl2 = rel_path_parts[1] if len(rel_path_parts) > 1 else ""

    if num_X_categoria == "1" or num_X_categoria == "4":
        num_X_final = num_X_categoria
        num_Y_match = get_first_num(subLvl1)
        num_Z_match = get_second_num(subLvl2)
        if num_Y_match: num_Y_final = num_Y_match
        if num_Z_match: 
            num_Z_final = num_Z_match
        else:
            num_Z_fallback = get_first_num(subLvl2)
            if num_Z_fallback: num_Z_final = num_Z_fallback
    else: 
        num_X_match = get_first_num(subLvl1)
        num_Y_match = get_second_num(subLvl1)
        num_Z_match = get_first_num(subLvl2)
        if num_X_match: num_X_final = num_X_match
        if num_Y_match: num_Y_final = num_Y_match
        if num_Z_match: num_Z_final = num_Z_match
    
    return f"{num_X_final}.{num_Y_final}.{num_Z_final}"


def process_master_tree(
    base_path: Path, 
    master_node: Dict, 
    num_X_categoria: str, 
    new_category_key: str, 
    special_paths: set, 
    intermediate_data: Dict, 
    rel_path_parts: list = None,
    inherited_flag: bool = False
):
    # (Função sem alteração)
    if rel_path_parts is None:
        rel_path_parts = []

    if not master_node: 
        rel_key = "/".join(rel_path_parts)
        disk_path = base_path / rel_key
        item_id = calculate_item_id(num_X_categoria, rel_path_parts)
        
        flag_concluido_especial = inherited_flag
        final_qtd = 0
        final_diretorio = rel_key
        final_itens = [] # Inicializa a lista de itens

        if disk_path.is_dir():
            # Pasta existe
            all_files = [f for f in disk_path.iterdir() if f.is_file()]
            real_files = [f for f in all_files if f.stem != SPECIAL_FILENAME_STEM]
            final_qtd = len(real_files)
            
            # --- AQUI: Preenche os itens com os nomes dos arquivos reais ---
            final_itens = [f.name for f in real_files]
            
            if disk_path in special_paths:
                flag_concluido_especial = True
            
            # Se foi justificado e não tem arquivos, conta como 1
            if flag_concluido_especial and final_qtd == 0:
                final_qtd = 1
                final_diretorio = f"{rel_key}/{SPECIAL_FILENAME_STEM}"
                # Adiciona a justificativa na lista de itens
                final_itens = [SPECIAL_FILENAME_STEM] 
        else:
            # Pasta NÃO existe: Injeção
            flag_concluido_especial = True
            final_qtd = 1
            final_diretorio = f"{rel_key}/{SPECIAL_FILENAME_STEM}"
            # Adiciona a justificativa na lista de itens
            final_itens = [SPECIAL_FILENAME_STEM]

        # --- Monta o Payload com a lista de itens ---
        dir_payload = {
            "diretorio": final_diretorio, 
            "qtd": final_qtd,
            "itens": final_itens, # <--- NOVA VARIÁVEL
            "flag_concluido": flag_concluido_especial 
        }
        
        if item_id not in intermediate_data[new_category_key]:
            intermediate_data[new_category_key][item_id] = []
        intermediate_data[new_category_key][item_id].append(dir_payload)

        return

    # Recursão para subpastas
    for dir_name, child_node in master_node.items():
        current_rel_path = rel_path_parts + [dir_name]
        current_disk_path = base_path / Path("/".join(current_rel_path))
        
        current_flag = inherited_flag
        if current_disk_path.is_dir() and current_disk_path in special_paths:
            current_flag = True
        
        process_master_tree(
            base_path, 
            child_node, 
            num_X_categoria, 
            new_category_key, 
            special_paths, 
            intermediate_data, 
            current_rel_path,
            current_flag
        )


def montar_relatorio_sms(base_path: Path) -> Dict[str, Any]:
    # --- PRÉ-SCAN ---
    special_paths = set()
    for f in base_path.rglob(f"{SPECIAL_FILENAME_STEM}*"):
        if f.is_file():
            special_paths.add(f.parent)

    # ETAPA 1: COLETAR DADOS
    intermediate_data: Dict[str, Any] = {}

    for category_name, category_node in MASTER_TREE.items():
        num_X_categoria = get_first_num(category_name)
        if not num_X_categoria: continue

        top_name = re.sub(r"(\d+(?:\.\d+)?)\.?\s*", "", category_name).strip()
        new_category_key = f'Item {top_name}'
        
        if new_category_key not in intermediate_data:
            intermediate_data[new_category_key] = {}
        
        category_path = base_path / category_name
        
        process_master_tree(
            category_path, 
            category_node, 
            num_X_categoria, 
            new_category_key, 
            special_paths, 
            intermediate_data,
            rel_path_parts=[],
            inherited_flag=False
        )

    # --- ETAPA 2: PROCESSAR DADOS ---
    final_report: Dict[str, Any] = {}
    
    for category_key, id_groups in intermediate_data.items():
        final_report[category_key] = {}
        
        for item_id, diretorios_list in id_groups.items():
            
            soma_total = 0
            count_pastas_preenchidas = 0 
            count_total_pastas = len(diretorios_list)

            for dir_payload in diretorios_list:
                soma_total += dir_payload["qtd"]
                
                if dir_payload["qtd"] > 0 or dir_payload["flag_concluido"]:
                    count_pastas_preenchidas += 1

            status = ""
            if count_pastas_preenchidas == 0:
                status = "Não Iniciado"
            elif count_pastas_preenchidas == count_total_pastas:
                status = "Concluído"
            else:
                status = "Em Andamento"
            
            percentual_conclusao = 0.0
            if count_total_pastas > 0:
                percentual_conclusao = (count_pastas_preenchidas / count_total_pastas) * 100
            
            for p in diretorios_list: p.pop("flag_concluido", None)

            final_report[category_key][item_id] = {
                "status": status,
                "soma_total": soma_total,
                "previsao_pastas": count_total_pastas,
                "percentual_conclusao": round(percentual_conclusao, 2),
                "diretorios": diretorios_list
            }

    return {
        "status": "ok",
        "result": final_report,
        "path": str(base_path)
    }