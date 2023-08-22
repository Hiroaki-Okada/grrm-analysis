# Analysis of GRRM log files

## Overview
Source code to analyze GRRM log files.

## Scripts
### cut_AFIR_path_for_LUP.py
Cut out specified regions of the AFIR path to reduce the cost of LUP calculations.

### gen_xyz_from_opt_log.py
Generate an xyz file (for Chemcraft) from a ITR of GRRM log file. FrozenAtoms are also written.

### gen_xyz_from_IRC_path.py
Generate an xyz file (for Chemcraft) from a IRC path of GRRM log file.

### gen_xyz_file_of_last_itr_of_each_opt_log.py
Generate an xyz file (for Chemcraft) of the structure of the last iteration of each GRRM log file and display the results of the interatomic distance analysis.