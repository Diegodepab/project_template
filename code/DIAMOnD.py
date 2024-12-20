############################################################
########## Entradas y salidas de esta parte ################
############################################################
# entrada
# data/network.txt Red del homosapiens
# data/genes_string.tsv Genes iniciales

# output 
# data/red_propagada.txt

# Codigo para ejecutarlo
# python DIAMOnD.py data/genes_string.tsv data/network.txt 20 1 data/red_propagada.txt

############################################################
########## Descarga o llamar las librerías #################
############################################################
try:
    import subprocess
except ImportError:
    print("Error inesperado")

# Función para instalar una librería si no está disponible
def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        print(f"Error installing package {package}: {e}")

try:
    import networkx as nx
except ImportError:
    install_package('networkx')
    import networkx as nx

try:
    import scipy.stats
except ImportError:
    install_package('scipy')
    import scipy.stats

try:
    import numpy as np
except ImportError:
    install_package('numpy')
    import numpy as np

try:
    from collections import defaultdict
except ImportError:
    install_package('collections')  # Parte de la librería estándar
    from collections import defaultdict

try:
    import sys
except ImportError:
    print("sys no está instalado. Intentando instalar...")
    # sys es parte de la librería estándar, así que esto no debería ser necesario
    install_package('sys')
    import sys

try:
    from tqdm import tqdm
except ImportError:
    install_package('tqdm')
    from tqdm import tqdm

# ------------------- FUNCIONES DE DIAMOND -------------------
def read_input(network_file, seed_file):
    """Lee la red y la lista de genes de semilla desde archivos externos, y considera el puntaje combinado como peso."""
    # Leer la red con pesos
    G = nx.Graph()
    with open(network_file, 'r') as f:
        for line in f:
            if line.startswith("protein1") or line.startswith("#"):
                continue  # Omitir líneas de encabezado o comentarios
            node1, node2, score = line.strip().split()  # Cambié a split() para leer por espacios
            score = int(score)  # Convertimos el score a entero

            # Filtrar las conexiones con score <= 400
            if score > 400:
                G.add_edge(node1, node2, weight=score)

    # Leer los genes de semilla
    seed_genes = set()
    with open(seed_file, 'r') as f:
        for line in f:
            for gene in line.strip().split():  # Lee todos los genes separados por espacios
                seed_genes.add(gene)

    return G, seed_genes



def compute_all_gamma_ln(N):
    """Precomputa todas las funciones gamma logarítmicas."""
    gamma_ln = {i: scipy.special.gammaln(i) for i in range(1, N + 1)}
    return gamma_ln

def gauss_hypergeom(x, r, b, n, gamma_ln):
    """Distribución hipergeométrica."""
    max_index = len(gamma_ln) - 1
    if r + b > max_index or x > max_index or r < x or b < (n - x):
        return 0  

    return np.exp(gamma_ln[r] - (gamma_ln[x] + gamma_ln[r - x]) +
                  gamma_ln[b] - (gamma_ln[n - x] + gamma_ln[b - n]) -
                  gamma_ln[r + b])

def pvalue(kb, k, N, s, gamma_ln):
    """Calcula el p-valor para un nodo con kb enlaces a semillas y k enlaces totales."""
    return sum(gauss_hypergeom(n, s, N - s, k, gamma_ln) for n in range(kb, k + 1))

from tqdm import tqdm

def diamond_iteration_of_first_X_nodes(G, S, X, alpha=1):
    """
    Ejecuta una iteración del algoritmo DIAMOnD de manera determinista,
    priorizando nodos con menor p-valor y, en caso de empate, usando la suma ponderada
    de los pesos de sus conexiones hacia los nodos del cluster.
    
    Parámetros:
        G: La red de interacción proteica (grafo de NetworkX).
        S: Conjunto de genes semilla.
        X: Número de genes a agregar.
        alpha: Parámetro opcional de ponderación (por defecto 1).
        
    Retorna:
        added_nodes: Lista de los genes agregados.
    """
    added_nodes = []
    neighbors = {node: set(G.neighbors(node)) for node in G.nodes}
    degrees = {node: G.degree(node) for node in G.nodes}
    cluster_nodes = set(S)
    gamma_ln = compute_all_gamma_ln(len(G.nodes))

    # Barra de progreso en la iteración DIAMOnD
    with tqdm(total=X, desc="Agregando genes con DIAMOnD", unit="gen", leave=True) as pbar:
        while len(added_nodes) < X:
            candidates = []

            # Iterar sobre los nodos que no están en el cluster actual
            for node in set(G.nodes) - cluster_nodes:
                k = degrees[node]  # Grado total del nodo
                kb = sum(1 for neighbor in neighbors[node] if neighbor in cluster_nodes)  # Grado en semillas
                p = pvalue(kb, k, len(G.nodes), len(cluster_nodes), gamma_ln)

                # Calcular la suma ponderada de los pesos hacia los genes semilla
                weight_sum = sum(G[node][neighbor]['weight'] for neighbor in neighbors[node] if neighbor in cluster_nodes)

                # Añadir los nodos candidatos junto con sus criterios
                candidates.append((p, -weight_sum, node))  # Nota: -weight_sum para priorizar mayor peso

            # Ordenar por p-valor, luego por suma de pesos (mayor primero) y finalmente por el ID del nodo
            candidates.sort()

            # Seleccionar el nodo con menor p-valor, mayor peso y menor ID (criterio lexicográfico)
            next_node = candidates[0][2]
            added_nodes.append(next_node)
            cluster_nodes.add(next_node)

            # Actualizar la barra de progreso
            pbar.update(1)

    return added_nodes



# ------------------- EJECUCIÓN -------------------

if __name__ == "__main__":
    # Verificar que se pasen exactamente 5 argumentos (script + 5 parámetros)
    if len(sys.argv) != 6:
        print("Uso: python diamond.py <archivo_genes_string> <archivo_red> <num_genes_diamond> <alpha> <archivo_salida>")
        sys.exit("Error: número incorrecto de parámetros.")

    # Asignación de argumentos
    seed_file = sys.argv[1]       # Archivo con genes de semilla
    network_file = sys.argv[2]    # Archivo de la red
    num_diamond_genes = int(sys.argv[3])  # Número de genes a agregar (asegurar que sea un entero)
    alpha = float(sys.argv[4])    # Alpha (convertirlo a flotante)
    output_file = sys.argv[5]     # Archivo de salida para la red propagada

    # Leer red y genes de semilla
    G, seed_genes = read_input(network_file, seed_file)

    # Ejecutar DIAMOnD
    diamond_genes = diamond_iteration_of_first_X_nodes(G, seed_genes, num_diamond_genes, alpha)

    # Eliminar el prefijo de los genes de DIAMOnD
    diamond_genes_clean = [gene.split('.')[1] for gene in diamond_genes]

    # Guardar los genes propagados en un archivo
    with open(output_file, 'w') as f_out:
        f_out.write("\n".join(seed_genes) + "\n")
        f_out.write("\n".join(diamond_genes_clean) + "\n")

    print(f"Genes propagados guardados en {output_file}")
