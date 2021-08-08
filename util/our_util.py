import logging
import time
import json
from sklearn import metrics
import os
import numpy as np
from pathlib import Path
import pandas as pd

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
    ch.setLevel(level)
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
