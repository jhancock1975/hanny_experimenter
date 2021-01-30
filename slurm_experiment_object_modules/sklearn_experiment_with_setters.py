import time
from our_util import next_seed, get_logger
import random
import pandas as pd
import json
import importlib

class SklearnExperimentContainer(object):
        # parent of sklearn experiment objects

    def __init__(self, name:str, experiment: object)->None:
        """
        constructor, sets properties
        :param experiment: dictionary of experiment parameters
        """
        self._features = experiment['features']
        self._label = experiment['label']
        self._model = self.load_module(experiment['model'])
        self._exp_name = name
        self._result_file = experiment['result file']
        self._max_workers = experiment['max workers']
        self._max_iteration_workers = experiment['max iteration workers']
        self._max_5_fold_workers = experiment['max 5 fold workers']
        self._sampler = self.load_module(experiment['sampler'])
        self._slurm_options = experiment['slurm options']
        self._input_file_name = experiment['input file']['name']
        self._separator = experiment['input file']['separator']

    def load_module(self, module_dict: object)->object:
        """
        dynamically load object from module name
        and class name
        :param module_dict: should contain entries for module name, class name, and class instance parameters in a sub-dictionary
        :return: instance of class     
        """
        if module_dict:        
            class_ = self._get_obj( module_dict)
            if (module_dict['instance params']):
                if 'model' in module_dict['instance params']:
                    # for cases like randomized search and grid search hyper parameter tuning
                    # we recursivley instantiate module
                    mod = self.load_module(module_dict['instance params']['model'])
                    module_dict['instance params']['estimator'] = mod
                return class_( **module_dict['instance params'])
            else:
                return  class_()
        else:
            return None
        
    def _get_obj(self, module_dict:object)->object:
        """
        for the "do not repeat yourself (DRY) principle, return object
        given class name and module name
        :param module_name: path to file e.g. scipy.stats
        :param class_name: class name e.g. RandomForestClassifier
        :return object constructor function
        """
        module_path = module_dict['module name']
        class_name = module_dict['class name']
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
        
    @property
    def features(self):
        """
        returns features from medicare part b data
        which is everything but the label. the label
        is in the exclusion column
        """
        return self._features
   
    @features.setter
    def features(self, features):
        self._featuers = features
    
    @property
    def label(self):
        """
        returns label for medicare
        part b data
        which is just the exclusion column
        """
        return self._label
    
    @label.setter
    def label(self, label):
        self._label = label

    @property
    def model(self):
        """
        returns model to be used in 
        run_one... scripts
        """
        return self._model

    @model.setter
    def model(self, model):
        self._model = model

    @property
    def exp_name(self):
        """
        returns name of experiment
        for tracking in analysis
        """
        return self._exp_name

    @exp_name.setter
    def exp_name(self, exp_name):
        self._exp_name = exp_name

    def data_prep(self, df: pd.DataFrame)->pd.DataFrame:
        """
        :param df: data frame
        """
        return df

    @property
    def result_file(self):
        """
        :return: name of file to save experiment results
        """
        return self._result_file

    @result_file.setter
    def result_file(self, result_file):
        self._result_file = result_file

    @property
    def max_workers(self):
        """
        return maximum number of concurrent
        workers for parallel threads for running experiments
        """
        return self._max_workers

    @max_workers.setter
    def max_workers(self, max_workers):
        self._max_workers = max_workers

    @property
    def max_iteration_workers(self):
        """
        return max number of concurrent
        iteration workers - one iteration
        is one run of 5-fold cross validation
        """
        return self._max_iteration_workers

    @max_iteration_workers.setter
    def max_iteration_workers(self, max_iteration_workers):
        self._max_iteration_workers = max_iteration_workers

    @property
    def max_5_fold_workers(self):
        """
        return max number of 
        concurrent folds
        running during 5-fold
        cross validation
        more than 5 would not make sense
        """
        return self._max_5_fold_workers

    @max_5_fold_workers.setter
    def max_5_fold_workers(self, max_5_fold_workers):
        self._max_5_fold_workers = max_5_fold_workers

    @property
    def sampler(self):
        """
        return sampling object
        """
        return self._sampler

    @sampler.setter
    def sampler(self, sampler):
        self._sampler = sampler

    @property
    def slurm_options(self):
        """
        returns slurm options for running experiment
        """
        return self._slurm_options

    @slurm_options.setter
    def slurm_options(self, slurm_options):
        self._slurm_options = slurm_options

    @property
    def input_file_name(self):
        """
        input file name for experiment
        """
        return self._input_file_name

    @input_file_name.setter
    def input_file_name(self, input_file_name):
        self._input_file_name = input_file_name
        
