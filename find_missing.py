#!/usr/bin/env python

# This program is for finding experiments
# that still need to run when the experiments
# are generated in a dictionary that conforms
# to the slurm_experimenter framework
import os
import argparse
import dill as pickle
import sys
import subprocess

def find_missing(pickle_file, results_dir):
    command = subprocess.run(['squeue', '-u', f'{os.environ["USER"]}', '-h', f'-o "%j|%k" '], capture_output=True)
    running_jobs = []
    std_out_str = command.stdout.decode('utf-8')
    for j in std_out_str.split('\n'):
        if 'mate-terminal' in j:
            continue
        if len(j.strip())==0:
            continue
        else:
            running_jobs.append(j.split('|')[1].replace('"', '').strip())
    with open(pickle_file, 'rb') as f:
        d = pickle.loads(f.read())
    exp_names  = []
    for exp_name in d.keys():
        found = False
        for r_name in os.listdir(results_dir):
            if r_name.startswith(exp_name):
                    found = True
                    break
        for r_name in running_jobs:
            if r_name.startswith(exp_name):
                found = True
                break
        if not found:
            exp_names.append(exp_name)
    return exp_names

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pickle_file', '-p' , help='experiments pickled dictionary')
    parser.add_argument('--results_dir', '-r', help='directory containing results files')
    args = parser.parse_args()
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    to_run_exps = find_missing(args.pickle_file, args.results_dir)
    for exp_name in to_run_exps:
        print(exp_name)
