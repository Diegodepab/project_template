#!/bin/bash

# Definir las carpetas donde estarán las dependencias de Python y de R
export R_LIB="./R_packages"
export PYTHON_LIB="./py_packages"

# Crear directorios necesarios
mkdir -p data

# Descargar los datos de genes de HPO
wget https://ontology.jax.org/api/network/annotation/HP:0031993/download/gene -O data/genes.tsv

# Convertir genes a string id (descomentar cuando el script esté listo)
# python genes2string.py data/genes.tsv data/genes_string.tsv

# Descargar la red de String
wget https://stringdb-downloads.org/download/protein.links.v12.0/9606.protein.links.v12.0.txt.gz -O data/network.txt.gz

# Descomprimir el archivo descargado
gunzip data/network.txt.gz

# Propagación de genes (descomentar cuando el script esté listo)
# python dyamond.py data/genes_string.tsv data/network.txt data/red_propagada.txt

# Análisis de la red (descomentar cuando el script esté listo)
# python analisis.py data/red_propagada.txt data/clusters.txt

# Análisis de enriquecimiento funcional (descomentar cuando el script esté listo)
# python analisis_enriquecimiento.py data/clusters.txt
