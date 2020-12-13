import sys
sys.path.append('.')
sys.path.append('./medicare_experiment_modules')
from catboost_2012_2017_1_1_part_b_hcpcs import *

def get_exp_name():
    """
    returns name of experiment
    for tracking in analysis
    """
    return "catboost_2013_2017_1_1_part_d_hcpcs"

def get_features():
    """
    returns features from medicare part b data
    which is everything but the label. the label
    is in the exclusion column
    """
    return [
        'provider_type',
        'description_flag',
        'drug_name',
        'generic_name',
        'bene_count',
        'total_claim_count',
        'total_30_day_fill_count',
        'total_day_supply',
        'total_drug_cost',
        'year'
    ]

def data_prep(df):
    """
    for catboost need to convert categorical
    columns to string
    make label 0/1 for auc and au prc calculations
    :param df: data frame
    """
    for col in ['provider_type', 'description_flag', 'drug_name', 'generic_name']:
        astype_per_column(df, col, str)
        
def get_model():
    return CatBoostClassifier(random_state=next_seed(),
                              cat_features=['provider_type', 'description_flag', 'drug_name',
                                            'generic_name'],
                              task_type="GPU",
                              devices='0',
                              logging_level='Silent')

def get_input_file_name():
    """
    input file name for experiment
    """
    full_file= '/home/groups/fau-bigdata-datasets/medicare/non-aggregated/Medicare_PUF_PartD_2013to2017.csv.gz'
    sample = '/home/jhancoc4/medicare-data/sample_part_d_2013_2017_individual.csv'
    return sample

