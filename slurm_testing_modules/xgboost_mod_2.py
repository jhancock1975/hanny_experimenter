import xgboost as xgb
import time
from our_util import next_seed
from imblearn.under_sampling import RandomUnderSampler
import pandas as pd
import re
import random

def to_safe_names(df:pd.DataFrame)->pd.DataFrame:
    """
    change column names to safe column names
    logic should be same for get_features and
    data prep
    """
    df.rename(columns = lambda x:re.sub('[^A-Za-z0-9_]+', '', x), inplace=True)
    return df

def get_features():
    """
    returns features from medicare part b data
    which is everything but the label. the label
    is in the exclusion column
    """
    # reading columns from sample rather than trying to use explicit list
    # to work around columns with quoted names with commas in them
    df = pd.read_csv('/home/jhancoc4/medicare-data/sample_part_d_agg_2013_2017.csv')
    df = to_safe_names(df)
    return df.columns.drop(['npi', 'exclusion'])


def get_label():
    """
    returns label for medicare
    part b data
    which is just the exclusion column
    """
    return ['exclusion']


def get_model():
    """
    returns model to be used in 
    run_one... scripts
    """
    return xgb.XGBClassifier(tree_method='gpu_hist', objective='binary:logistic',  learning_rate=0.1,
                              max_depth=6, random_state=next_seed())

def get_exp_name():
    """
    returns name of experiment
    for tracking in analysis
    """
    return "xgboost_2013_2017_1_1_part_d_agg"

def data_prep(df):
    """
    :param df: data frame
    """
    df['exclusion'].replace(to_replace=['no', 'yes'], value=[0, 1], inplace=True)
    df = to_safe_names(df)
    return df

def get_result_file():
    return "slurm_testing/parallel_experiment_results-{}.json".format(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())), int(random.random()*10000))

def get_max_workers():
    """
    return maximum number of concurrent
    workers for parallel threads
    """
    return 1

def get_max_iteration_workers():
    """
    return max number of concurrent
    iteration workers - one iteration
    is one run of 5-fold cross validation
    """
    return 1

def get_max_5_fold_workers():
    """
    return max number of 
    concurrent folds
    running during 5-fold
    cross validation
    more than 5 would not make sense
    """
    return 1


def get_last_fitted_model_path():
    """
    return location of last fitted model
    """
    return f"fitted_models/{get_exp_name()}.pkl".replace(" ","_").replace(",", "_")

def get_sampler():
    """
    return sampling object
    """
    return RandomUnderSampler(sampling_strategy=1.0, random_state=next_seed())

def get_slurm_options():
    """
    returns slurm options for running experiment
    """
    return ["--gres=gpu:1", "--mem-per-cpu=96gb", "--mem-per-gpu=32gb", "-p", "longq7-mri"]

def get_input_file_name():
    """
    input file name for experiment
    """
    full_file= '/home/groups/fau-bigdata-datasets/medicare/part-d/20190814_NPI-level_2013_to_2017_Medicare_PartD_aggregated_with_LEIE_one-hot_encoding.csv'
    sample = '/home/jhancoc4/medicare-data/sample_part_d_agg_2013_2017.csv'
    return sample
