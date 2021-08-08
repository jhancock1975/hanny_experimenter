import numpy as np
import json
import copy
import re
import os

def capitalize(s:str) -> str:
    """
    make first letter of s upper case
    :param s: string
    :return: s with first letter capitalized
    """
    return s[0].upper()+s[1:]

def space_underscores(s):
    """
    replace underscores with spaces
    separate function to keep f strings
    from getting too long
    :param s: a string
    :return: s with underscores replaced with spaces
    """
    return s.replace("_", " ")

def escape_underscores(s):
    """
    escape underscores with back slashes
    separate function to keep f strings
    from getting too long
    :param s: a string
    :return: s with underscores prefixed with back slashes
    """
    return s.replace("_", "\_")

def proper_form(s:str)->str:
    """
    return properly formed string for 
    metric to be consistent, for example a_prc->AUPRC
    since in papers & other official documents we abbreviate 
    "area under the precison recall curve" as AUPRC
    :parm s: any string
    :return: proper form of input value if we know it, the input value unchanged if not
    """
    if s == "a_prc":
        return "\\ac{AUPRC}"
    elif s == "auc":
        return "\\ac{AUC}"
    elif s == "acc":
        return "accuracy"
    else:
        return s
def englishify(l:object)->str:
    """
    convert list to string
    separating elements by commas
    except for between the last two elements
    which are separated by the word and
    """
    ll = copy.deepcopy(l)
    for i in range(len(ll)):
        ll[i] = proper_form(ll[i])
    return ', '.join(list(map(str, ll)))[::-1].replace(',', ' dna ', 1)[::-1]

def acc_from_cm(cm: object)->float:
    """
    calculate accuracy from confusion matrix
    :param cm: confusion matrix
    :return: accuracy
    """
    tp = cm[0][0]
    fp = cm[0][1]
    fn = cm[1][0]
    tn = cm[1][1]
    return (tp + tn)/(tp + tn + fp + fn)

def format_number(x):
    """
    return in LaTeX scientific notation if very small or very close
    to one
    :param x: number to format
    :return: string
    """
    # caught this issue formatting
    # results from sample data
    assert not np.isnan(x), 'encountered NaN metric'
    def py_sci_to_latex(x):
        arr = x.split("E")
        return f'${arr[0]} \\times 10^{{{arr[1]}}}$'
    if (x < 1E-5):
        return py_sci_to_latex(f'{x:.5E}')
    else:
        return f'{round(x, 5):.5f}'

def cross_validation_results_table(results_dict: object, metrics_list: object, exp_title=None, shorten_func=None, exp_subtitle=None, long_exp_names=False)->None:
    """
    print mean values of results_dict
    in LaTeX format
    :param results_dict: dictionary of dictionary of results
    :param metrics_list: list of metrics to tabulate, currently supported:
      'auc' for accuracy, 'a_prc' for area under precision recall curve, 'acc' for accuracy
    :return: string holding contents of LaTeX table
    """
    if not shorten_func:
        # define an identity function if
        # shorten_func not specified
        def shorten_func(s):
            return s
    for clf_name, results_files in results_dict.items():
        # LaTeX table boilerplate
        table_str = '\\bgroup'
        table_str += '\\begin{table}[H]\n'
        table_str += '\t\\centering\n'
        table_str += f'\t\\caption{{{exp_title if exp_title else ""}; \n'
        table_str += f'\tMean and standard deviations of {englishify(metrics_list)}, \n'
        table_str += '\t(10 iterations of 5-fold cross-validation)}\n'
        # wrap long exp names
        if long_exp_names == True:
            first_col = 'p{2in}'
        else:
            first_col = 'l'
        alignment_chars = 'c'*(2*len(metrics_list))
        table_str += f'\t\\begin{{tabular}}{{{first_col}{alignment_chars}}} \\toprule\n'
        # table header
        table_str += '\tExperiment Name'
        for metric in metrics_list:
            table_str += ' & Mean  & \\ac{SD}'
        table_str += '\\\\ \n'
        for metric in metrics_list:
                table_str += f' & {proper_form(metric)} & {proper_form(metric)}'
        table_str += '\\\\ \\midrule\n'
        # compute mean values of metrics and put them
        # on rows
        for file_name in results_files:
            with open(file_name, 'r') as f:
                j = json.loads(f.read())
            metrics_dict = {}
            for exp_name, exp_data in j.items():
                for metric in metrics_list:
                    metrics_dict[metric] = []
                for iter_num, iter_data in exp_data['results_data'].items():
                    for fold_num, fold_data in iter_data.items():
                        for metric in metrics_list:
                            if metric == 'acc':
                                # calculate accuracy from confusion matrix
                                metrics_dict[metric].append(acc_from_cm(fold_data['cm']))
                            else:
                                metrics_dict[metric].append(fold_data[metric])
                if len(metrics_dict[metric]) != 50:
                    # something is not right if we get more than 50 measurements in a file
                    raise Exception(f'found results with more than 50 measurements in {file_name}')
                table_str += f'\t\t{space_underscores(shorten_func(exp_name))}'
                for metric in metrics_list:
                    table_str +=  f'& {format_number(np.mean(metrics_dict[metric]))} & {format_number(np.std(metrics_dict[metric]))}'
                table_str += '\\\\ \\midrule\n'

        table_str += '\t\\end{tabular}\n'
        table_str += f'\t\label{{tab:mean_{metric}_for_{clf_name.replace(" ","_")}_exp}} \n'
        if exp_subtitle:
            table_str += f"\\flushleft{exp_subtitle}"
        table_str += '\\end{table}\n'
        table_str += '\\egroup'
        return table_str

def find_max_metric_by_clf(dir_name, metric_name, clf_names, output_file_name, file_name_pattern=None):
    """
    return list of files that has max metric by key in max_by_key_dict
    :param dir_name: directory of results files
    :param metric_name: name of metric to search for max valuee of, e.g. auc au_prc
    :param file_name_pattern: filter files to search, e.g. *default*none*agree*
    :param max_by_key_dict: keys to search for results for, for example mlp, cp, dt (classifier names
    :result: list of files that can be passed to merge_results.merge_dicts and then cross_validation_results_table
    """
    if file_name_pattern:
        file_list = [f for f in os.listdir(dir_name) if file_name_pattern.match(f)]
    else:
        file_list = [f for f in os.listdir(dir_name)]
    max_by_key_dict = {clf_name: None for clf_name in clf_names}
    for  search_key in max_by_key_dict.keys():
        for f_name in file_list:
            with open(os.path.join(dir_name, f_name), 'r') as f:
                d = json.loads(f.read())
                for k, v in d.items():
                    # we have been saving results in json file where
                    # top level format has key that is experiment name
                    # that is the file name without the .json extension
                    # and the value is the results data
                    if search_key in f_name:
                        results_data = v['results_data']
                        metric_mean = np.mean([results_data[str(i)][str(j)][metric_name]
                                               for i in range(1, len(results_data) + 1)
                                               for j in range(1, len(results_data[str(i)]) + 1)])
                        try:
                            if metric_mean > max_by_key_dict[search_key]['metric_mean']:
                                max_by_key_dict[search_key]['metric_mean'] = metric_mean
                                max_by_key_dict[search_key]['file_name'] = f_name
                        except TypeError as te:
                            max_by_key_dict[search_key] = {'metric_mean' :metric_mean,
                                                           'file_name': f_name}

    res_dict = { output_file_name: []}
    for k,v in max_by_key_dict.items():
        res_dict[output_file_name].append(os.path.join(dir_name, v['file_name']))
    return res_dict
                    

