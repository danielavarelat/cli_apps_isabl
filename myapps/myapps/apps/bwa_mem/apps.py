from isabl_cli import AbstractApplication
from isabl_cli import options

from myapps.utils import get_docker_command

from . import constants
from . import utils

class BwaMem(AbstractApplication):

    NAME = "BWA_MEM"
    #VERSION = "0.7.17-r1188"
    VERSION = "1"
    ASSEMBLY = "GRCh37"
    SPECIES = "HUMAN"
    URL = "https://github.com/cancerit/PCAP-core/wiki/Scripts-Reference-implementations"

    cli_help = "Align DNA data with bwa-mem."
    cli_options = [options.TARGETS]
    application_description = constants.APPLICATION_DESCRIPTION
    application_results = constants.APPLICATION_RESULTS
    application_settings = {
        "cores": {"WG": 32, "WE": 32, "TD": 32},
        "reference": "reference_data_id:genome_fasta",
        "bwa_mem_pl": get_docker_command("leukgen/docker-pcapcore:v0.1.1"),
    }

    def get_experiments_from_cli_options(self, **cli_options):
        return [([i], []) for i in cli_options["targets"]]

    def validate_experiments(self, targets, references):
        self.validate_dna_only(targets + references)
        self.validate_single_data_type(targets + references)
        self.validate_one_target_no_references(targets, references)
        self.validate_methods(targets, ["WG", "WE", "TD"])
        assert not targets[0].is_pdx, "Use Disambiguate for PDX experiments"

    def validate_settings(self, settings):
        self.validate_reference_genome(settings.reference)

    def get_command(self, analysis, inputs, settings):
        #sequencing_data = analysis.targets[0].sequencing_data
        return self.get_bwa_mem_command(analysis, inputs, settings)

    def get_bwa_mem_command(self, analysis, inputs, settings):
        target = analysis["targets"][0]
        method = target["technique"]["method"]
        sample_name = target["system_id"]
        outdir = analysis["storage_url"]
        groupinfo, sequencing_data = utils.write_groupinfo(target, outdir, sample_name)
        command = [
            settings.bwa_mem_pl,
            "-fragment",
            10,
            "-reference",
            settings.reference,
            "-threads",
            settings.cores[method],
            "-map_threads",
            settings.cores[method],
            "-sample",
            sample_name,
            "-outdir",
            outdir,
        ]

        if target.technique["custom_fields"].get("nomarkdup"):
            command += ["-nomarkdup"]

        if groupinfo:
            command += ["-groupinfo", groupinfo]

        return (
            " ".join(map(str, command + sequencing_data))
            + f" && sudo chown -R ec2-user {outdir}"
            # make sure index is older than bam
            + f" && touch {outdir}/{sample_name}.bam.bai"
        )

    def get_analysis_results(self, analysis):
        results = utils.get_bwa_mem_pl_results(analysis)

        self.update_experiment_bam_file(
            experiment=analysis["targets"][0],
            bam_url=results["bam"],
            analysis_pk=analysis["pk"],
        )
        return results