# Systematic Analysis of Instances with TIMES

This repository contains a Python script (`run.py`) designed to perform a systematic analysis of a set of instances using the [TIMES source code](https://github.com/etsap-TIMES/TIMES_model). The script processes instance data, generates benchmark statistics, and compares results against a ground truth from a previous run.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Configuration](#configuration)
- [Output](#output)
- [Contributing](#contributing)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. Ensure you have Python installed (Python 3.6 or higher).

3. Install necessary dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. **Choose a Solve Mode**:
    Choose your `solvemode` from
    1. `SOLVE`: 
        - Runs and solves all instances and generates a [savepoint file](https://www.gams.com/latest/docs/UG_GamsCall.html#GAMSAOsavepoint) `TIMES_p.gdx` in the output directory.
        - The savepoint file contains the information on the current solution point can be used to skip the solve of a future run to save time.
    2. `LOADSOLUTION`:
        - Requires a savepoint file (`TIMES_p.gdx`) in the output directory.
        - Loads information from a previous solve instead of resolving the model.

2. **Prepare Instance Data**:
   Place your instance data into subfolders within the `data` directory. Each subfolder should contain the relevant data for an instance.

   Add all instances you want to analyze to the `instances` list where each tuple contains `(<folder_name>,<run_file>)`:
    ```python
    instances = [
        ("Instance_1", "Instance_1.RUN"),
        ("Instance_2", "Instance_2.RUN"),
    ]
    ```

1. **Specify TIMES Source Code Location**:
   In the `run.py` script, set the path to the [TIMES source code](https://github.com/etsap-TIMES/TIMES_model). Modify the following line:
   ```python
   TIMES_SOURCE_PATH = '/path/to/times/source'
   ```

3. **Run the Script**:
   Execute the script to start the analysis:
   ```sh
   python run.py
   ```

## File Structure

- `run.py`: The main script for performing the analysis.
- `summarize_results.py`: Script for analyzing output files and writing statistics.
- `data/`: Directory where instance data subfolders are placed.
- `output/`: Directory where log and profile files are written.
- `ground_truth_result_overview.csv`: CSV file containing results from a previous run for comparison.
- `results_overview.csv`: CSV file containing results from the latest run of `run.py`.
- `results.md`: Markdown file generated with benchmark statistics and analysis. Compares `ground_truth_result_overview.csv` and `results_overview.csv`.

## Configuration

Ensure the following configurations are set in `run.py` before running the script:

- `TIMES_SOURCE_PATH`: Path to the TIMES source code.
- Data directory structure should be maintained as specified.
- `instances`: List of tuples containing instances subject to analyses.
- `solvemode`: Mode of solving (solve vs skip solve)

## Output

The script generates several outputs:
- **.log, .lst and Profile Files**: Written to subfolders within the `output` directory.
- **Comparison to Ground Truth**: A markdown file (`results.md`) with statistics on all analyzed results.
- **Benchmark Results**: A CSV file (`results_overview.csv`) containing statistics from the latest run.
- **Profile Summary**: A markdown file (`profile_summary.md`) with detailed run times for GAMS assignments or equations.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

---

Feel free to reach out if you have any questions or need further assistance!

Happy analyzing!
