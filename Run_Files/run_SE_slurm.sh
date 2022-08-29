#!/bin/bash

#SBATCH --cpus-per-task=4   # Amount of memory needed by each process (ppn) in the job.
#SBATCH -D /lustre/aoc/students/ecarlson/data/J0000+0000/working/ # Working directory (PBS_O_WORKDIR) set to your Lustre area
#SBATCH --mem=64GB
#SBATCH --mail-type=END,FAIL                 # Send mail on begin, end and abort
#SBATCH --mail-user=ecarlson@nrao.edu
#SBATCH --export=ALL


# casa's python requires a DISPLAY for matplot, so create a virtual X server
xvfb-run -d /home/casa/packages/pipeline/casa-6.1.3-3-pipeline-2021.1.1.29/bin/casa --pipeline --nogui --nologger -c  command_script.py
