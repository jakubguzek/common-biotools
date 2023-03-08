#!/usr/bin/env python
# MIT License
#
# Copyright (c) 2023 Jakub J. Guzek
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import pathlib
import re
import sys
from typing import Dict, List

# Keep script name in global constant (for error messages).
SCRIPT_NAME = pathlib.Path(__file__).name


def parse_args() -> argparse.Namespace:
    """Returns parsed command-line arguments of the script."""
    description = ("gp2fasta is converting gp files from NCBI GenPept or GenBank format "
                   "to fasta. Its main purpose is to create fasta files with short, "
                   "but still accurate headers for sequence. By default the header/identifier "
                   "of a sequence will be just its locus. See command-line options for more "
                   "functionalities. Additionally name of organism can be included in the header, "
                   "detailed information (gene name), and additional information (see -a option).")
    parser = argparse.ArgumentParser(description=description)
    organism = parser.add_argument_group("species")
    parser.add_argument(
        "gp", type=str, metavar="input_file", help="input file in gp format"
    )
    parser.add_argument(
        "fasta", type=str, metavar="output_file", help="output file in fasta format"
    )
    parser.add_argument(
        "-i",
        "--gi-identifier",
        action="store_true",
        help="use gi instead of locus as id if present",
    )
    parser.add_argument(
        "-g", "--genename", action="store_true", help="add gene name to identifier"
    )
    parser.add_argument(
        "-a",
        "--additional",
        action="store_true",
        help=("add additional information to identifier. Additional information is added as a suffix "
              "to the identifier (P -> PREDICTED; s -> similar; h -> hypothetical protein; "
              "u -> unnamed protein product; n -> novel; p -> putative; o -> open reading frame)."),
    )
    organism.add_argument(
        "-o", "--organism", action="store_true", help="add organism name to identifier"
    )
    organism.add_argument(
        "-f",
        "--format",
        type=str,
        help="how to format organism name ('long', 'med', 'short'). Only workd if -o option was passed.",
    )
    parser.add_argument(
        "-s",
        "--separator",
        type=str,
        default="-",
        help="character to separate portions of identifier (default: '-')",
    )
    parser.add_argument(
        "-n",
        "--no-overwrite",
        action="store_true",
        help="don't overwrite existing files when creating fasta file",
    )
    return parser.parse_args()


def parse_metadata(lines: List[str]) -> Dict[str, str]:
    """Returns a hash map with metadata identifiers and values from gp file."""
    metadata: Dict[str, str] = {}
    # Regular expression matching identifiers and value from gp file.
    #
    # (^[A-Z]+)\s+(.+)  Matches identifiers that beggin on leftmost side of
    #                   a gp file (^[A-Z]+), such as LOCUS, DEFINITION, ACCESSION etc.
    #                   and values (.+) after indeterminate number of whitespaces (\s+)
    #                   after the identifier. Groups identifier and value.
    # OR
    # ^\s+([A-Z]{5,1000}?)\s+(.+)   Matches identifier that begin on the left side
    #                               of gp file but after indeterminate number of whitespaces
    #                               (^\s+([A-Z]{5,1000}?)) and values similarly to previous
    #                               regular expression.
    key_value_regex = re.compile("(^[A-Z]+)\s+(.+)|^\s+([A-Z]{5,1000}?)\s+(.+)")
    # Check all lines for regular expressions.
    for line in lines:
        patterns = re.search(key_value_regex, line)
        # Save matches to hash map if any are found.
        if patterns:
            groups = patterns.groups()
            if (groups[0], groups[1]) != (None, None):
                metadata.setdefault(groups[0], groups[1])
            elif (groups[2], groups[3]) != (None, None):
                metadata.setdefault(groups[2], groups[3])
    return metadata


def parse_sequence(lines: List[str]) -> str:
    """Returns a protein sequence from gp file."""
    sequence: str = ""
    # Regular expression to match only lines with protein sequences.
    # Matches only on lines where there is number after indeterminate
    # number of whitespaces and dequence of lowercase letters after
    # indeterminate numebr of whitespaces after the number.
    sequence_pattern = re.compile("^\s+[0-9]+\s+([a-z\s]+)$")
    # Check all lines for regular expressions
    for line in lines:
        patterns = re.search(sequence_pattern, line)
        # Add sequence part of the match to sequence variable.
        if patterns:
            sequence += patterns.groups()[0].strip("\n")
    # Return sequence stripped of newline characters, whitespaces in the middle
    # and with all letters capitalized.
    return sequence.strip("\n").replace(" ", "").upper()


