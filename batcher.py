#!/usr/bin/env python
# script for running jobs as nodes become available
# we found that for jobs that use a lot of memory
# slurm will still batch some of those jobs
# to the same node, both jobs will fail
# however if we run them one at a time
# the jbos will run to completion

from our_util  import get_logger
import time
from find_missing import find_missing
from run_exp_list  import run_exp
import logging
import argparse
import subprocess
import copy

# this is system dependent, current cluster we have nodes
# nodenviv100001 through nodenviv100016
# here as a global so we don't have to
# allocate a new array evrey time we run
# get_availble_nodes
nodes = [f'nodenviv10000{i}' for i in range(1,10)] + [f'nodenviv1000{i}' for i in range(10,17)]

def get_available_nodes():
    """
    queries slurm for nodes in use
    then returns list of nodes not in use
    """
    sub_proc_arr = ["squeue", "-h", "-u", "jhancoc4", "-o", "%N"]
    sub_proc_out = subprocess.run(sub_proc_arr, capture_output=True)
    nodes_in_use = sub_proc_out.stdout.decode('utf8').strip().split('\n')
    available_nodes = [n for n in nodes if n not in nodes_in_use]
    return available_nodes if len(available_nodes) > 0 else None

def filter_not_done(exp_list, inclusion_list, exclusion_list):
    """
    remove any unwanted experiments, and keep only those
    desired
    :param exp_list: list of experiments from find_not_done
    :param inclusion_list: list of substrings of experiment names if substring in experiment
    name we keep it, otherwise we don't use it
    leave empty if not needed
    :param exclusion_list: list of substrings of experiment names to exlcude, if substring
    in experiment name we do not use it
    :reeturn: filtered list
    """
    res = []
    if inclusion_list and len(inclusion_list) > 0 and exclusion_list and len(exclusion_list) > 0:
        for e in exp_list:
            has_all_terms = True
            for i in inclusion_list:
                if i not in e:
                    has_all_terms = False
            if has_all_terms == True:
                res.append(e)
                    
        # have to use deep copy otherwise get infinite loop
        exp_list = copy.deepcopy(res)
        for e in exp_list:
            for ex in exclusion_list:
                if ex in e and e  in res:
                    res.remove(e)
        return res
    
    elif inclusion_list and len(inclusion_list) > 0:
        for e in exp_list:
            for i in inclusion_list:
                if i in e:
                    res.append(e)
        return res
    
    elif exclusion_list and len(exclusion_list) > 0:
        for e in exp_list:
            for i in exclusion_list:
                if i not in e:
                    res.append(e)
        return res
    
    else:
        return exp_list
    
    
logger = get_logger(logger_name="batcher", level=logging.DEBUG)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--pickle_file', '-p' , help='experiments pickled dictionary')
    parser.add_argument('--results_dir', '-r', help='directory containing results files')
    parser.add_argument('--inclusion_list', '-i', nargs='+',
                        help='list of keywords experiment names must have',
                        default=None, required=False)
    parser.add_argument('--exclusion_list', '-e', nargs='+',
                        help='list of keywords experiment names must not have',
                        default=None, required=False)
    parser.add_argument('--mode', '-m', default=None, required=False,
                        help='mode s or p for sequential or parallel (multithreaded)')
    args = parser.parse_args()
    logger.info(f'starting up with arguments {vars(args)}')
    # this controls how often the script wakes up
    # to check for available nodes
    interval = 30
    not_done = find_missing(args.pickle_file, args.results_dir)
    done = len(not_done) <= 0
    complete_msg = 'All experiments are complete.'
    if done:
        logger.info(complete_msg)
    while not done:
        available_nodes = get_available_nodes()
        if available_nodes:
            logger.info(f'number of pending experiments: {len(not_done)}')    
            not_done = filter_not_done(not_done, args.inclusion_list, args.exclusion_list)
            logger.debug(f'after filter, number pending experiments: {len(not_done)}')    
            # cut the list of experiments to run to the number of available nodes
            not_done = not_done[:len(available_nodes)]
            if len(not_done) == 0:
                done = True
            for exp_name, node in zip(not_done, available_nodes):
                cmd_out_str = run_exp(exp_name, args.pickle_file, node_name=node, mode=args.mode)
                logmsg = f"Output of sbatch command for running experiment {exp_name}:\n{cmd_out_str}"
                logger.info(logmsg)
                remaining_jobs = "\n".join(not_done)
                logger.info(f'remaining jobs:\n {remaining_jobs}')
        time.sleep(interval)
        not_done = find_missing(args.pickle_file, args.results_dir)
    logger.info(complete_msg)
