#!/bin/bash
set -e

echo "=== 1. Compilazione del programma C++ ==="
clang++ -O3 -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib src/main.cpp -o sad_simd -lomp
echo "Compilazione completata."

mkdir -p results
SCALING_CSV="results/scaling_results.csv"
SCHEDULING_CSV="results/scheduling_results.csv"
INPUT_CSV="results/input_scaling_results.csv"

echo "Algorithm,Threads,Schedule,Time_s" > $SCALING_CSV
echo "Algorithm,Threads,Schedule,Time_s" > $SCHEDULING_CSV
echo "Dataset_Size,Time_s" > $INPUT_CSV

echo ""
echo "=== 2. Esecuzione Benchmark: Baseline (1 Thread) ==="
./sad_simd 0 1 150 >> $SCALING_CSV
./sad_simd 1 1 150 >> $SCALING_CSV

echo ""
echo "=== 3. Esecuzione Benchmark: Strong Scaling (OpenMP) ==="
export OMP_SCHEDULE="static"
for THREADS in 1 2 4 8; do
    echo "Test con $THREADS thread(s)..."
    ./sad_simd 2 $THREADS 150 >> $SCALING_CSV
done

echo ""
echo "=== 4. Esecuzione Benchmark: Input Size Scaling (SIMD, 1 Thread) ==="
# Testiamo diverse replicazioni del dataset (es. 50x, 100x, 150x, 200x)
for REP in 50 100 150 200; do
    echo "Test dimensione dataset con $REP repliche..."
    # Eseguiamo il programma in modalità SIMD catturando l'output personalizzato per la taglia
    OUTPUT=$(./sad_simd 1 1 $REP)
    # Calcoliamo approssimativamente gli elementi (ogni replica base ha ~405k elementi)
    SIZE=$((REP * 405184))
    TIME=$(echo $OUTPUT | cut -d',' -f4)
    echo "$SIZE,$TIME" >> $INPUT_CSV
done

echo ""
echo "=== 5. Esecuzione Benchmark: Load Balancing (8 Threads) ==="
for SCHED in "static" "static,1000" "dynamic,1000" "guided"; do
    echo "Test scheduling: $SCHED"
    export OMP_SCHEDULE="$SCHED"
    ./sad_simd 2 8 150 >> $SCHEDULING_CSV
done

echo ""
echo "=== 6. Generazione Automatica dei Grafici ==="
python3 src/plot_results.py

echo ""
echo "=== PIPELINE COMPLETATA ==="