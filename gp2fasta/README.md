# gp2fasta

gp2fasta is a CLI converter which can be used to convert gp files from NCBI GenPept or GeneBank format to fasta. Its can create fasta files with short and accurate identifiers for sequence. 

## Options for sequence identifier content
Converter can include some of the metadata from gp file in sequence identifier of fasta file.

Fields that can be included and associated options:
| cli option | gp field         | notes                               |
|----------- |----------------- |------------------------------------ |
| -i         | LOCUS/GI/VERSION | include gi or locus as id           |
| -g         | DEFINITON        | include gene name in identifier     |
| -a         | DEFINITION       | include some additional information |
| -o         | ORGANISM         | include organism name               |
| -f         | -                | format organism name                |

## Example usages
given gp file dis3.gp:
```
LOCUS       AAH38101                 796 aa            linear   PRI 18-JAN-2007
DEFINITION  DIS3 protein [Homo sapiens].
ACCESSION   AAH38101
VERSION     AAH38101.1  GI:71296758
DBSOURCE    accession BC038101.1
KEYWORDS    MGC.
SOURCE      Homo sapiens (human)
  ORGANISM  Homo sapiens
            Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi;
            Mammalia; Eutheria; Euarchontoglires; Primates; Haplorrhini;
            Catarrhini; Hominidae; Homo.
REFERENCE   1  (residues 1 to 796)
  AUTHORS   Strausberg,R.L., Feingold,E.A., Grouse,L.H., Derge,J.G.,
            Klausner,R.D., Collins,F.S., Wagner,L., Shenmen,C.M., Schuler,G.D.,
...
...
ORIGIN      
        1 msadnqlqvi fitndrrnke kaieegipaf tceeyvkslt anpelidrla clseegneie
       61 sgkiifsehl plsklqqgik sgtylqgtfr asrenyleat vwihgdseen keiilqglkh
      121 lnravhediv avellpksqw vapssvvlhd egqneedvek eeetermlkt avsekmlkpt
...
```
command
```
$ ./gp2fasta dis3.gp output.fas
```
outputs file output.fas containing:
```
>AAH38101
MSADNQLQVIFITNDRRNKEKAIEEGIPAFTCEEYVKSLTA...
```
command-line options can be used to affect what is included in sequence identifier like so:
```
$ ./gp2fasta -gi dis3.gp output.fas
```
outputs file output.fas containing:
```
>71296758-DIS3 protein [Homo sapiens]
MSADNQLQVIFITNDRRNKEKAIEEGIPAFTCEEYVKSLTA...
```
and some additional formatting can be done:
```
$ ./gp2fasta -gioa -f="med" dis3.gp output.fas
```
outputs file output.fas containing:
```
>H.sapiens-71296758-DIS3 protein [Homo sapiens]
MSADNQLQVIFITNDRRNKEKAIEEGIPAFTCEEYVKSLTA...
```

## Detailed help
```
usage: gp2fasta [-h] [-i] [-g] [-a] [-o] [-f FORMAT] [-s SEPARATOR] [-n] input_file output_file

gp2fasta is converting gp files from NCBI GenPept or GenBank format to fasta. Its main purpose is to create fasta files with
short, but still accurate headers for sequence. By default the header/identifier of a sequence will be just its locus. See
command-line options for more functionalities. Additionally name of organism can be included in the header, detailed
information (gene name), and additional information (see -a option).

positional arguments:
  input_file            input file in gp format
  output_file           output file in fasta format

options:
  -h, --help            show this help message and exit
  -i, --gi-identifier   use gi instead of locus as id if present
  -g, --genename        add gene name to identifier
  -a, --additional      add additional information to identifier. Additional information is added as a suffix to the
                        identifier (P -> PREDICTED; s -> similar; h -> hypothetical protein; u -> unnamed protein product; n
                        -> novel; p -> putative; o -> open reading frame).
  -s SEPARATOR, --separator SEPARATOR
                        character to separate portions of identifier (default: '-')
  -n, --no-overwrite    don't overwrite existing files when creating fasta file

species:
  -o, --organism        add organism name to identifier
  -f FORMAT, --format FORMAT
                        how to format organism name ('long', 'med', 'short'). Only workd if -o option was passed.
```

## Implementation details

gp2fasta is a short program written in python. All relevant functions are inside gp2fasta.py file inside src/gp2fasta. Executable gp2fasta should be used when calling the script. Exemplary data and outputs are provided in data/ and test_output/ directories. 

Based on: [gp2fasta](gp2fasta.netmark.pl)
