#!/bin/bash

#Configure home directory for Contiguator
CONTIGUATOR_HOME=/usr/local/contiguator/current

#Configure PATH for Blast
BLAST_HOME=/usr/local/blast/current

PATH="$BLAST_HOME/bin:$PATH"

export CONTIGUATOR_HOME BLAST_HOME PATH


