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
    node_list = set(subprocess.run(['squeue','-h', '--me', '-o', '%N'],
                               capture_output=True).stdout.decode('utf-8').split('\n')[:-1]
                    )
    # we never want to run anything on nodegpu002 and nodegpu003, they are too wimpy
    # so assume they are in use
    node_list.update(['nodegpu002', 'nodegpu003'])
    return node_list

    return 
if __name__ == '__main__':
    logger.info('staring up')
    # node names in Koko are mostly like nodenviv1000
    # foolowed by the node number with a leading 0
    all_nodes = set([f'nodenviv1000{"0" if node_num > 10 else ""}{node_num}'
                     for node_num in range(1, 17)])
    # two nodes do not fit the pattern of other node names
    all_nodes.update(['nodegpu002', 'nodegpu003'])
    while True:
        nodes_in_use = get_node_list()
        available_nodes = all_nodes.difference(nodes_in_use)
        logger.info(f'available_nodes {available_nodes}')
        time.sleep(10)

    
