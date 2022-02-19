import json
import statistics
import os
from tabulate_one_parallel_results import proper_form
"""
 hyperparameter tuning is a requirement for for every case study
"""

table_start = """
\\bgroup\\begin{{table}}[H]
  \\centering
    \\begin{{tabular}}{{ll}} \\toprule
"""

table_end="""
    \\end{{tabular}}
    \\caption{{Modes of {classifier} tuned hyperparameter values for experiments with the {experiment_name} dataset{none_msg}; 
    parameter values for classifier yielding best results in terms of {metric} }}
  \\label{{{label}}}
  \\end{{table}}
\\egroup"""

def get_end_hyperp_table(k, output_file_name, metric, needs_none_msg, file2exp_name=None):
    if needs_none_msg:
        none_msg = """; ``None'' value indicates default value of hyperparameter is optimal"""
    else:
        none_msg = ''
    if file2exp_name:
        experiment_name = file2exp_name(output_file_name)
    else:
        experiment_name = output_file_name
    return table_end.format(label=f"tab:{k}_{output_file_name}",
                                experiment_name=experiment_name, classifier=get_clf(k),
                            none_msg=none_msg, metric=proper_form(metric))
def escape_underscores(s):
    if type(s) is str:
        return s.replace('_', '\\_')
    else:
        return s

def num_format(s):
    if type(s) is float:
        return f'{s:.5f}'
    else:
        return s

def get_clf(s):
    if 'cb' in s:
        return 'CatBoost'
    elif 'dt' in s:
        return 'DT'
    elif 'lgb' in s:
        return 'LightGBM'
    elif 'lightgbm' in s:
        return 'LightGBM'
    elif  'lr' in s:
        return 'LR'
    elif 'mlp' in s:
        return 'MLP'
    elif 'nb' in s:
        return  'NB'
    elif 'rf' in s:
        return 'RF'
    elif 'xgboost':
        return 'XGBoost'

def empty_to_none(param_mode):
    """
    noticed some tuned hyperparameters
    come back as {}
    change to None for consistency
    """
    try:
        if len(eval(param_mode) ) == 0:
            return 'None'
        else:
            return param_mode
    except:
        return param_mode

def get_best_params_from_results_file(input_file_name, metric, output_file_location=None, file2exp_name=None):
    """parses results file for hyperparameter values
    then prints LaTeX table to a file with mode values
    for each hyperparameter
    :param input_file_name: name of results file
    :param output_file
    :return: string with LaTeX table and side effect file is
    written with same base name (sans extension) to directory
    specified in output_file_location 

    """
    with open(input_file_name, 'r') as f:
        d=json.loads(f.read())
    table_str = ''
    for k,v in d.items():
        table_str += table_start.format()
        table_str += f"\t\\textbf{{Paramater Name}} & \\textbf{{Value}} \\\\ \\midrule\n"
        params_d = {}
        for i in range(1, len(v) + 1):
            for j in range(1, len(v['results_data'][str(i)]) + 1):
                best_params  = v['results_data'][str(i)][str(j)]['best_params_']
                for k1, v1 in best_params.items():
                    try:
                        params_d[k1].append(v1)
                    except Exception as e:
                        params_d[k1] = [v1]
        needs_none_msg = False
        for k1,v1 in params_d.items():
            try:
                param_mode = num_format(statistics.mode(v1))
                param_mode = empty_to_none(param_mode)
                if 'None' in param_mode:
                    needs_none_msg = True
                table_str += f"\t{escape_underscores(k1)} & {escape_underscores(param_mode)} \\\\ \\midrule\n"
            except TypeError as e:
                str_list = list(map(str, v1))
                param_mode = escape_underscores(statistics.mode(str_list))
                param_mode = empty_to_none(param_mode)                                                   
                if 'None' in param_mode:
                    needs_none_msg = True
                table_str += f"\t{escape_underscores(k1)} & {param_mode} \\\\ \\midrule\n"
        table_str += get_end_hyperp_table(k, input_file_name, metric, needs_none_msg, file2exp_name = file2exp_name)
    if output_file_location:
        output_base_name = input_file_name.replace('.json', f'_{metric}_')
        output_file_name = f'{os.path.join(output_file_location, os.path.basename(output_base_name))}_best_tuned_params.tex'
        with open(output_file_name, 'w') as f:
            f.write(table_str)
    return table_str
                
