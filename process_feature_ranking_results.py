#!/usr/bin/env python
import json
import re
import os

table_start = """
% feature rankings copied from file  {input_file_name}
\\bgroup\\begin{{table}}[H]
  \\centering
    \\begin{{tabular}}{{{align_chars}}} \\toprule
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

def proper_form(s):
    if 'information gain' in s:
        return s.replace('information gain', 'Information Gain')
    elif 'information gain ratio' in s:
        return s.replace('information gain ratio', 'Information Gain Ratio')
    elif 'chi 2' in s:
        return s.replace('chi 2', 'Chi 2')
    elif 'XGBoost_default' in s:
        return s.replace('XGBoost_default', 'XGBoost')
    else:
        return s
    
def ranking_table(input_file_name, ranking_dicts, ranking_names, caption, label):
    """
    put rankings in ranking_dicts specified by ranking_names
    into LaTeX table format

    :param ranking_dicts: dictionaries of raknkings

    :ranking_names: names of rankings to put in table since
    all will not fit in one table

    :param caption: caption for table

    :param label: label for table

    :return: latex format of tables, plus file containing the same as a 
    side-effect
    """
    d = {}
    # ranking dicts is difficult to unpack
    # this is a work-around for a bug in the
    # way the ranking dictionaries are created
    # that put
    for obj in ranking_dicts:
        for k,v in obj.items():
            d[k]=v
    table_str = table_start.format(input_file_name=input_file_name,
                                   align_chars = len(ranking_names)*'l')
    max_rows = max(list(map(len, d.values() )))
    table_str += ' & '.join(list(map(escape_underscores, map(proper_form, ranking_names)))) + "\\\\ \\midrule\n"
                    
    for i in range(max_rows):
        row_str = '      '
        for k in ranking_names:
            try:
                row_str += f'{escape_underscores(d[k][i])} & '
            except IndexError as ie:
                row_str += f' & '
        # replace last & character with LaTeX line ending
        table_str += "\\\\ \\midrule\n".join(row_str.rsplit('&', 1))
    table_str += table_end.format(caption=caption, label=label)
    return table_str
        
        
def ranking_file_to_latex(input_file_name):
    """
    takes output of feature_ranking.py
    and makes into a LaTeX file
    :param input_file_name: name of input file to process
    :return: None, file containing tablees produce as side effect.
    """
    supervised_rankings = ['XGBoost_default', 'CatBoost', 'Light GBM', 'Random Forest']
    unsupervised_rankings = ['information gain ', 'information gain ratio ', 'chi 2 ']
    table_str = ''
    label_prefix = '-'.join(re.split('[_,\-]', os.path.basename(input_file_name).replace(' ', ''))[:2])
    with open(input_file_name, 'r') as f:
        d = json.loads(f.read())
    for ranking_names, caption, label in zip(
            [supervised_rankings, unsupervised_rankings],
            
            ['Features by supervised ranking feature importance',
             'Features by filter-based feature importance'],
            
            [f'tab:{label_prefix}_supervised', f'tab:{label_prefix}_unsupervised']
    ):
        # assuming input file top-level structure is one key that is the input
        # file name for the ranking functions, values are feature rankings
        table_str += ranking_table(input_file_name, d.values(), ranking_names, caption,
                                   label) + '\n'
    return table_str

