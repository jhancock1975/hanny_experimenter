#!/home/jhancoc4/venv/py-3.8.7/bin/python
# this script distributes jobs round-robin style to all ndoes in a list
# good for up to medium sized data
import sys
import os
import subprocess
import argparse
import json
# we *want* that to throw a key error if the n_jobs environment variable is not set
n_jobs=os.environ['n_jobs']

def run_exp(exp_name, pickle_file_name, node_name, ram=None):
    """
    runs experiment with sbatch command
    TODO: how to handle requested ram?  move to exp def?
    :param exp_name: name of experiment, should be key to experiment in pickled dictionary in file
    named args.pickle_file_name
    """
    if not ram:
        # "Go big or go home'
        ram = '164G'
    if not os.path.isdir('./logs'):
        os.makedirs('./logs')
    command = subprocess.run(['sbatch',
                    f'--nodelist={node_name}',
                    '-o' , f'./logs/{exp_name}.log',
                    '--comment',
                    exp_name,
                    f'--cpus-per-task={n_jobs}',
                    f'--mem=',
                    '-p',
                    'longq7-mri',
                    '/home/jhancoc4/git/spring-2021-research/one_parallel_with_resume.py',
                    '-f'
                    f'{pickle_file_name}',
                    '-e',
                    exp_name], capture_output=True)
    return json.dumps( {'stdout': command.stdout.decode('utf8'),
                        'stderr': command.stderr.decode('utf8')},
                       indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Run slurm experiments, we find slurm sends too many jobs to the same node so we send them to all nodes uniformly, this program will create a directory named logs that will hold log files for all experiments in the same directory it is invoked from.')
    parser.add_argument('-e', '--exp_name_list_file', help='file of experiment names, one per line')
    parser.add_argument('-p', '--pickle_file_name', help='pickle file name containing experiment definitions')
    parser.add_argument('-n', '--node_list', help='space separated list of last two characters (digits) of nodes to run experiments on, e.g. 01 05 16', nargs='+')
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    # list of nodes to submit jobs to
    base_node_name = 'nodenviv1000'
    node_numbers  = args.node_list

    os.makedirs('./logs', exist_ok=True)

    nodes = [f'{base_node_name}{node_numbers[i]}' for i in range(len(node_numbers))]
    with open(args.exp_name_list_file, 'r') as f:
        exp_names = f.read().splitlines()
    i = 0
    for exp_name in exp_names:
        i += 1
        run_exp(exp_name, args.pickle_file_name, node_name=nodes[i % len(nodes)], ram='164G')