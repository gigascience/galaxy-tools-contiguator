#!/bin/bash

#Configure home directory for Contiguator
CONTIGUATOR_HOME=/usr/local/contiguator/current

BLAST_HOME=/usr/local/blast/current
MUMMER_HOME=/usr/local/mummer/current

PATH=$PATH:$BLAST_HOME/bin:$MUMMER_HOME/bin

export MUMMER_HOME CONTIGUATOR_HOME BLAST_HOME PATH


