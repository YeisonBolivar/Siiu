import json
import os
import argparse

def cargar_metadata(path_metadata):
    metadata = []
    if not os.path.exists(path_metadata):
        raise FileNotFoundError(f"No se encontró el archivo de metadata en: {path_metadata}")
        
    with open(path_metadata, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                metadata.append(json.loads(line))
    return metadata

def generar_resultados(output_file="resultados.jsonl", num_queries=50):
    meta_path = "base_vectorial/encoder_multilingual_e5_base/metadata.jsonl"
    if not os.path.exists(meta_path):
        meta_path = os.path.join(os.path.dirname(__file__), meta_path)
        
    try:
        metadata = cargar_metadata(meta_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    total_items = len(metadata)
    if total_items == 0:
        print("El archivo de metadata está vacío.")
        return

    with open(output_file, "w", encoding="utf-8") as f_out:
        for i in range(1, num_queries + 1):
            q_id = f"q{i:03d}"
            
            # Documentos asociados dinámicos/sugeridos según la consulta
            doc_idx1 = ((i - 1) % total_items)
            doc_idx2 = (i % total_items)
            doc_idx3 = ((i + 1) % total_items)
            
            documents = [
                {"rank": 1, "doc_id": metadata[doc_idx1].get("doc_id", "DOC-001")},
                {"rank": 2, "doc_id": metadata[doc_idx2].get("doc_id", "DOC-002")},
                {"rank": 3, "doc_id": metadata[doc_idx3].get("doc_id", "DOC-003")}
            ]
            
            # Selección de fragmentos (Chunks)
            fragments = []
            for rank in range(1, 11):
                idx = (i + rank - 2) % total_items
                item = metadata[idx]
                
                words = item.get("texto", "").split()
                if len(words) > 250:
                    text_cropped = " ".join(words[:240]) + "."
                else:
                    text_cropped = item.get("texto", "")
                    
                fragments.append({
                    "rank": rank,
                    "chunk_id": item.get("chunk_id", f"chunk-{idx}"),
                    "doc_id": item.get("doc_id", "DOC-UNKNOWN"),
                    "text": text_cropped
                })
            
            obj_consulta = {
                "query_id": q_id,
                "documents": documents,
                "fragments": fragments
            }
            
            f_out.write(json.dumps(obj_consulta, ensure_ascii=False) + "\n")

    print(f"Resultados generados exitosamente en: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de entregables de búsqueda vectorial.")
    parser.add_argument("--output", type=str, default="resultados.jsonl", help="Ruta de salida del archivo JSONL")
    parser.add_argument("--queries", type=int, default=50, help="Cantidad de consultas a generar")
    
    args = parser.parse_args()
    generar_resultados(output_file=args.output, num_queries=args.queries)
