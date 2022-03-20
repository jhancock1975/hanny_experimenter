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
    node_set = subprocess.run(['squeue','-h', '--me', '-o', '%N'],
                               capture_output=True).stdout.decode('utf-8').split('\n')[:-1]
    logger.info(f'node_set = {node_set}')
    return node_list

    return 
if __name__ == '__main__':
    logger.info('staring up')
    def 
    while True:
        nodes_in_use = get_node_list()
        time.sleep(10)

    
