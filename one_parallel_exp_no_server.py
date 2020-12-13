#!/usr/bin/env python3
from sklearn.tree import DecisionTreeClassifier
import sys,traceback
sys.path.append('.')
from our_util import get_logger,  get_metrics_dict, next_seed, create_parent_dir_if_not_exists
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB, CategoricalNB
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import f1_score
from sklearn.metrics import auc
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import StratifiedKFold
from imblearn.under_sampling import RandomUnderSampler
import  numpy as np
import socket
import selectors
import types
import pickle
from io import StringIO
import argparse
import importlib
import importlib.util
import concurrent.futures
import os
import pprint
import json
from pathlib import Path
import re
import subprocess

# reference to last fitted model
# for saving to disk
last_fitted_model = None

def train_test(experiment_params_module: object, train_index: object, \
               test_index: object, fold: int,  logger:object):
    """
    train and test a model on one fold of cross validation
    :model: dictionary should have entries for model name
    and model constructor function
    :param X: features
    :param y: labels
    :param sampling_conf: sampling configuration
    :param train_index: index of training examples
    :param test_index: index of test examples
    :param fold: fold number for reporting
    :param logger: logging object
    """
    global last_fitted_model
    model_obj = experiment_params_module.get_model()
    logger.debug('starting fit %s for cross validation fold %d', str(model_obj), fold)

    X_sample = X.loc[train_index]
    y_sample = y.values[train_index]
    sampler = experiment_params_module.get_sampler()
    if sampler:
        X_sample, y_sample =  sampler.fit_resample(X.loc[train_index], y.values[train_index])
    model_obj.fit(X_sample, y_sample)
    last_fitted_model = model_obj
    exp_name = experiment_params_module.get_exp_name()
    logger.debug('starting predict %s for cross validation fold %d', exp_name, fold)
    y_pred = model_obj.predict(X.loc[test_index])
    y_prob = model_obj.predict_proba(X.loc[test_index])
    logger.debug('complete %s cross validation fold %d', exp_name, fold)
    return {f'{fold}':
            get_metrics_dict(y.values[test_index], y_pred, logger,  y_prob)}

def do_5_fold_cv(experiment_params_module: object, logger:object)->object:
    """
do 5-fold cross validation fit model to dataset and
    evaluate resultsn
    :param experiment_parms_module: contains experiment parameters
    :param logger: logging object
    :retrun: dictionary of performance results
    """
    logger.info('doing 5-fold cross validation for %s', experiment_params_module.get_exp_name())
    skf = StratifiedKFold(n_splits = 5, random_state = next_seed(), shuffle = True)
    fold = 1
    model_name = experiment_params_module.get_exp_name()
    results = {}
    for train_index, test_index in skf.split(X, y):
        with concurrent.futures.ThreadPoolExecutor(
                max_workers = experiment_params_module.get_max_5_fold_workers()
                or experiment_params_module.get_max_workers()
        ) as executor:
            futures = []
            futures.append(
                executor.submit(train_test, experiment_params_module,
                                train_index, test_index, fold, logger
                )
            )
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                results.update(res)
            fold += 1
    return results

def do_model_exp( experiment_params_module, logger:object)->object:
    """
    do ten iterations of 5-fold cross validation
    :param experiment_params_module: has parameters for experiment
    :param  X: features
    :param y: label
    :retrun: dictionary of performance results
    """
    logger.info('in do_model_exp model')
    logger.info('on host %s', socket.gethostname())
    model_base_name = experiment_params_module.get_exp_name()
    results = {
        model_base_name : {
            'params_module': str(experiment_params_module),
            'input_file': experiment_params_module.get_input_file_name(),
            'results_data': {}
        }
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers
                                               = experiment_params_module.get_max_iteration_workers()
                                               or experiment_params_module.get_max_workers()) as executor:
        futures = []
        # do 10 iterations of 5-fold cross validation
        for i in range(1, 11):
            # just initialize results
            # iteration number assigned is not important
            results[model_base_name]['results_data'][i] = {}
            futures.append(executor.submit(do_5_fold_cv, experiment_params_module, logger))
            logger.info("submitted iteration %d for %s", i, model_base_name)
        i = 1
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            results[model_base_name]['results_data'][i].update(res)
            logger.info("completed iteration %d for %s", i, str(res.keys()))
            i += 1
    return results

