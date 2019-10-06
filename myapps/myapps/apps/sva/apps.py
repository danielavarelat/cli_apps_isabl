from os.path import isfile
from os.path import join

from isabl_cli import AbstractApplication
from isabl_cli import options

from myapps.utils import get_docker_command


class Svaba(AbstractApplication):
    ASSEMBLY = "GRCh37"
    SPECIES = "HUMAN"
    NAME = "SVABA"
    VERSION = "0.2.1"

    cli_help = "Find structural variants with Svaba."
    cli_options = [options.PAIRS, options.PAIRS_FROM_FILE]
    application_description = cli_help
    application_results = {
        "svs": {
            "frontend_type": "tsv-file",
            "description": "Svaba somatic SVS VCF.",
            "verbose_name": "Somatic SVS VCF",
            "external_link": None,
        }
    }
    application_settings = {
        "svab": get_docker_command("papaemmelab/docker-svaba:v1.0.0"),
        "reference": "reference_data_id:genome_fasta",
        "cores": "16",
    }

    def get_experiments_from_cli_options(self, **cli_options):
        return cli_options["pairs"] + cli_options["pairs_from_file"]

    def validate_experiments(self, targets, references):
        #self.validate_dna_pairs(targets, references)
        self.validate_same_technique(targets, references)

    def validate_settings(self, settings):
        self.validate_reference_genome(settings.reference)

    def get_command(self, analysis, inputs, settings):
        target = analysis.targets[0]
        reference = analysis.references[0]
        command = [
            settings.svab,
            "run",
            "-z",
            "-a",
            target.system_id,
            "-G",
            settings.reference,
            "-t",
            self.get_bam(target),
            "-n",
            self.get_bam(reference),
            "-p",
            settings.cores,
        ]
        com = (" ".join(command))
        return com


    def get_analysis_results(self, analysis):
        results = {
            "svs": join(
                analysis["storage_url"],
                analysis["targets"][0]["system_id"] + ".svaba.somatic.sv.vcf.gz",
            )
        }
        for i in results.values():
            assert isfile(i)

        return results

class SvabaGRCh37(Svaba):

    ASSEMBLY = "GRCh37"
    SPECIES = "HUMAN"


class SvabaGRCm38(Svaba):

    ASSEMBLY = "GRCh38"
    SPECIES = "HUMAN"