import binascii
import gzip
from statistics import median
from getpass import getuser
from os import stat
from os.path import join
from pwd import getpwuid

import click

from isabl_cli.settings import system_settings


def find_owner(filename):
    """Find directory owner."""
    return getpwuid(stat(filename).st_uid).pw_name


def assert_same_owner(path):
    """Validate that a path is owned by the same user."""
    try:
        assert find_owner(path) == getuser(), f"{path} must be owned by {getuser()}"
    except AssertionError as error:
        raise click.UsageError(str(error))
    except FileNotFoundError:
        pass


def get_docker_command(image, entrypoint=None, docker_args=""):
    """Build docker command."""
    vol = system_settings.BASE_STORAGE_DIRECTORY
    cmd = f"docker run -v {vol}:{vol} {docker_args} "

    if entrypoint is not None:
        cmd += f"--entrypoint {entrypoint} "

    return " ".join(f"{cmd}{image}".split()) + " "


def first(items):
    """Get first item or None from list."""
    return next(iter(items or []), None)


def is_gz_file(f):
    """Return true if a given file is gziped."""
    with open(f, "rb") as fin:
        return binascii.hexlify(fin.read(2)) == b"1f8b"


def count_variants(filename, content=None):
    """Get the number of variants from file."""
    open_fn = gzip.open if is_gz_file(filename) else open
    count = 0
    with open_fn(filename, "rt") as ifile:
        for line in ifile:
            if not line.startswith("#"):
                if content:
                    if content in line:
                        count += 1
                else:
                    count += 1
    return count


def merge_paired_fastqs(target, outdir):
    """Merge paired-end fastqs into a single file for each end."""
    left, right = target.get_fastq()
    left_fq = join(outdir, target.system_id + "_1.fq.gz")
    right_fq = join(outdir, target.system_id + "_2.fq.gz")
    commands = []

    if is_gz_file(left[0]):
        commands += [f"cat {' '.join(left)} > {left_fq}"]
        commands += [f"cat {' '.join(right)} > {right_fq}"]
    else:
        commands += [f"cat {' '.join(left)} | " f"gzip -c > {left_fq}"]
        commands += [f"cat {' '.join(right)} | " f"gzip -c > {right_fq}"]

    remove = [f"rm {left_fq} {right_fq}"]

    return (left_fq, right_fq), commands, remove


def est_read_len(fq, reads=100):
    """Guess read length from a first set of reads in fastq file."""
    if is_gz_file(fq):
        openf = gzip.open
    else:
        openf = open
    readlens = []
    with openf(fq) as f:
        try:  # File less than 4*reads lines
            for _ in range(reads):
                next(f)
                readlens.append(len(next(f).strip()))
                next(f), next(f)
        except:
            pass
    return median(readlens)
