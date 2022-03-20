#!/usr/bin/env python3
import subprocess
import logging
import time
from our_util import get_logger

logger = get_logger()

def get_node_list():
    '''
    get list of nodes currently in use
    :return: list of node names that current user is running jobs on
    '''
    #  output of subprocess is a CompletedProcess object
    # which has a stdout member when capture_output equals True
    # stdout is a bytes array, we convert to a string, then split on newline to
    # get a list of nodes currently in use
    # split gives an empty element after last node name because it is followed by a newline
    # we never want to run anything on nodegpu002 and nodegpu003, they are too wimpy
    # so assume they are in use
    return set(subprocess.run(['squeue','-h', '--me', '-o', '%N'],
                               capture_output=True).stdout.decode('utf-8').split('\n')[:-1]
                   ).update(['nodegpu002', 'nodegpu003'])


    return 
if __name__ == '__main__':
    logger.info('staring up')
    
    while True:
        nodes_in_use = get_node_list()
        logger.info(f'nodes_in_use {nodes_in_use}')
        time.sleep(10)

    
