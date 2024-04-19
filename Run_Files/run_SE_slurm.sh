#!/bin/bash

#SBATCH --cpus-per-task=1   # Amount of memory needed by each process (ppn) in the job.
#SBATCH --mem=64GB
#SBATCH --export=ALL


# casa's python requires a DISPLAY for matplot, so create a virtual X server
xvfb-run -d /home/casa/packages/pipeline/casa-6.4.1-12-pipeline-2022.1.1.5/bin/casa --pipeline --nogui --nologger -c  command_script.py
