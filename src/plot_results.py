import csv
import os
import importlib
plt = importlib.import_module("matplotlib.pyplot")

RESULTS_DIR = "results"
PLOTS_DIR = "plots"
SCALING_CSV = os.path.join(RESULTS_DIR, "scaling_results.csv")
SCHEDULING_CSV = os.path.join(RESULTS_DIR, "scheduling_results.csv")
INPUT_CSV = os.path.join(RESULTS_DIR, "input_scaling_results.csv")

def plot_speedup():
    threads, times = [], []
    if not os.path.exists(SCALING_CSV): return
    with open(SCALING_CSV, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Algorithm'] == 'OpenMP':
                threads.append(int(row['Threads']))
                times.append(float(row['Time_s']))
    if not times: return
    
    t1 = times[0]
    speedups = [t1 / t for t in times]

    plt.figure(figsize=(8, 5))
    plt.plot(threads, speedups, marker='o', linestyle='-', linewidth=2, color='#1f77b4', label='Speedup Reale')
    plt.plot(threads, threads, linestyle='--', color='gray', label='Speedup Ideale (Lineare)')
    plt.title('Strong Scaling: Curva di Speedup', fontsize=12, fontweight='bold')
    plt.xlabel('Numero di Thread (p)', fontsize=10)
    plt.ylabel('Speedup (Sp)', fontsize=10)
    plt.xticks(threads)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend()
    plt.savefig(os.path.join(PLOTS_DIR, "speedup_curve.png"), dpi=300, bbox_inches='tight')
    plt.close()

def plot_algorithm_comparison():
    algos, times = [], []
    if not os.path.exists(SCALING_CSV): return
    with open(SCALING_CSV, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['Threads']) == 1:
                algos.append(row['Algorithm'])
                times.append(float(row['Time_s']))
    if not times: return

    plt.figure(figsize=(7, 5))
    colors = ['#ff9896', '#aec7e8', '#98df8a']
    bars = plt.bar(algos, times, color=colors[:len(algos)], edgecolor='black', alpha=0.85)
    plt.title('Confronto Architetturale (1 Thread)', fontsize=12, fontweight='bold')
    plt.xlabel('Versione Algoritmo', fontsize=10)
    plt.ylabel('Tempo di Esecuzione (s)', fontsize=10)
    plt.grid(axis='y', linestyle=':', alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, f"{yval:.2f}s", ha='center', va='bottom', fontsize=9)

    plt.savefig(os.path.join(PLOTS_DIR, "algorithm_comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()

def plot_input_scaling():
    sizes, times = [], []
    if not os.path.exists(INPUT_CSV): return
    with open(INPUT_CSV, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sizes.append(int(row['Dataset_Size']))
            times.append(float(row['Time_s']))
    if not times: return

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, times, marker='s', linestyle='-', linewidth=2, color='#ff7f0e')
    plt.title('Complessità Temporale al variare della Taglia', fontsize=12, fontweight='bold')
    plt.xlabel('Numero di Elementi della Serie Storica', fontsize=10)
    plt.ylabel('Tempo di Esecuzione (s)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.savefig(os.path.join(PLOTS_DIR, "input_scaling_curve.png"), dpi=300, bbox_inches='tight')
    plt.close()

def plot_scheduling():
    schedules, times = [], []
    if not os.path.exists(SCHEDULING_CSV): return
    with open(SCHEDULING_CSV, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            schedules.append(row['Schedule'])
            times.append(float(row['Time_s']))
    if not times: return

    plt.figure(figsize=(9, 5))
    colors = ['#aec7e8', '#ffbb78', '#98df8a', '#ff9896']
    bars = plt.bar(schedules, times, color=colors[:len(schedules)], edgecolor='black', alpha=0.85)
    plt.title('Confronto Politiche di Scheduling (8 Threads)', fontsize=12, fontweight='bold')
    plt.xlabel('Politica e Dimensione Chunk', fontsize=10)
    plt.ylabel('Tempo di Esecuzione (s)', fontsize=10)
    plt.grid(axis='y', linestyle=':', alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"{yval:.2f}s", ha='center', va='bottom', fontsize=9)

    plt.savefig(os.path.join(PLOTS_DIR, "scheduling_comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    os.makedirs(PLOTS_DIR, exist_ok=True)
    print("Generazione avanzata dei grafici in corso...")
    plot_speedup()
    plot_algorithm_comparison()
    plot_input_scaling()
    plot_scheduling()
    print("Tutti i grafici sono stati generati con successo!")