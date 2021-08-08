import logging
import time
import json
from sklearn import metrics
import os
import numpy as np
from pathlib import Path
import pandas as pd
import copy

def get_logger(logger_name="main", level=logging.DEBUG) -> object:
    """
    returns a console logger in debug mode,
    covers most of our purposes
    
    @param logger_name: name of logger, shows up on every line
    
    @param level: logging level

    @return: logging object
    """
    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger

def get_metrics(y_test, y_pred, logger, y_prob):
    """
    common code for getting popular metrics
    :param y_test: ground truth
    :param y_pred: predictions
    :param y_prob: result of predict_proba function
    :result: auc, f1, confusion matrix, precision, recall, area under precision-recall curve
    """
    fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred, pos_label = 1)
    auc = metrics.auc(fpr, tpr)
    f1  =metrics.f1_score(y_test, y_pred)
    accuracy = metrics.accuracy_score(y_test, y_pred)
    cm = metrics.confusion_matrix(y_test, y_pred).tolist()
    precision_score = metrics.precision_score(y_test, y_pred)
    recall_score = metrics.recall_score(y_test, y_pred)
    precis, recall, _ = metrics.precision_recall_curve(y_test, y_prob[:, 1])
    a_prc = metrics.auc(recall, precis)
    return auc, f1, cm, precision_score, recall_score, a_prc, accuracy

def log_metrics(y_test, y_pred, logger, y_prob):
    """
    calculate metrics
    :param y_test: ground truth
    :param y_pred: predictions
    :result: auc, f1, and confusion matrix
    """
    auc, f1, cm, precis_score, rec_score, a_prc, accuraccy = get_metrics(y_test, y_pred, logger, y_prob)
    logger.debug('auc = %f', auc)
    logger.debug('f1 = %f', f1)
    logger.debug('confusion matrix = %s', cm)
    logger.debug('accurcy = %f', accuracy)
    return auc, f1, cm, precis_score, rec_score, a_prc

def get_metrics_dict(y_test, y_pred, logger, y_prob)->object:
    """
    returns dictionary of metrics
    :param y_test: ground truth
    :param y_pred: test results
    :param logger: logging object
    :y_prob: probabilities from sklearn classifier predict_proba function
    :return: dictionary of metrics
    """
    auc, f1, cm, precision, recall, a_prc, accuracy = get_metrics(y_test, y_pred, logger, y_prob)
    return {'auc': auc,
            'f1': f1,
            'cm': cm,
            'precision': precision,
            'recall': recall,
            "a_prc": a_prc,
            "accuracy": accuracy}

seed = 1729
def next_seed(s:int = None)->int:
    """
    for seeding random number generators for
    repeatable results returns next value for
    global seed unless param is passed
    :param s: new value for seed
    :return: seed incremented by one
    """
    global seed
    if not s:
        seed += 1
    else:
        seed = s
    return seed

def print_results(test_results, logger=None, file_name=None):
    """
    print test results to file name results_<<epoch time>>.txt
    where <<epoch time is seconds since Jan 1st 1970>>
    @param test_results: dictionary of test_results
    @param logger: logging object
    @param file_name: name of file to store results
    @return: None
    """
    if not os.path.exists('results'):
        os.makedirs('results')
    if not file_name:
        file_name = "results/results_dictionary-{}.txt".format(time.time())
    results_str = json.dumps(test_results, indent=2)
    with open(file_name, "w") as results_file:
        results_file.write(results_str)
    pass

def get_feature_importance_list(feature_names: list, importance_list: list) -> object:
    """
    marries feature names to importances
    from sklearn classifier feature_importances_ array
    and sorts by importance
    :param feature_names: dataframe for feture names
    :param importance_list: sklearn feature importances list
    :return: list of 1-element dictionaries of feature names and importances,
    sorted by importance
    """
    result = {}
    for feature_name, importance in zip(feature_names, importance_list):
        result[feature_name] = float(importance)
    return {k: v for k, v in sorted(result.items(), reverse=True, key=lambda item: item[1])}