def check_for_results(file_name: str, result_file_parent_dir: str, logger: object)->bool:
    """
    checks if we don't already have a results file for directory
    :param file_name: name of experiment, could be a key in results file
    :param result_file_parent_dir: directory to check
    :return: true if there is a results file with experiment name in result_file_parent_dir
    false otherwise
    """
    for entry in os.scandir(result_file_parent_dir):
        if entry.path.endswith(".json") and entry.is_file():
            try:
                with open(entry, 'r') as f:
                    j = json.loads(f.read())
                    for exp_name, exp_data in j.items():
                        if file_name in exp_data['params_module']:
                            return True
            except Exception as e:
                #if logger:
                #logger.debug("We caught the exception %s checking for completed results.", str(e))
                continue
    if logger:
        logger.debug("we will run the experiment again.")
    return False

def check_running_now(module_name: str, logger: object)->bool:
    """
    checks if module is not currently running
    :param module_name: experiment module name
    :return: true if module already submitted to slurm queue for my user id
    """
    running_jobs=subprocess.run(['squeue', '-u', 'jhancoc4', '-o', '"%k"', '-h'],
                                                           capture_output=True)
    s_out=str(running_jobs.stdout)
    if module_name in s_out:
        logger.debug("experiment %s apparently already running in %s,", module_name, s_out)
        logger.debug("not running %s again at this time", module_name)
        return True
    else:
        return False


df = None
# make features and label global
# so threads don't pass around copies
# and jobs are killed for using too much
# memory
X = None
y = None
            
if __name__ == "__main__":
    logger = get_logger()
    logger.debug('starting up')

    parser = argparse.ArgumentParser(description='run 5-fold cross validation in multiple threads')
    parser.add_argument('-m', '--module_name',  required=True,
                        help='<Required> module containing experiment details')
    parser.add_argument('-s', '--separator',  required=False, const=",", nargs="?", default=",",
                        help='<Optional> csv separator character, default: ","', type=str)

        
    args = parser.parse_args()
    logger.debug("args %s", str(args))
    

    # load experiment parameters module 
    file_path = args.module_name
    module_name = file_path[0:file_path.rfind('.')]

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    experiment_params_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(experiment_params_module)

    # check if we already have results for this experiment
    result_file_name = experiment_params_module.get_result_file()
    create_parent_dir_if_not_exists(result_file_name)
    exp_name = experiment_params_module.get_exp_name()
    path = Path(result_file_name)
    result_file_parent_dir=path.parent
    already_done = check_for_results(file_path, result_file_parent_dir, logger)
    # check if an experiment is not already running
    # may fail later and we would have to run again
    # running_now = check_running_now(module_name, logger)
    if not already_done:
        #only do the experiment if we do not have results
        logger.debug("We have not yet conducted experiment %s.  We commence to perform it now.",
                     exp_name)
        exp_input_file=experiment_params_module.get_input_file_name().strip()
        logger.debug('reading input file %s, separator = %s', exp_input_file, args.separator)
        df = pd.read_csv(exp_input_file, sep=args.separator)
        logger.debug('complete reading input file')

        experiment_params_module.data_prep(df)

        X = df[experiment_params_module.get_features()]
        y = df[experiment_params_module.get_label()]

        # run experiments and save resuts to dictionary

        with open(result_file_name, 'w') as f:
            f.write(
                json.dumps(
                    do_model_exp(experiment_params_module, logger),
                    indent=2
                )
            )

        # save last trained model
        trained_model_file = experiment_params_module.get_last_fitted_model_path()
        if trained_model_file:
            create_parent_dir_if_not_exists(trained_model_file)
            with open(trained_model_file, 'wb') as f:
                pickle.dump(last_fitted_model, f, pickle.HIGHEST_PROTOCOL)
