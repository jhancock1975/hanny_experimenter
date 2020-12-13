import sys
sys.path.append('.')
sys.path.append('./medicare_experiment_modules')
from catboost_1_1_2012_2017_part_b_agg import *
from our_util import astype_per_column

def get_exp_name():
    """
    returns name of experiment
    for tracking in analysis
    """
    return "catboost_2012_2017_1_1_part_b_hcpcs"

def get_features():
    """
    returns features from medicare part b data
    which is everything but the label. the label
    is in the exclusion column
    """
    return [
        'line_srvc_cnt', 'bene_unique_cnt', 'bene_day_srvc_cnt', 'average_submitted_chrg_amt',
        'average_medicare_payment_amt', 'provider_type', 'gender', 'hcpcs_code'
    ]

def data_prep(df):
    """
    for catboost need to convert categorical
    columns to string
    make label 0/1 for auc and au prc calculations
    :param df: data frame
    """
    for col in ['provider_type', 'gender', 'hcpcs_code']:
        astype_per_column(df, col, str)
        
def get_model():
    return CatBoostClassifier(random_state=next_seed(),                        
                              cat_features=['provider_type', 'gender', 'hcpcs_code'],
                              task_type="GPU",
                              devices='0',
                              logging_level='Silent')

def get_input_file_name():
    """
    input file name for experiment
    """
    full_file= '/home/groups/fau-bigdata-datasets/medicare/non-aggregated/Medicare_PUF_PartB_2012to2017.csv.gz'
    sample = '/home/jhancoc4/medicare-data/sample_Medicare_PUF_PartB_2012to2017.csv'
    return sample