def create_suffix_from_additional_info(definition: str) -> str:
    """Return suffix that can be added at the end of the identifier.

    Information used to create suffix is taken from DEFINITION field
    in gp file."""
    suffix = ""
    if "PREDICTED" in definition:
        suffix += "P"
    if "similar" in definition:
        suffix += "s"
    if "hypothetical protein" in definition:
        suffix += "h"
    if "unnamed protein product" in definition:
        suffix += "u"
    if "novel" in definition:
        suffix += "n"
    if "putative" in definition:
        suffix += "p"
    if "open reading frame" in definition:
        suffix += "o"
    return suffix


def create_identifier(parsed_data: Dict[str, str], args: argparse.Namespace) -> str:
    """Returns a string representing identifier to be used in output fasta file."""
    identifier = ">"
    # Simple anonymous functions for formatting of organism name.
    # All of them can possibly raise IndexError, ValueError or TypeError
    # and it should be handled.
    short = lambda s: s.split(" ")[0][:3] + s.split(" ")[1][:3]
    med = lambda s: s.split(" ")[0][0] + "." + s.split(" ")[1]
    long = lambda s: s.split(" ")[0] + " " + s.split(" ")[1]
    # Logic for creation of identifier.
    # Add formatted organism name.
    if args.organism:
        try:
            if args.format == "med":
                identifier += med(parsed_data.get("ORGANISM", "")) + args.separator
            elif args.format == "short":
                identifier += short(parsed_data.get("ORGANISM", "")) + args.separator
            else:
                identifier += long(parsed_data.get("ORGANISM", "")) + args.separator
        except (IndexError, ValueError, TypeError):
            organism = parsed_data.get("ORGANISM", "")
            print(
                f"{SCRIPT_NAME}: warning: Wasn't able to correctly parse organism name'{organism}'!"
            )
            identifier += organism + args.separator
    # Add gi or locus as id.
    if args.gi_identifier:
        try:
            identifier += parsed_data.get("VERSION", "").split(" ")[-1].split(":")[-1]
        except IndexError:
            print(
                f"{SCRIPT_NAME}: warning: Wasn't able to correctly parse gi, using locus as id!"
            )
            identifier += parsed_data.get("LOCUS", "").split(" ")[0]
    else:
        identifier += parsed_data.get("LOCUS", "").split(" ")[0]
    # Add gene name after locus or gi.
    if args.genename:
        identifier += args.separator + parsed_data.get("DEFINITION", "").strip(" ,.")
    # Add additional information in form of a suffix at the end of the identifier.
    if args.additional:
        if suffix := create_suffix_from_additional_info(
            parsed_data.get("DEFINITION", "")
        ):
            identifier += args.separator + suffix
    return identifier


def parse_gp(filepath: pathlib.Path) -> Dict[str, str]:
    """Returns a hash map with data from gp file.

    This includes metadata and sequence data."""
    data: Dict[str, str] = {}
    with open(filepath, "r") as file:
        lines = file.readlines()
    # Add metadata to data hash map.
    data.update(parse_metadata(lines))
    # Add sequence data to data hash map.
    data.setdefault("sequence", parse_sequence(lines))
    return data


def main(args: argparse.Namespace) -> int:
    input = pathlib.Path(args.gp)
    # Print more concise error message if input file doesn't exist.
    try:
        data = parse_gp(input)
    except FileNotFoundError:
        print(f"{SCRIPT_NAME}: error: [Errrno 2] No such file or directory '{input}'")
        return 2
    output = pathlib.Path(args.fasta)
    # Return early with failure if output file exist and -n option was passed.
    if output.exists() and args.no_overwrite:
        print(f"{SCRIPT_NAME}: error: File {output} exists!")
        return 1
    # Write converted data to output file.
    with open(output, "w") as file:
        file.write(create_identifier(data, args) + "\n")
        file.write(data.get("sequence", "null"))
    return 0


# Run main if script was called directly and not imported by other python module.
if __name__ == "__main__":
    sys.exit(main(parse_args()))
