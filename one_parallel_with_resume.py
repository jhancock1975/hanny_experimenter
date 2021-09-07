#!/home/jhancoc4/venv/py-3.8.7/bin/python
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
from sklearn.preprocessing import StandardScaler, MinMaxScaler, MaxAbsScaler
from sklearn.model_selection import StratifiedKFold
from imblearn.under_sampling import RandomUnderSampler
import  numpy as np
import socket
import selectors
import types
import dill as pickle
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
from scipy.stats import randint, uniform, loguniform
import gc
from scipy.sparse import csr_matrix
from category_encoders.cat_boost import CatBoostEncoder
from filelock import Timeout, FileLock

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

        try:
            X_sample = ExpRunner.X.loc[train_index]
        except AttributeError as e:
            # X is probably a sparse matrix
            logger.debug('X has no loc attribute, accessing X as array')
            X_sample = ExpRunner.X[train_index]
        y_sample = ExpRunner.y.values[train_index]
        sampler = experiment_params_module.sampler
        if sampler:
            X_sample, y_sample =  sampler.fit_resample(ExpRunner.X.loc[train_index], ExpRunner.y.values[train_index])
        if experiment_params_module.scaler:
            scaler = experiment_params_module.scaler()
            if scaler:
                X_sample = scaler.fit_transform(X_sample)
        else:
            scaler = None
        model_obj.fit(X_sample, y_sample)
        results = {}
        exp_name = experiment_params_module.exp_name
        logger.debug('starting predict %s for cross validation fold %d', exp_name, fold)
        try:
            if scaler:
                X_test = scaler.transform(ExpRunner.X.loc[test_index])
            else:
                X_test = ExpRunner.X.loc[test_index]
            y_pred = model_obj.predict(X_test)
            y_prob = model_obj.predict_proba(X_test)
        except AttributeError as e:
            # X is probably a sparse matrix
            logger.debug('X has no loc attribute, accessing X as array')
            if scaler:
                X_test = scaler.transform(ExpRunner.X[test_index])
            else:
                X_test = ExpRunner.X[test_index]
            y_pred = model_obj.predict(X_test)
            y_prob = model_obj.predict_proba(X_test)
        logger.debug('complete %s cross validation fold %d', exp_name, fold)
        d = get_metrics_dict(ExpRunner.y.values[test_index], y_pred, logger,  y_prob)
        if hasattr(model_obj, 'best_estimator_'):
            d['best_params_'] = model_obj.best_params_
        return {f'{fold}': d}

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
            results.update(
                self.train_test(experiment_params_module, train_index, test_index, fold, logger))
            fold += 1
        return results

    def do_model_exp(self, experiment_dict,  experiment_params_module, logger:object)->object:
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
                'results_data': {}
            }
        }
        try:
            with open(experiment_params_module.in_progress_file_name, 'r') as f:
                try:
                    results.update(json.loads(f.read()))
                    last_iter  = len (results[model_base_name]['results_data']) + 1
                except json.decoder.JSONDecodeError as e:
                    logger.info(f'unable to parse {experiment_params_module.in_progress_file_name} for reading last iteration')
                    last_iter = 1
        except FileNotFoundError as e:
            logger.info(f'{experiment_params_module.in_progress_file_name} not found for reading last iteration')
            last_iter = 1
        logger.info(f'resuming experiment {experiment_params_module.exp_name}  at iteration {last_iter}')
        with concurrent.futures.ThreadPoolExecutor(max_workers
                                                   = experiment_params_module.max_iteration_workers
                                                   or experiment_params_module.max_workers) as executor:
            futures = []
            # do 10 iterations of 5-fold cross validation
            # read result file and skip completed iterations
            # as a form of checkpointing
            for i in range(last_iter, 11):
                # just initialize results
                # iteration number assigned is not important
                futures.append(executor.submit(self.do_5_fold_cv, experiment_params_module, logger))
                logger.info("submitted iteration %d for %s", i, model_base_name)
            # 5-fold cv's are running asynchronously; here we are waiting for them to finish
            # so reset the counter variable i to initial value
            i = last_iter
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                results[model_base_name]['results_data'][i]= res
                # save partial progress
                lock = FileLock(experiment_params_module.in_progress_file_name + '.lock')
                with lock :
                    open(experiment_params_module.in_progress_file_name, 'w').write(json.dumps(results, indent=2))
                logger.info("completed iteration %d for %s", i, str(res.keys()))
                i += 1
        return results
            
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='run 5-fold cross validation in multiple threads')
    
    parser.add_argument('-f', '--file_name',  required=True,
                        help='<Required> JSON or pickle file describing experiment')

    parser.add_argument('-e', '--experiment_name',  required=True,
                        help='<Required> name of one experiment, should be top level key in file specified in -f/--file-name ')

    args = parser.parse_args()
    logger = get_logger(logger_name=args.experiment_name)
    logger.debug("args %s", str(args))

    if args.file_name.endswith('.json'):
        with open(args.file_name, 'r') as f:
            experiment_dict = json.loads(f.read())
    elif args.file_name.endswith('.pkl'):
        with open(args.file_name, 'rb') as f:
            experiment_dict = pickle.load(f)
    else:
        logger.error('unsupported file type')
        exit(1)
    experiment = experiment_dict[args.experiment_name]
    

    # load experiment parameters module 
    experiment_params_module = SklearnExperimentContainer(args.experiment_name, experiment)
    # check if we already have results for this experiment
    result_file_name = experiment_params_module.result_file
    create_parent_dir_if_not_exists(result_file_name)
    # create the in-progress direcotry if it does not exist
    create_parent_dir_if_not_exists(experiment_params_module.in_progress_file_name)
    
    exp_name = experiment_params_module.exp_name
    exp_runner = ExpRunner()

    logger.debug("Starting experiment %s...", exp_name)
    separator =  experiment['input file']['separator']
    exp_input_file=experiment_params_module.input_file_name.strip()
    logger.debug('reading input file %s, separator = %s', exp_input_file,
                 separator)
    # attach dataframe to object as static member
    # trying to avoid out-of-memory erroes
    if exp_input_file.endswith('.pkl'):
        ExpRunner.df = pd.read_pickle(exp_input_file)
        # reset index for working with sample
        ExpRunner.df.reset_index(drop=True, inplace=True)
    else:
        ExpRunner.df = pd.read_csv(exp_input_file, sep=separator)
    logger.debug('complete reading input file')

    logger.debug('start data prep')
    ExpRunner.df = experiment_params_module.data_prep(ExpRunner.df, experiment)
    ExpRunner.X = ExpRunner.df[experiment_params_module.features]
    gc.collect()
    ExpRunner.y = ExpRunner.df[experiment_params_module.label]

    # run experiments and save resuts to dictionary

    try:
        results_d = exp_runner.do_model_exp(experiment_dict[experiment_params_module.exp_name],
                        experiment_params_module,
                        logger)
        with open(result_file_name, 'w') as f:
            f.write(json.dumps(results_d, indent=2))
        os.remove(experiment_params_module.in_progress_file_name)
    except Exception as e:
        logger.debug('caught exception %s', str(e))
        traceback.print_exc()
