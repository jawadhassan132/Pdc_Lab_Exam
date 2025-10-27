# Parallel and Distributed Image Processing

**Student ID:** SP22-BCS-132  
**Course:** Parallel & Distributed Computing  


## Project Overview

This project implements image preprocessing using three different approaches: sequential, parallel, and distributed processing. The goal is to demonstrate performance improvements through parallelism and understand the trade-offs between different parallel computing strategies.

## Dataset

- **Total Images:** 94
- **Classes:** 4 (cars, Cat, dogs, Flowers)
- **Operations:** Resize to 128x128 pixels and add watermark

## Project Structure

```
├── Dataset/
│   ├── cars/
│   ├── Cat/
│   ├── dogs/
│   └── Flowers/
├── sequential_process.py       # Task 1: Sequential implementation
├── parallel_process.py          # Task 2: Parallel processing (multiprocessing)
├── distributed_sim.py           # Task 3: Distributed simulation
├── output_seq/                  # Sequential output
├── output_parallel/             # Parallel output
├── output_distributed/          # Distributed output
├── sample_output/               # Sample processed images
├── requirements.txt             # Python dependencies
└── report.txt                   # Performance analysis report
```

## Requirements

- Python 3.7+
- Pillow (PIL)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Task 1: Sequential Processing
```bash
python sequential_process.py
```
Processes all images sequentially and outputs to `output_seq/` folder.

### Task 2: Parallel Processing
```bash
python parallel_process.py
```
Tests parallel processing with 1, 2, 4, and 8 workers using multiprocessing.Pool. Outputs to `output_parallel/` folder.

### Task 3: Distributed Processing
```bash
python distributed_sim.py
```
Simulates distributed environment with 2 nodes processing images independently. Outputs to `output_distributed/` folder.

## Performance Results

| Approach | Workers | Time (s) | Speedup | Efficiency |
|----------|---------|----------|---------|------------|
| Sequential | 1 | 0.69 | 1.00x | 100.00% |
| Parallel | 2 | 0.47 | 1.47x | 73.29% |
| Parallel | 4 | 0.38 | 1.82x | 45.40% |
| Parallel | 8 | 0.54 | 1.28x | 16.03% |
| Distributed | 2 nodes | 0.5 | ~1.6x | ~80.00% |

**Best Configuration:** 4 workers with 1.82x speedup

## Key Findings

1. **Optimal Worker Count:** 4 workers provided the best performance for this dataset size
2. **Overhead Impact:** 8 workers showed decreased performance due to parallel overhead exceeding benefits
3. **Distributed Potential:** 2-node distributed approach shows promise for larger-scale deployments
4. **Bottlenecks:** Small dataset size, I/O contention, and process creation overhead limit scalability

## Technical Implementation

- **Sequential:** Single-threaded baseline implementation
- **Parallel:** Uses `multiprocessing.Pool` for true multi-core parallelism
- **Distributed:** Simulates distributed nodes using separate processes with Queue-based communication

All approaches use Pillow for image operations and maintain consistent output quality.

## Report

Detailed performance analysis and discussion of bottlenecks available in `report.txt`.

## Author

**SP22-BCS-132**  
Parallel & Distributed Computing - Mid Lab Exam  
8th Semester