import time
from our_util import next_seed, get_logger
import random
import pandas as pd

class SklearnExperiment(object):
        # parent of sklearn experiment objects

    @property
    def features(self):
        """
        returns features from medicare part b data
        which is everything but the label. the label
        is in the exclusion column
        """
        raise NotImplementedError("Please define a features() property that returns a list of strings representing the input values for a supervised machine learning algorithm")
   
    @features.setter
    def features(self, features):
        raise NotImplementedError("Please define a features() property that returns a list of strings representing the input values for a supervised machine learning algorithm")
    
    @property
    def label(self):
        """
        returns label for medicare
        part b data
        which is just the exclusion column
        """
        raise NotImplementedError("Please define a label() property that returns a one element array with the name of the label on the dataset.  This will be used as the ground truth for a supervised machine learning algorithm")

    @label.setter
    def label(self, label):
        raise NotImplementedError("Please define a label() property that returns a one element array with the name of the label on the dataset.  This will be used as the ground truth for a supervised machine learning algorithm")

    @property
    def model(self):
        """
        returns model to be used in 
        run_one... scripts
        """
        raise NotImplementedError("Please define a model() property that returns an instance of a classifier for supervised machine learning, For example: xboost.XGBClassifier(), with at least the required parameters.")

    @model.setter
    def model(self, model):
        raise NotImplementedError("Please define a model() property that returns an instance of a classifier for supervised machine learning, For example: xboost.XGBClassifier(), with at least the required parameters.")

    @property
    def exp_name(self):
        """
        returns name of experiment
        for tracking in analysis
        """
        raise NotImplementedError("Please give a human readable name for this experiment.")

    @exp_name.setter
    def exp_name(self, exp_name):
        raise NotImplementedError("Please give a human readable name for this experiment.")

    def data_prep(self, df: pd.DataFrame)->pd.DataFrame:
        """
        :param df: data frame
        """
        raise NotImplementedError("Please define a function data_prep(data_frame_obj) for any data preparation necesssary prior to experment, or simply return data_frame_obj unchanged if no pre-processing is necessary")

    @property
    def result_file(self):
        """
        :return: name of file to save experiment results
        """
        raise NotImplementedError("Please define a property that returns the name of the file where we should store results.")

    @property
    def max_workers(self):
        """
        return maximum number of concurrent
        workers for parallel threads for running experiments
        """
        1

    @property
    def max_iteration_workers(self):
        """
        return max number of concurrent
        iteration workers - one iteration
        is one run of 5-fold cross validation
        """
        return 1

    @property
    def max_5_fold_workers(self):
        """
        return max number of 
        concurrent folds
        running during 5-fold
        cross validation
        more than 5 would not make sense
        """
        return 1


    @property
    def last_fitted_model_path(self):
        """
        return location of last fitted model
        """
        return f"fitted_models/{self.exp_name}.pkl".replace(" ","_").replace(",", "_")

    @property
    def sampler(self):
        """
        return sampling object
        """
        return None

    @property
    def slurm_options(self):
        """
        returns slurm options for running experiment
        """
        raise NotImplementedError('Please define a slurm_options() property that gives the command line options for the sbatch command for running this experiment.  Every option should be one or two elements of a list.  If it is an option that is set with an = operator, then it should be one element.  If it is an optoin that is not set wtih the = operator, then it should be two elements.  Here is an example: return ["--gres=gpu:1", "--mem-per-cpu=96gb", "--mem-per-gpu=32gb", "-p", "longq7-mri"]')

    @property
    def input_file_name(self):
        """
        input file name for experiment
        """
        raise NotImplementeError("Please define a property that returns the name of the input file for the experiment.")
