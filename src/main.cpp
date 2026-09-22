#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <cmath>
#include <chrono>
#include <limits>
#include <omp.h>
#include <cstdlib>

std::vector<double> load_time_series(const std::string& filename) {
    std::vector<double> series;
    std::ifstream file(filename);
    std::string line;
    if (!file.is_open()) return series;
    while (std::getline(file, line)) {
        try { series.push_back(std::stod(line)); } catch (...) { continue; }
    }
    return series;
}

// Le funzioni ora restituiscono il double calcolato per evitare la Dead Code Elimination
double run_naive(const double* series, const double* pattern, size_t n, size_t m) {
    double min_sad = std::numeric_limits<double>::max();
    for (size_t i = 0; i <= n - m; ++i) {
        double current_sad = 0.0;
        for (size_t j = 0; j < m; ++j) {
            current_sad += std::abs(series[i + j] - pattern[j]);
        }
        if (current_sad < min_sad) min_sad = current_sad;
    }
    return min_sad;
}

double run_simd(const double* __restrict__ series, const double* __restrict__ pattern, size_t n, size_t m) {
    double min_sad = std::numeric_limits<double>::max();
    for (size_t i = 0; i <= n - m; ++i) {
        double current_sad = 0.0;
        #pragma omp simd reduction(+:current_sad)
        for (size_t j = 0; j < m; ++j) {
            current_sad += std::abs(series[i + j] - pattern[j]);
        }
        if (current_sad < min_sad) min_sad = current_sad;
    }
    return min_sad;
}

double run_omp(const double* __restrict__ series, const double* __restrict__ pattern, size_t n, size_t m) {
    double global_min_sad = std::numeric_limits<double>::max();
    #pragma omp parallel
    {
        double local_min_sad = std::numeric_limits<double>::max();
        
        #pragma omp for schedule(runtime)
        for (size_t i = 0; i <= n - m; ++i) {
            double current_sad = 0.0;
            #pragma omp simd reduction(+:current_sad)
            for (size_t j = 0; j < m; ++j) {
                current_sad += std::abs(series[i + j] - pattern[j]);
            }
            if (current_sad < local_min_sad) local_min_sad = current_sad;
        }
        #pragma omp critical
        {
            if (local_min_sad < global_min_sad) global_min_sad = local_min_sad;
        }
    }
    return global_min_sad;
}

int main(int argc, char *argv[]) {
    int mode = 2; 
    int num_threads = 4;
    
    if (argc > 1) mode = std::stoi(argv[1]);
    if (argc > 2) num_threads = std::stoi(argv[2]);
    
    omp_set_num_threads(num_threads);

    std::vector<double> time_series_original = load_time_series("data/serie_storica.csv");
    std::vector<double> pattern = load_time_series("data/pattern.csv");
    if (time_series_original.empty() || pattern.empty()) return 1;

    std::vector<double> time_series;
    int replications = 150; 
    for(int i = 0; i < replications; ++i) {
        time_series.insert(time_series.end(), time_series_original.begin(), time_series_original.end());
    }

    size_t n = time_series.size();
    size_t m = pattern.size();
    const double* s_ptr = time_series.data();
    const double* p_ptr = pattern.data();

    // L'uso di volatile obbliga il compilatore a eseguire il calcolo per poterlo salvare in memoria
    volatile double dummy_result = 0.0;

    auto start_time = std::chrono::high_resolution_clock::now();
    
    if (mode == 0) dummy_result = run_naive(s_ptr, p_ptr, n, m);
    else if (mode == 1) dummy_result = run_simd(s_ptr, p_ptr, n, m);
    else if (mode == 2) dummy_result = run_omp(s_ptr, p_ptr, n, m);
    
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> execution_time = end_time - start_time;
    
    const char* env_schedule = std::getenv("OMP_SCHEDULE");
    std::string sched_str = env_schedule ? env_schedule : "default";
    std::string mode_str = (mode == 0) ? "Naive" : (mode == 1) ? "SIMD" : "OpenMP";
    
    // Stampa: aggiunte le virgolette a sched_str per evitare il troncamento sul CSV
    std::cout << mode_str << "," << num_threads << ",\"" << sched_str << "\"," << execution_time.count() << std::endl;

    return 0;
}