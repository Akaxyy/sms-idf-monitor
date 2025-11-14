from pathlib import Path

def contar_arquivos_diretos(pasta: Path) -> int:
    return len([f for f in pasta.iterdir() if f.is_file()])


def montar_relatorio_sms(base_path: Path):
    map_itens = {
        "1.1.1": base_path / r"1. SMS/1. Incidentes/1.1  Abrangencia das Ocorrencias",
        "1.1.2": base_path / r"1. SMS/1. Incidentes/1.2 Tratamento das Ocorrencias",
        "1.1.3": base_path / r"1. SMS/1. Incidentes/1.3 Ocorrencias",
        "1.2.1": base_path / r"1. SMS/2. Normas Regulamentadoras/2.1  Matriz de Treinamento e NR 01",
        "1.3.1": base_path / r"1. SMS/3. Gestão de SMS/3.1 Inventário e Manutenção - Maquinas e Equipamentos",
        "1.3.2": base_path / r"1. SMS/3. Gestão de SMS/3.2 Avaliações Iniciais (PGR e PCMSO)",
        "1.3.3": base_path / r"1. SMS/3. Gestão de SMS/3.3 Ferramentas Proativas",
        "1.3.4": base_path / r"1. SMS/3. Gestão de SMS/3.4 Tratamento de NC e Desvios",
    }

    relatorio = {}

    for codigo, rel_path in map_itens.items():
        item_path = base_path / rel_path
        if not item_path.exists():
            continue

        todos_dirs = [d for d in item_path.rglob("*") if d.is_dir()]
        todos_dirs_sorted = sorted(todos_dirs, key=lambda p: str(p))

        item_info = {"folders": {}, "total_arquivos": 0}

        # Contagem por pasta (ajustada para não mostrar 0 se tiver subpastas)
        for d in todos_dirs_sorted:
            rel = d.relative_to(item_path)
            chave = str(rel).replace("\\", "/")
            n = contar_arquivos_diretos(d)
            tem_subpastas = any(child.is_dir() for child in d.iterdir())

            if n > 0 or not tem_subpastas:
                item_info["folders"][chave] = n
                item_info["total_arquivos"] += n

        relatorio[codigo] = item_info["folders"]

    return relatorio

                      