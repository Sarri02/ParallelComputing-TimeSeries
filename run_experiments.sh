#!/bin/bash

# Interrompi in caso di errore
set -e

echo "=== 1. Compilazione del programma C++ ==="
clang++ -O3 -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib src/main.cpp -o sad_simd -lomp
echo "Compilazione completata."

# Creazione cartella dei risultati
mkdir -p results
SCALING_CSV="results/scaling_results.csv"
SCHEDULING_CSV="results/scheduling_results.csv"

# Scrittura intestazioni dei CSV
echo "Algorithm,Threads,Schedule,Time_s" > $SCALING_CSV
echo "Algorithm,Threads,Schedule,Time_s" > $SCHEDULING_CSV

echo ""
echo "=== 2. Esecuzione Benchmark: Baseline (1 Thread) ==="
echo "Esecuzione Sequenziale Pura (Naive)..."
./sad_simd 0 1 >> $SCALING_CSV

echo "Esecuzione SIMD Singolo Core..."
./sad_simd 1 1 >> $SCALING_CSV

echo ""
echo "=== 3. Esecuzione Benchmark: Strong Scaling (OpenMP) ==="
export OMP_SCHEDULE="static"
for THREADS in 1 2 4 8; do
    echo "Test con $THREADS thread(s)..."
    ./sad_simd 2 $THREADS >> $SCALING_CSV
done

echo ""
echo "=== 4. Esecuzione Benchmark: Load Balancing & Scheduling (8 Threads) ==="
for SCHED in "static" "static,1000" "dynamic,1000" "guided"; do
    echo "Test scheduling: $SCHED"
    export OMP_SCHEDULE="$SCHED"
    ./sad_simd 2 8 >> $SCHEDULING_CSV
done

echo ""
echo "=== 5. Generazione Automatica dei Grafici ==="
# Verifica la presenza di python3 e matplotlib
if ! command -v python3 &> /dev/null; then
    echo "Errore: Python 3 non è installato."
    exit 1
fi

# Installa matplotlib se non presente nell'ambiente corrente
python3 -c "import matplotlib" 2>/dev/null || {
    echo "Libreria matplotlib non trovata. Installazione automatica tramite pip..."
    pip3 install matplotlib --break-system-packages
}

# Esegui lo script di plotting
python3 src/plot_results.py

echo ""
echo "=== PIPELINE COMPLETATA CON SUCCESSO ==="
echo "Trovi i grafici pronti all'uso nella cartella 'results/'."