def create_parent_dir_if_not_exists(file_name:str)->str:
    """
    creates parent directory of file if parent directory
    does not exist
    :param file_name: a file name, parent of parent should
    exist
    :return: input value, so one may call this function
    nested in open such as:
    open(create_parent_dir_if_not_exists(...
    """
    path = Path(file_name)
    if not os.path.exists(path.parent):
        os.makedirs(path.parent, exist_ok=True)
    return file_name

def astype_per_column(df: pd.DataFrame, column: str, dtype):
    """
    in place change type of column
    https://stackoverflow.com/a/62317634
    :param df: dataframe
    :param column: column name
    :param dyype: data type for new column
    """
    df[column] = df[column].astype(dtype)
    pass

def n_rankings_agree(d_l, n):
    """
    add lists of features that supervised rankings agree on
    to dictionaries in dictionary
    :param d_l: dictionary of lists
    :param n: number of features that must appear in all rankings
    """
    # collect all features
    features = set()
    for ranker_name, feature_arr in d_l.items():
        for f in feature_arr:
            features.add(f)
    res = set()
    for f in features:    
        agree_count = 0
        for ranker_name, feature_arr in d_l.items():
            if f in feature_arr:
                agree_count += 1
                if agree_count >= n:
                    res.add(f)
    return res

def get_rankings(rankings_file, output_file_name):
    """
    get the 4, 5, 6, 7 agree feature sets for a file holding
    one or more feature rakings
    and save result to json
    :param rankings_file: dictionary , top level keys are file names with rankings results
    from feature_ranking.py
    :param output_file_name: will hold dictionary of results
    :return: same dictionary we write to output_file_name, side-effect is file gets created
    """
    with open(rankings_file, 'r') as f:
        r = {}
        d = json.loads(f.read())
        r = {
            dataset_file_name: {
                f'{i}_agree':  list(n_rankings_agree(ranking_dict, i))
                for i in range(4,8)
            }
            for dataset_file_name, ranking_dict in d.items()
        }
    with open(output_file_name, 'w' )as f:
              f.write(json.dumps(r, indent=2))
    return r


def get_feature_selection_experiments(feature_selection_file_name, selected_features_key, experiments, ds_name,
                                      ds_obj):
    """
    expand experiments to cover feature sets generated with feature
    selection technique
    :param feature_selection_file_name: output of get_rankings() in our_util
    :param selected_features_key: key into dictionary contained in feature_selection_file_name to use for features
    :param experiments: dictionary of existing experiments to copy
    :param ds_name: dataset name
    :param ds_objs: dictionary of selected feature set names and arrays
    :return: expanded experiments dictionary
    """
    # read the selected features out of
    # the feature selection results file
    with open(feature_selection_file_name, 'r') as f:
        d=json.loads(f.read())
        selected_features = d[selected_features_key]
    
    ## copy datasets dictionary entries once for each feature set
    fs_datasets_dict = {
        # part one of kludge  we get experiments dictionaries
        # that have experimernts for different datasets (input files)
        # so we seaprate the ds_name here, it will have values like
        # "theft" or "keylogging"
        ds_name: {
            f'{fs_name}': fs_arr
            for fs_name, fs_arr in selected_features.items()
            }
    }

    ## copy experiments entries once for each dataset entry
    fs_experiments = {}
    for exp_name, exp_obj in experiments.items():
        for ds_name, ds_obj in fs_datasets_dict.items():
            for fs_name, fs_arr in ds_obj.items():
                # part two of the Kludge check if the dataset
                # name is in the experiment name, if it is it's
                # ok to use the features
                if ds_name in exp_name:
                    exp_obj_cpy = copy.deepcopy(exp_obj)
                    exp_obj_cpy['features'] = fs_arr
                    new_exp_name = f'{exp_name}_{ds_name}_{fs_name}'
                    exp_obj_cpy['result file'] = str(Path(exp_obj['result file']).parent)\
                        + f'/{new_exp_name}.json'
                    fs_experiments[f'{exp_name}_{ds_name}_{fs_name}'] = exp_obj_cpy
                    exp_obj_cpy['in progress file'] = str(Path(exp_obj['in progress file']).parent)\
                        + f'/{new_exp_name}.json'
                    

    return fs_experiments
