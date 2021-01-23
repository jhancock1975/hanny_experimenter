#!/home/jhancoc4/venv/python-3.7.3/bin/python
from sklearn.tree import DecisionTreeClassifier
import sys,traceback
sys.path.append('.')
sys.path.append('./slurm_experiment_object_modules/')
from sklearn_experiment_with_setters import SklearnExperimentContainer
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

class ExpRunner(object):
    """
    runs one experiment
    if experiment module workers
    are configured it will run 
    10 iterations of 5 fold cross validation
    on separate threads
    """
    def __init__(self):
        # reference to last fitted model
        # for saving to disk
        super(ExpRunner, self).__init__()
        pass

        
    def train_test(self, experiment_params_module: object, train_index: object, \
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
        model_obj = experiment_params_module.model
        logger.debug('starting fit %s for cross validation fold %d', str(model_obj), fold)

        X_sample = ExpRunner.X.loc[train_index]
        y_sample = ExpRunner.y.values[train_index]
        sampler = experiment_params_module.sampler
        if sampler:
            X_sample, y_sample =  sampler.fit_resample(ExpRunner.X.loc[train_index], ExpRunner.y.values[train_index])
        model_obj.fit(X_sample, y_sample)

        best_model_params = None
        if hasattr(model_obj, "best_model") and callable(model.best_model):
            # assume its a hyperpopt model
            best_model_params = json.loads(model_obj.best_model())
        elif hasattr(model_obj, "best_estimator_"):
            # assume its a GridSearchCV object
            best_model_params = model_obj.best_estimator
            
        ExpRunner.last_fitted_model = model_obj
        exp_name = experiment_params_module.exp_name
        logger.debug('starting predict %s for cross validation fold %d', exp_name, fold)
        y_pred = model_obj.predict(ExpRunner.X.loc[test_index])
        y_prob = model_obj.predict_proba(ExpRunner.X.loc[test_index])
        logger.debug('complete %s cross validation fold %d', exp_name, fold)
        if best_model_params:
            return {f'{fold}':
                {'results':
                 get_metrics_dict(ExpRunner.y.values[test_index], y_pred, logger,  y_prob),
                 'best_params': best_model_params
                }
            }
        else:
            return {f'{fold}':
                get_metrics_dict(ExpRunner.y.values[test_index], y_pred, logger,  y_prob)}

    def do_5_fold_cv(self, experiment_params_module: object, logger:object)->object:
        """
    do 5-fold cross validation fit model to dataset and
        evaluate resultsn
        :param experiment_parms_module: contains experiment parameters
        :param logger: logging object
        :retrun: dictionary of performance results
        """
        logger.info('doing 5-fold cross validation for %s', experiment_params_module.exp_name)
        skf = StratifiedKFold(n_splits = 5, random_state = next_seed(), shuffle = True)
        fold = 1
        model_name = experiment_params_module.exp_name
        results = {}
        for train_index, test_index in skf.split(ExpRunner.X, ExpRunner.y):
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers = experiment_params_module.max_5_fold_workers
                    or experiment_params_module.max_workers
            ) as executor:
                futures = []
                futures.append(
                    executor.submit(self.train_test, experiment_params_module,
                                    train_index, test_index, fold, logger
                    )
                )
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    results.update(res)
                fold += 1
        return results

    def do_model_exp(self, experiment_json,  experiment_params_module, logger:object)->object:
        """
        do ten iterations of 5-fold cross validation
        :param experiment_params_module: has parameters for experiment
        :param  X: features
        :param y: label
        :retrun: dictionary of performance results
        """
        logger.info('in do_model_exp model')
        logger.info('on host %s', socket.gethostname())
        model_base_name = experiment_params_module.exp_name
        results = {
            model_base_name : {
                'params': experiment_json,
                'results_data': {}
            }
        }
        with concurrent.futures.ThreadPoolExecutor(max_workers
                                                   = experiment_params_module.max_iteration_workers
                                                   or experiment_params_module.max_workers) as executor:
            futures = []
            # do 10 iterations of 5-fold cross validation
            # TODO here we could read result file and skip completed iterations
            # as a form of checkpointing
            for i in range(1, 11):
                # just initialize results
                # iteration number assigned is not important
                results[model_base_name]['results_data'][i] = {}
                futures.append(executor.submit(self.do_5_fold_cv, experiment_params_module, logger))
                logger.info("submitted iteration %d for %s", i, model_base_name)
            i = 1
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                results[model_base_name]['results_data'][i].update(res)
                logger.info("completed iteration %d for %s", i, str(res.keys()))
                i += 1
        return results
            
if __name__ == "__main__":
    logger = get_logger()
    logger.debug('starting up')

    parser = argparse.ArgumentParser(description='run 5-fold cross validation in multiple threads')
    
    parser.add_argument('-f', '--file_name',  required=True,
                        help='<Required> JSON file describing experiment')

    parser.add_argument('-e', '--experiment_name',  required=True,
                        help='<Required> name of noe experiment, should be top level key in file specified in -f/--file-name ')

    args = parser.parse_args()
    logger.debug("args %s", str(args))
    with open(args.file_name, 'r') as f:
        experiment_json = json.loads(f.read())
        experiment = experiment_json[args.experiment_name]
    

    # load experiment parameters module 
    experiment_params_module = SklearnExperimentContainer(args.experiment_name, experiment)
    # check if we already have results for this experiment
    result_file_name = experiment_params_module.result_file
    create_parent_dir_if_not_exists(result_file_name)
    exp_name = experiment_params_module.exp_name
    path = Path(result_file_name)
    result_file_parent_dir=path.parent
    exp_runner = ExpRunner()

    #only do the experiment if we do not have results
    logger.debug("We have not yet conducted experiment %s.  We commence to perform it now.",
                 exp_name)
    separator =  experiment['input file']['separator']
    exp_input_file=experiment_params_module.input_file_name.strip()
    logger.debug('reading input file %s, separator = %s', exp_input_file,
                 separator)
    # attach dataframe to object as static member
    # trying to avoid out-of-memory erroes
    ExpRunner.df = pd.read_csv(exp_input_file, sep=separator)
    logger.debug('complete reading input file')

    experiment_params_module.data_prep(ExpRunner.df)

    ExpRunner.X = ExpRunner.df[experiment_params_module.features]
    ExpRunner.y = ExpRunner.df[experiment_params_module.label]

    # run experiments and save resuts to dictionary

    try:
        with open(result_file_name, 'w') as f:
            f.write(
                json.dumps(
                    exp_runner.do_model_exp(
                        experiment_json[experiment_params_module.exp_name],
                        experiment_params_module,
                        logger),
                    indent=2
                )
            )
    except Exception as e:
        logger.debug('caught exception %s', str(e))
        traceback.print_exc()

    # save last trained model
    trained_model_file = experiment_params_module.last_fitted_model_path
    if trained_model_file:
        create_parent_dir_if_not_exists(trained_model_file)
        with open(trained_model_file, 'wb') as f:
            pickle.dump(ExpRunner.last_fitted_model, f, pickle.HIGHEST_PROTOCOL)
