#!/bin/bash

#PBS -V    # Export all environment variables from the qsub commands environment to the batch job.
#PBS -l pmem=64gb,pvmem=64gb       # Amount of memory needed by each process (ppn) in the job.
#PBS -d /lustre/aoc/students/ecarlson/data/J0925+1444_Custom_Size/ # Working directory (PBS_O_WORKDIR) set to your Lustre area
#PBS -l nodes=1:ppn=1 Number of nodes and the number of cores request
#PBS -m ae                 # Send mail on begin, end and abort




# casa's python requires a DISPLAY for matplot, so create a virtual X server
#ensure that the below path is pointed at your command script. 
xvfb-run -d /home/casa/packages/pipeline/casa-6.4.1-12-pipeline-2022.1.1.5/bin/mpicasa -n 16 --pipeline --nogui --nologger -c  command_script.py
