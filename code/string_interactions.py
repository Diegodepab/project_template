# stringdb_interaction_proteins.py
import pandas as pd
import requests

def download_interactions(proteins_file, output_file):
    # Cargar los identificadores de proteínas desde el archivo
    with open(proteins_file, "r") as file:
        protein_ids = [line.strip() for line in file.readlines()]

    # Preparar la URL para StringDB
    species_id = 9606  # Homo sapiens
    string_api_url = "https://string-db.org/api/tsv/network"
    proteins_str = "%0d".join(protein_ids)  # Concatenar proteínas en el formato requerido por StringDB

    # Construir la solicitud a StringDB
    params = {
        "identifiers": proteins_str,  # Identificadores separados por %0d
        "species": species_id,
        "required_score": 400,  # Puntaje mínimo (ajustable)
        "network_type": "functional"
    }

    # Realizar la solicitud GET a StringDB
    response = requests.get(string_api_url, params=params)
    if response.status_code == 200:
        with open(output_file, "w") as file:
            file.write(response.text)
        print(f"Red de interacciones descargada exitosamente en '{output_file}'")
    else:
        print(f"Error al descargar datos de StringDB: {response.status_code}")

# Ejecutar la función si el archivo se ejecuta directamente
if __name__ == "__main__":
    # Nombre del archivo de entrada y salida
    input_file = "red_propagada.txt"
    output_file = "string_interactions.tsv"

    # Llamar a la función para descargar las interacciones
    download_interactions(input_file, output_file)
