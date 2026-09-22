#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <cmath>
#include <chrono>
#include <limits>
#include <omp.h>

// Funzione per caricare una serie temporale da un file CSV
std::vector<double> load_time_series(const std::string& filename) {
    std::vector<double> series;
    std::ifstream file(filename);
    std::string line;
    
    if (!file.is_open()) {
        std::cerr << "Errore: impossibile aprire il file " << filename << std::endl;
        return series;
    }

    while (std::getline(file, line)) {
        try {
            series.push_back(std::stod(line));
        } catch (const std::invalid_argument& e) {
            continue;
        }
    }
    file.close();
    return series;
}

// Implementazione parallela della ricerca pattern tramite sliding window e SAD
std::pair<size_t, double> find_best_pattern_match_sad(const std::vector<double>& series_vec, const std::vector<double>& pattern_vec) {
    size_t n = series_vec.size();
    size_t m = pattern_vec.size();
    
    if (m == 0 || n < m) return {0, -1.0};

    const double* __restrict__ series = series_vec.data();
    const double* __restrict__ pattern = pattern_vec.data();

    double global_min_sad = std::numeric_limits<double>::max();
    size_t global_best_index = 0;

    #pragma omp parallel
    {
        double local_min_sad = std::numeric_limits<double>::max();
        size_t local_best_index = 0;

        #pragma omp for schedule(dynamic)
        for (size_t i = 0; i <= n - m; ++i) {
            double current_sad = 0.0;
            
            #pragma omp simd reduction(+:current_sad)
            for (size_t j = 0; j < m; ++j) {
                current_sad += std::abs(series[i + j] - pattern[j]);
            }
            
            if (current_sad < local_min_sad) {
                local_min_sad = current_sad;
                local_best_index = i;
            }
        }

        #pragma omp critical
        {
            if (local_min_sad < global_min_sad) {
                global_min_sad = local_min_sad;
                global_best_index = local_best_index;
            }
        }
    }

    return {global_best_index, global_min_sad};
}

int main(int argc, char *argv[]) {
    // Gestione del parametro thread da terminale
    int num_threads = 4; // default
    if (argc > 1) {
        num_threads = std::stoi(argv[1]);
    }
    omp_set_num_threads(num_threads);

    std::string series_path = "data/serie_storica.csv";
    std::string pattern_path = "data/pattern.csv";

    // FASE 1: I/O (Esclusa)
    std::vector<double> time_series_original = load_time_series(series_path);
    std::vector<double> pattern = load_time_series(pattern_path);

    if (time_series_original.empty() || pattern.empty()) {
        std::cerr << "I dataset sono vuoti o non trovati." << std::endl;
        return 1;
    }

    std::vector<double> time_series;
    int replications = 150; 
    for(int i = 0; i < replications; ++i) {
        time_series.insert(time_series.end(), time_series_original.begin(), time_series_original.end());
    }

    // FASE 2: Calcolo puro
    auto start_time = std::chrono::high_resolution_clock::now();
    
    std::pair<size_t, double> result = find_best_pattern_match_sad(time_series, pattern);
    
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> execution_time = end_time - start_time;
    
    // Stampa compatta: Num_Threads, Tempo_Esecuzione
    std::cout << num_threads << "," << execution_time.count() << std::endl;

    return 0;
}