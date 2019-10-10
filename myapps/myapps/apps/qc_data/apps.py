from os.path import isfile
from os.path import join
import csv
import subprocess
import sys

from isabl_cli import AbstractApplication
from isabl_cli import api
from isabl_cli import options
from isabl_cli import exceptions

from myapps.utils import get_docker_command

from .constants import BASE_APPLICATION_RESULTS
from .constants import APPLICATION_RESULTS
from .constants import PICARD_BASE_COMMANDS
from .constants import PICARD_TARGETED_COMMANDS


class QualityControl(AbstractApplication):

    """See https://quay.io/repository/biocontainers/rna-seqc."""

    NAME = "QC_DATA"
    VERSION = "0.1.0"

    cli_help = "Get Quality Control metrics for NGS data."
    cli_options = [options.TARGETS]
    application_project_level_results = BASE_APPLICATION_RESULTS
    application_individual_level_results = BASE_APPLICATION_RESULTS
    application_results = APPLICATION_RESULTS
    application_description = "Quality Control metrics for NGS data."
    application_settings = {
        "reference": "reference_data_id:genome_fasta",
        "java_args": "-Xmx4g -XX:-UsePerfData",
        # RNA settings
        "gc_gencode": None,
        "fasta_rrna": None,
        "gtf": None,
        # executables
        "multiqc": get_docker_command("ewels/multiqc:v1.5", "multiqc"),
        "picard": get_docker_command("leukgen/docker-picard"),
        "fastqc": get_docker_command("biocontainers/fastqc:v0.11.5", "fastqc"),
        "rna_seqc": get_docker_command(
            "quay.io/biocontainers/rna-seqc:1.1.8--2", "rna-seqc"
        ),
    }

    def get_experiments_from_cli_options(self, **cli_options):
        return [([i], []) for i in cli_options["targets"]]

    def validate_experiments(self, targets, references):
        self.validate_bams(targets + references)
        self.validate_one_target_no_references(targets, references)

        if targets[0].technique.analyte == "DNA":
            self.validate_bedfiles(targets + references)

        # msk specific validation
        for i in targets[0]["sequencing_data"]:
            if i["file_type"].startswith("FASTQ") and i["file_url"]:
                assert not i["file_url"].startswith(
                    "/warm"
                ), "fastq in /warm, cant process"

    def validate_settings(self, settings):
        self.validate_reference_genome(settings.reference)

    def get_command(self, analysis, inputs, settings):
        target = analysis["targets"][0]
        outdir = analysis["storage_url"]
        system_id = target["system_id"]
        fastqc_dir = join(outdir, "fastqc")
        picard_dir = join(outdir, "picard")
        multiqc_dir = join(outdir, "multiqc")
        rna_seqc_dir = join(outdir, "rna_seqc")
        commands = [f"mkdir -p {multiqc_dir}"]
        bampath = self.get_bam(target)

        # build fastqc command, it is possible some samples don't gave fastq
        fastqc_cmds = []
        fastqc_input = join(fastqc_dir, f"{system_id}.fastq.gz")

        for i in target["sequencing_data"]:
            if i["file_type"].startswith("FASTQ"):
                fastq = i["file_url"]

                if fastq.endswith(".gz"):
                    fastqc_cmds.append(f"cat {fastq} > {fastqc_input}")
                else:
                    fastqc_cmds.append(f"gzip -c {fastq} >> {fastqc_input}")

        if fastqc_cmds:
            commands += [f"mkdir -p {fastqc_dir}"] + fastqc_cmds
            commands += [f"{settings.fastqc} -o {fastqc_dir} {fastqc_input}"]
            commands += [f"rm {fastqc_input}"]

        # run picard for DNA data, bedfiles can't have a chr prefix
        if target["technique"]["analyte"] == "DNA":
            commands.append(f"mkdir -p {picard_dir}")
            picard_cmd = f'{settings.picard} -j "{settings.java_args}" '
            picard_kwargs = dict(
                bampath=bampath,
                reference=settings.reference,
                outbase=join(picard_dir, system_id),
                bedfile=self.get_bedfile(target),
            )

            for i in PICARD_BASE_COMMANDS:
                commands.append(picard_cmd + i.format(**picard_kwargs))

            if target["technique"]["method"] in ["WE", "TD"]:
                for i in PICARD_TARGETED_COMMANDS:
                    commands.append(picard_cmd + i.format(**picard_kwargs))

        # run RNA-SeQC for RNA data
        if target["technique"]["analyte"] == "RNA":
            if not settings.gtf or not settings.fasta_rrna:
                raise exceptions.ConfigurationError(
                    "Settings 'gtf' and 'fastq_rrna' must be set"
                )

            commands.append("mkdir -p {0}".format(rna_seqc_dir))
            strat_args = ""

            if settings.gc_gencode:
                strat_args = f"-strat gc -gc {settings.gc_gencode}"

            commands.append(
                f"{settings.rna_seqc} {settings.java_args} "
                f"-o {join(rna_seqc_dir, system_id)} "
                f"-r {settings.reference} "
                f"-t {settings.gtf} "
                f"-BWArRNA {settings.fasta_rrna} "
                f"-s \"'{system_id}|{bampath}|NA'\" "
                f"{strat_args}"
            )

        # run multiqc on current sample
        commands.append(f"{settings.multiqc} -f -p -o {multiqc_dir} {outdir}")

        return " && ".join(commands)

    def get_analysis_results(self, analysis):
        target = analysis["targets"][0]
        outdir = analysis["storage_url"]
        multiqc = join(outdir, "multiqc")
        multiqc_data = join(multiqc, "multiqc_data")

        results = {
            "multiqc_html": join(multiqc, "multiqc_report.html"),
            "multiqc_data": join(multiqc_data, "multiqc_data.json"),
            "multiqc_stats": join(multiqc_data, "multiqc_general_stats.txt"),
            "read_length": None,
        }

        for key, i in results.items():
            if key == "multiqc_data":
                continue
            assert True if i is None else isfile(i), f"Missing result {i}"

        if target["technique"]["analyte"] == "DNA":
            read_length_column = "MEAN_READ_LENGTH"
            read_length_path = "multiqc_picard_AlignmentSummaryMetrics.txt"
            read_length_path = join(multiqc_data, read_length_path)
        else:
            read_length_column = "Read Length"
            read_length_path = join(multiqc_data, "multiqc_rna_seqc.txt")

        with open(read_length_path) as f:
            row = next(csv.DictReader(f, delimiter="\t"))
            results["read_length"] = float(row[read_length_column])
            api.patch_instance(
                endpoint="experiments",
                instance_id=target["pk"],
                read_length=results["read_length"],
            )

        return results

    def validate_project_analyses(self, project, analyses):
        assert (
            len(analyses) <= 500
        ), "Project level QC only valid for projects with lestt than 500 samples"

    # -----------
    # MERGE LOGIC
    # -----------

    def get_project_analysis_results(self, analysis):
        return self.get_merged_results(analysis)

    def get_individual_analysis_results(self, analysis):
        return self.get_merged_results(analysis)

    def merge_project_analyses(self, analysis, analyses):
        return self.merge_analyses(
            analysis,
            analyses,
            f"QC report for project {analysis['project_level_analysis']['pk']} "
            f"created using {len(analyses)} samples.",
        )

    def merge_individual_analyses(self, analysis, analyses):
        return self.merge_analyses(
            analysis,
            analyses,
            f"QC report for individual {analysis['individual_level_analysis']['pk']} "
            f"created using {len(analyses)} samples.",
        )

    def get_merged_results(self, analysis):
        outdir = analysis["storage_url"]
        multiqc_data = join(outdir, "multiqc_data")
        results = {
            "multiqc_html": join(outdir, "multiqc_report.html"),
            "multiqc_data": join(multiqc_data, "multiqc_data.json"),
            "multiqc_stats": None,
        }

        for i, j in results.items():
            if i != "multiqc_stats":
                assert isfile(j), f"Missing result {j}"
            elif j and isfile(j):
                results["multiqc_stats"] = join(
                    multiqc_data, "multiqc_general_stats.txt"
                )

        return results

    def merge_analyses(self, analysis, analyses, comment):
        subprocess.check_call(
            [i for i in self.settings.multiqc.split(" ") if i]
            + [
                "--comment",
                comment,
                "--outdir",
                analysis["storage_url"],
                "--data-dir",
                "--force",
            ]
            + [i["storage_url"] for i in analyses],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )


class QualityControlGRCh37(QualityControl):

    ASSEMBLY = "GRCh37"
    SPECIES = "HUMAN"


class QualityControlGRCm38(QualityControl):

    ASSEMBLY = "GRCm38"
    SPECIES = "MOUSE"
