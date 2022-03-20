#!/usr/bin/env python3
import subprocess
import logging
from our_util import get_logger
logger = get_logger()

if __name__ == '__main__':
    logger.info('staring up')
    # output of subprocess is a CompletedProcess object
    # which has a stdout member when capture_output equals True
    # stdout is a bytes array, we convert to a string, then split on newline to
    # get a list of nodes currently in use
    # there is an extra byte after the last newline in the squeue output
    node_list = subprocess.run(['squeue','-h', '--me', '-o', '%N'],
                               capture_output=True).stdout.decode('utf-8').split('\n')[:-1]
    logger.info(f'node_list = {node_list}')
    logger.info(subprocess.run(['squeue','-h', '--me', '-o', '%N'], capture_output=True).stdout)
    
