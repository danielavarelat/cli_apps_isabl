#!/usr/bin/env python

import os
import argparse

from os.path import join
from os.path import basename
from os.path import abspath
from os.path import isdir

import re

FASTQ_REGEX = r"(([_.]R{0}[_.].+)|([_.]R{0}\.)|(_{0}\.))f(ast)?q(\.gz)?$"


def format_file_name(file_name):
    """Return destination file name."""
    file_name = basename(file_name)

    for index in [1, 2]:
        if re.search(FASTQ_REGEX.format(index), file_name):
            suffix = "_{}.fastq".format(index)
            letter_index_fastq = r"[_.]R{}([_.])?\.f(ast)?q".format(index)
            number_index_fastq = r"[_.]{}([_.])?\.f(ast)?q".format(index)
            letter_index_any_location = r"[_.]R{}[_.]".format(index)
            file_name = re.sub(letter_index_fastq, ".fastq", file_name)
            file_name = re.sub(number_index_fastq, ".fastq", file_name)
            file_name = re.sub(letter_index_any_location, "_", file_name)
            file_name = re.sub(r"[_.]f(ast)?q", suffix, file_name)

    return file_name


def symlink_input_data(outdir, sequencing_data):
    """Symlink fastq files using pcapcore expected naming."""
    links_dir = join(outdir, "input_data")
    sym_links = []

    if not isdir(links_dir):
        os.makedirs(links_dir)

    for src in map(abspath, sequencing_data):
        dst = join(links_dir, format_file_name(basename(src)))
        sym_links.append(dst)

        try:
            os.unlink(dst)
            os.symlink(src, dst)
        except OSError:
            os.symlink(src, dst)

    return sym_links


def _get_parser():
    parser = argparse.ArgumentParser(
        description="Create symlinks in {outdir}/input_data with file names "
        "as expected by bwa_mem.pl."
    )

    parser.add_argument(
        "--outdir", help="Output directory where bwa_mem.pl will be executed."
    )

    parser.add_argument(
        "sequencing_data", nargs="+", help="List of FASTQ, BAMS, or CRAMS."
    )

    return parser


if __name__ == "__main__":
    args = _get_parser().parse_args()
    symlink_input_data(args.outdir, args.sequencing_data)
