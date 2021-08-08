#!/bin/env python
import logging
import sys
from our_util import get_logger
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
import os
from pathlib import Path

class EdaMeister(object):

    def stratified_sample_csv(self, df: pd.DataFrame, col: str, n_samples: int, output_file_name: str):
        """
        from https://stackoverflow.com/a/53615691
        save stratified sample from a dataframe
        :param df: big dataframe take a sample of it
        :param col: name of column to use for stratified sample
        :param n_samples: number of samples to save
        :param output_file_name: name of file to save stratified sample
        :return: dataframe with stratified sample, side-effect saving sample to dataframe
        """
        n = min(n_samples, df[col].value_counts().min())
        df_ = df.groupby(col).apply(lambda x: x.sample(n))
        df_.index = df_.index.droplevel(0)
        df_.to_csv(output_file_name, index=False)
        return df_

    def get_descriptive_stats_str(self, df: pd.DataFrame):
        stats_df = df.describe(include="all")
        stats_report = ''
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', None)
        # pd.set_option('display.max_colwidth', -1)
        for c in stats_df.columns:
            stats_report += f"\n{stats_df[c]}"
        return stats_report
    
if __name__ == "__main__":
    eda_meister = EdaMeister()
    parser  = argparse.ArgumentParser('get descriptive statistics')
    parser.add_argument('-i', '--input_file_name', help='input file name')
    parser.add_argument('-s', '--sample_column', help='column name to use for stratified sample, if you do not want a sample, do not set this value', nargs='?', const=None, type=str)
    parser.add_argument('-z', '--sample_size', help='sample size, if you do not want a sample, do not set this value', nargs='?', const=None, type=int)
    args = parser.parse_args()
    input_file_name = args.input_file_name
    sample_column = args.sample_column
    sample_size = args.sample_size
    logger = get_logger(logger_name='get_descriptive_stats', level=logging.DEBUG)
    logger.debug(f"reading input file {input_file_name}")
    df = pd.read_csv(input_file_name)
    logger.debug('taking stratified sample')
    if sample_size and sample_column:
            sample_file_name = os.path.join(f'{Path(input_file_name).parent.absolute()}', f'sample_{os.path.basename(input_file_name)}')
            logger.debug(f'sample file name {sample_file_name}')
            eda_meister.stratified_sample_csv(df, sample_column, sample_size, sample_file_name)
    else:
        logger.debug('--sample_size or --sample_file_name not set, skipping sampling')
    stats_report = eda_meister.get_descriptive_stats_str(df)
    logger.info(stats_report)
