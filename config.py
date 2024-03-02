#import operating system library
import os

#obtain the general path/current one
path_notebook = os.getcwd()
path_notebook_backwards = os.path.dirname(path_notebook)
general_path = os.path.dirname(path_notebook_backwards)

# -- PATH FOR DATA
path_raw_data = os.path.join(general_path, r"data", r"1_raw_data")
path_indicators_processed = os.path.join(general_path, r"data", r"2_indicators_processed")
path_iteration_output = os.path.join(general_path, r"data", r"2_indicators_processed", r"iteration_output")
path_iteration_output_gamma = os.path.join(general_path, r"data", r"2_indicators_processed", r"iteration_output_gamma")
path_iteration_output_cmpoisson = os.path.join(general_path, r"data", r"2_indicators_processed", r"iteration_output_cmpoisson")
path_control_limits = os.path.join(general_path, r"data", r"3_control_limit")
path_confusion_matrices = os.path.join(general_path, r"data", r"4_confusion_matrices")
path_performance_indicators = os.path.join(general_path, r"data", r"5_performance_indicators")
path_results = os.path.join(general_path, r"data", r"6_results")

# -- PATH FOR NOTEBOOKS
path_nb_monte_carlo_simulator = os.path.join(general_path, r"notebooks", r'1_monte_carlo_simulator')
path_nb_calculate_control_limits = os.path.join(general_path, r"notebooks", r'2_calculate_control_limits')
path_nb_create_confusion_matrix = os.path.join(general_path, r"notebooks", r'3_create_confusion_matrix')
path_nb_calculate_performance_indicators = os.path.join(general_path, r"notebooks", r'4_calculate_performance_indicators')

# -- PATH FOR SCRIPTS
path_monte_carlo_simulator = os.path.join(general_path, r"scripts", r'1_monte_carlo_simulator')
path_calculate_control_limits = os.path.join(general_path, r"scripts", r'2_calculate_control_limits')
path_create_confusion_matrix = os.path.join(general_path, r"scripts", r'3_create_confusion_matrix')
path_calculate_performance_indicators = os.path.join(general_path, r"scripts", r'4_calculate_performance_indicators')
