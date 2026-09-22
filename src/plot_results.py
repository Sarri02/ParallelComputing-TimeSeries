import csv
import os
import matplotlib.pyplot as plt

RESULTS_DIR = "results"
SCALING_CSV = os.path.join(RESULTS_DIR, "scaling_results.csv")
SCHEDULING_CSV = os.path.join(RESULTS_DIR, "scheduling_results.csv")

def plot_scaling():
    threads = []
    times = []
    
    if not os.path.exists(SCALING_CSV):
        print(f"Errore: {SCALING_CSV} non trovato.")
        return

    with open(SCALING_CSV, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Algorithm'] == 'OpenMP':
                threads.append(int(row['Threads']))
                times.append(float(row['Time_s']))

    if not times:
        print("Nessun dato OpenMP trovato in scaling_results.csv")
        return

    # Calcolo dello Speedup Sp = t1 / tp
    t1 = times[0]
    speedups = [t1 / t for t in times]

    # Creazione del grafico di Speedup
    plt.figure(figsize=(8, 5))
    plt.plot(threads, speedups, marker='o', linestyle='-', linewidth=2, color='#1f77b4', label='Speedup Reale')
    plt.plot(threads, threads, linestyle='--', color='gray', label='Speedup Ideale (Lineare)')
    
    plt.title('Strong Scaling: Curva di Speedup (SAD Algorithm)', fontsize=12, fontweight='bold')
    plt.xlabel('Numero di Thread (p)', fontsize=10)
    plt.ylabel('Speedup (Sp)', fontsize=10)
    plt.xticks(threads)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend()
    
    output_path = os.path.join(RESULTS_DIR, "speedup_curve.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Grafico Speedup salvato in: {output_path}")

def plot_scheduling():
    schedules = []
    times = []

    if not os.path.exists(SCHEDULING_CSV):
        print(f"Errore: {SCHEDULING_CSV} non trovato.")
        return

    with open(SCHEDULING_CSV, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            schedules.append(row['Schedule'])
            times.append(float(row['Time_s']))

    if not times:
        print("Nessun dato trovato in scheduling_results.csv")
        return

    # Creazione dell'istogramma di confronto scheduling
    plt.figure(figsize=(9, 5))
    colors = ['#aec7e8', '#ffbb78', '#98df8a', '#ff9896']
    bars = plt.bar(schedules, times, color=colors[:len(schedules)], edgecolor='black', alpha=0.85)

    plt.title('Confronto Politiche di Scheduling (8 Threads)', fontsize=12, fontweight='bold')
    plt.xlabel('Politica e Dimensione Chunk', fontsize=10)
    plt.ylabel('Tempo di Esecuzione (s)', fontsize=10)
    plt.grid(axis='y', linestyle=':', alpha=0.7)

    # Aggiunta dei valori sopra le barre per leggibilità immediata
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"{yval:.2f}s", ha='center', va='bottom', fontsize=9)

    output_path = os.path.join(RESULTS_DIR, "scheduling_comparison.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Istogramma Scheduling salvato in: {output_path}")

if __name__ == "__main__":
    print("Generazione dei grafici in corso...")
    plot_scaling()
    plot_scheduling()
    print("Generazione completata con successo!")