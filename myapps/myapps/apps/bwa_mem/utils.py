"""Applications utils."""

from os.path import join

import yaml

from . import pcapcore


def get_bwa_mem_pl_results(analysis):
    """Get bwa_mem.pl expected results."""
    base = join(analysis["storage_url"], analysis["targets"][0]["system_id"])

    with open(base + ".bam.md5", "r") as f:
        md5 = f.read()

    return {
        "bam": base + ".bam",
        "bai": base + ".bam.bai",
        "bas": base + ".bam.bas",
        "met": base + ".bam.met",
        "md5": md5,
    }


def write_groupinfo(target, outdir, sample_name):
    """Return path of of groupsinfo.yaml if can be created, else None."""
    groups = {}
    platform = target["platform"]
    center = target["center"]
    raw_data = []
    groupinfo_path = None

    for i in target["raw_data"]:
        if i["file_type"] not in {"BAM", "FASTQ_R1", "FASTQ_R2"}:
            continue

        raw_data.append(i["file_url"])
        data = i["file_data"] or {}
        group = {}

        if i["file_type"].startswith("FASTQ"):
            groups[pcapcore.format_file_name(i["file_url"])] = group
            group["CN"] = data.get("CN", center["slug"])
            group["PL"] = data.get("PL", platform["manufacturer"]).upper()
            group["PM"] = data.get("PM", platform["slug"])
            group["PU"] = data.get("PU", 1)

            if data.get("LB"):
                group["LB"] = data["LB"]

    if groups:
        groupinfo = dict(SM=sample_name, READGRPS=groups)
        groupinfo_path = join(outdir, "groupinfo.yaml")

        with open(groupinfo_path, "w") as f:
            yaml.dump(groupinfo, f, default_flow_style=False)

    return groupinfo_path, pcapcore.symlink_input_data(outdir, raw_data)
