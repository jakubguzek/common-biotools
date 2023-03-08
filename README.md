# Common Bioinformatics Toolkit

A Work In Progress set of command-line tools for common bioinformatics operations written in Python and Rust.

For now there are two simple modules, one finished and one still in development. Detailed information about given module can be found in README files inside particular module directory.

## gp2fasta

gp2fasta is a CLI converter which can be used to convert gp files from NCBI GenPept or GeneBank format to fasta. Its can create fasta files with short and accurate identifiers for sequence.

Written in Python.

## proebs

probes is a CLI program for generation of unique DNA probes for a given set of sequences (in fasta file format). It should be able to find shortest probes that are unique for a given set of sequences.

Written in Rust. Still in development.

## TODO
 - build and development
 - common CLI for modules maybe
