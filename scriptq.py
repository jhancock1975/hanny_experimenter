#!/usr/bin/env python3
import subprocess
import logging
from our_util import get_logger

if __name__ == '__main__':
    logger = get_logger()
    # output of subprocess is a CompletedProcess object
    # which has a stdout member when capture_output equals True
    # stdout is a bytes array, we convert to a string, then split on newline to
    # get a list of nodes currently in use
    node_list = subprocess.run(['squeue','-h', '--me', '-o', '%N'],
                               capture_output=True).decode('utf-8').split('\n')
    logger.debug(f'node_list = {node_list}')
    
