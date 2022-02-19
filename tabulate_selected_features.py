import json
import os
import re

table_start = """
% feature rankings copied from file  {input_file_name}
\\bgroup\\begin{{table}}[H]
  \\centering
    \\begin{{tabular}}{{ll}} \\toprule
"""

table_end="""
    \\end{{tabular}}
    \\caption{{ {caption} }}
  \\label{{{label}}}
  \\end{{table}}
\\egroup"""

def escape_underscores(s):
    """
    separated to reduce code clutter
    """
    return s.replace("_", "\\_")

def get_next(t, i):
    try:
        next_t = f'{escape_underscores(t[i])} '
    except IndexError as ie:
        next_t = '  '
    return next_t
    
def print_fs_tables(t1, t2):
    table_str = ''
    max_i = max(len(t1), len(t2))
    for i in range(max_i):
        table_str += f'      {get_next(t1, i)} &  {get_next(t2,i)} \\\\ \\midrule\n'
    return table_str
        
def print_feature_selection_tables(input_file_name):
    """print feature selection tables from ensemble feature selection
    4 agree, 5 agree, 6 agree, 7, agree

    :param input_file_name: name of file containing feature rakings
    should be prodcued from do_feature_sel.py

    :return: output files name same as star of input
    file name with ...feature_raking_tables.tex as suffix
    """
    with open(input_file_name, 'r') as f:
        d = json.loads(f.read())
    table_str = ''
    for fs_exp_output_file_name, fs_lists in d.items():
        dataset_name = '-'.join(re.split('[_,\-]', os.path.basename(fs_exp_output_file_name))[:2])
        table_str += table_start.format(input_file_name=input_file_name)
        table_str += '4-Agree & 5-Agree \\\\ \\midrule'
        table_str += print_fs_tables(fs_lists['4_agree'], fs_lists['5_agree'])
        table_str += table_end.format(caption='Results of the 4-Agree and 5-Agree \\ac{FST}s',
                               label=f'tab:{dataset_name}_4_5_agree')
        table_str += '\n'
        table_str += table_start.format(input_file_name=input_file_name)
        table_str += '6-Agree & 7-Agree \\\\ \\midrule'
        table_str += print_fs_tables(fs_lists['6_agree'], fs_lists['7_agree'])
        table_str += table_end.format(caption='Results of the 6-Agree and 7-Agree \\ac{FST}s',
                               label=f'tab:{dataset_name}_6_7_agree')
        table_str += '\n'
    return table_str
            
