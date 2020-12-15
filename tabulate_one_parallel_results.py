import numpy as np
import json

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
    metric to be consistent, for example a_prc->AU PRC
    since in papers & other official documents we abbreviate 
    "area under the precison recall curve" as AU PRC
    :parm s: any string
    :return: proper form of input value if we know it, the input value unchanged if not
    """
    if s == "a_prc":
        return "\\ac{AU PRC}"
    elif s == "auc":
        return "\\ac{AUC}"
    else:
        return s
def englishify(l:object)->str:
    """
    convert list to string
    separating elements by commas
    except for between the last two elements
    which are separated by the word and
    """
    return ', '.join(list(map(str, l)))[::-1].replace(',', ' dna ', 1)[::-1]

def cross_validation_results_table(results_dict: object, metrics_list: object)->None:
    """
    print mean values of results_dict
    in LaTeX format
    :param results_dict: dictionary of dictionary of results
    :param metrics_list: list of metrics to tabulate, 'auc', 'a_prc', etc.
    :return: string holding contents of LaTeX table
    """
    for clf_name, results_files in results_dict.items():
        # LaTeX table boilerplate
        table_str = '\\bgroup'
        table_str += '\\begin{table}[H]\n'
        table_str += '\t\\centering\n'
        table_str += '\t\\begin{tabular}{p{2in}cccc} \\toprule\n'
        # table header
        table_str += '\tExperiment Name'
        for metric in metrics_list:
            table_str += f' & Mean {proper_form(metric)} & \\ac{{SD}} {proper_form(metric)}'
        table_str += '\\\\ \\hline\n'
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
                            metrics_dict[metric].append(fold_data[metric])
                if len(metrics_dict[metric]) != 50:
                    # something is not right if we get more than 50 measurements in a file
                    raise Exception(f'found results with more than 50 measurements in {file_name}')
                table_str += f'\t\t{space_underscores(exp_name)}'
                for metric in metrics_list:
                    table_str +=  f'& {round(np.mean(metrics_dict[metric]),5):.5f} & {round(np.std(metrics_dict[metric]),5):.5f}'
                table_str += '\\\\ \\hline\n'

        table_str += '\t\\bottomrule\n\t\\end{tabular}\n'
        table_str += f'\t\\caption{{Mean and standard deviations of {englishify(metrics_list)}, \n'
        table_str += '\tfor 10 iterations of 5-fold cross-validation}\n'
        table_str += f'\t\label{{tab:mean_auc_for_{clf_name.replace(" ","_")}_exp}}\n'
        table_str += '\\end{table}\n'
        table_str += '\\egroup'
        print(table_str)
        return table_str
