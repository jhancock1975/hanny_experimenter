#!/usr/bin/env python3
import subprocess
import logging
from our_util import get_logger

if __name__ == '__main__':
    logger = get_logger()
    # output of subprocess is a CompletedProcess object
    cp = subprocess.run(['squeue', '-u jhancoc4' '-o "%N"', '-h'])
    logger.debug(f'cp.stdout = {cp.stdout}')
    
