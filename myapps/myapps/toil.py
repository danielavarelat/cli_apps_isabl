"""Toil utils."""

from os.path import isdir
from os.path import isfile
from os.path import join

from myapps.utils import assert_same_owner


def build_toil_command(
    outdir,
    executable,
    args,
    jobname="-",
    batch_system="CustomLSF",
    jobstore="jobstore",
    state_polling_wait=60,
    max_local_jobs=2000,
    toil="toil",
    restart=False,
    stats_name="stats_toil",
):  # pylint: disable=too-many-arguments
    """
    Normalize the way toil is called.

    Arguments:
        outdir (str): path to output directory.
        jobname (str): job name.
        jobstore (str): name of jobstore.
        executable (str): name or path to executable toil script.
        args (list): list of application specific arguments.
        batch_system (str): either LSF or CustomLSF.
        state_polling_wait (int): seconds before status is checked.
        max_local_jobs (int): max number of jobs at a given time.
        toil (str): path to toil executable.
        restart (bool): whether to restart the job.
        stats_name (str): name for stats file.

    Returns:
        str: a toil command.
    """
    jobname = f'"{jobname}"'
    jobstore = join(outdir, jobstore)
    stats_json = join(outdir, f"{stats_name}.json")
    stats_txt = join(outdir, f"{stats_name}.txt")

    # skip if retries to restart a completed job
    if restart and not isdir(jobstore) and isfile(stats_txt):
        return "echo 'Skipping {} as it has finished already'".format(jobstore)

    restart = restart and isdir(jobstore)
    logs_dirs = join(outdir, "logs_toil")
    logs_path = join(outdir, "head_job.toil.restart" if restart else "head_job.toil")

    # assert same owner, otherwise toil will fail
    assert_same_owner(outdir)
    assert_same_owner(jobstore)

    command = [
        executable,
        jobstore,
        "--stats",
        "--disableCaching",
        "--disableChaining",
        "--rotatingLogging",
        "--batchSystem",
        batch_system,
        "--writeLogs",
        logs_dirs,
        "--logFile",
        logs_path,
        "--statePollingWait",
        str(state_polling_wait),
        "--maxLocalJobs",
        str(max_local_jobs),
        "--setEnv",
        f"TOIL_LSF_JOBNAME='{jobname}'",
    ] + args

    if restart:
        command += ["--restart"]
    else:
        # toil can't report stats on restart
        # this got fixed at https://github.com/DataBiosphere/toil/pull/2513
        command += [
            "&&",
            toil,
            "stats",
            "--raw",
            jobstore,
            "1>",
            stats_json,
            "&&",
            toil,
            "stats",
            "--human",
            jobstore,
            "1>",
            stats_txt,
        ]

    return " ".join(map(str, command + ["&&", toil, "clean", jobstore]))
