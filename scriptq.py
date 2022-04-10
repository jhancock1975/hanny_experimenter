#!/usr/bin/env python3
import subprocess
import logging
import time
from our_util import get_logger
import argparse
import shutil
import os

def get_node_list():
    '''
    get list of nodes currently in use
    :return: list of node names that current user is running jobs on
    '''
    # output of subprocess is a CompletedProcess object
    # which has a stdout member when capture_output equals True
    # stdout is a bytes array, we convert to a string, then split on newline to
    # get a list of nodes currently in use
    # split gives an empty element after last node name because it is followed by a newline
    # in squeue command %n gives nodes in use, %N gives nodes requested
    node_list = subprocess.run(['squeue','-h', '--me', '-o', '%N %n'],
                               capture_output=True).stdout.decode('utf-8').split()[:-1]
    # need to remove whitespace surrounding node names
    node_list = list(map(lambda s: s.strip(), node_list))
    # conver to a set to make it easy to
    # get available nodes later
    node_list = set(node_list)
    # we never want to run anything on nodegpu002 and nodegpu003, they are too wimpy
    # so assume they are in use
    # add other nodes to be ignored here
    # temporarily adding '05 because anything I submit does not run
    # and squeue report "resource unavailable"
    node_list.update(['nodegpu002', 'nodegpu003','nodenviv100005'])
    return node_list

def run_next_job(available_nodes, script_file, logger):
    '''
    read one command from script file and run it
    on any available node
    :param available_nodes: list of nodes we are not running anything on yet
    :param script_file: file of commands to run with sbatch, first command in
    file will be run, and removed from file
    '''
    # get first line of file, assume it is a python string with placeholder
    # value for nodelist, which will be the node that the job runs on
    with open(script_file, 'r') as f:
        cmd = f.readline()
    cmd = cmd.format(node=list(available_nodes)[0])
    if len(cmd.strip()) > 0:
        logger.info(f'running command: {cmd}')
        # subrprocess.run whatever fiddle-faddle it does
        # in turning the array passed to it to a comand
        # is too complicated to reconcile with complex sbatch command
        # so use os.system
        os.system(cmd)
            # remove first line from file
        with open(script_file, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(script_file, 'w') as fout:
            fout.writelines(data[1:])
        result = True
    else:
        logger.info('empty line found, no command to execute')
        result = False
    return result

def get_nodes_in_queue(queue: str)->set :
    '''
    based on name of queue, return names of nodes to use
    :param queue: name of queue to use, longq7-mri or longq7-eng
    :return: set of nodes to used
    '''
    if queue == 'longq7-mri':
        all_nodes = set([f'nodenviv1000{"0" if node_num < 10 else ""}{node_num}'
                     for node_num in range(1, 17)])
    elif queue == 'longq7-eng':
        # return cpu nodes in longq7-eng, only one
        # gpu node in longq7-eng now, so no need for
        # scriptq
        all_nodes = set([f'nodeamd0{i}' for i in range(17,39)])
    else:
        raise Exception('unknown queue')
    return all_nodes
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='turn on debugging output')
    parser.add_argument('queue', help='queue to submit jobs to')
    parser.add_argument('script_file', help='file of commands to run via the sbatch utility') 
    args = parser.parse_args()
    
    logger = get_logger(level=logging.DEBUG if args.verbose else logging.INFO)
    logger.info('staring up')

    # node names in Koko are mostly like nodenviv1000
    # foolowed by the node number with a leading 0
    all_nodes = get_nodes_in_queue(queue) 
    # two nodes do not fit the pattern of other node names
    all_nodes.update(['nodegpu002', 'nodegpu003'])
    more_jobs = True
    while more_jobs:
        nodes_in_use = get_node_list()
        logger.debug(f'nodes in use {nodes_in_use}')
        available_nodes = all_nodes.difference(nodes_in_use)
        logger.debug(f'available_nodes {available_nodes}')
        if len(available_nodes) > 0:
            more_jobs = run_next_job(available_nodes, args.script_file, logger)
        else:
            logger.debug('no nodes available')
        time.sleep(10)

    
