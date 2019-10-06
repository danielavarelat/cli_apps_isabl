from os.path import isfile
from os.path import join

from isabl_cli import AbstractApplication
from isabl_cli import options

from myapps.utils import get_docker_command

class Merge(AbstractApplication):

    NAME = "MERGE"
    VERSION = "1"

    ASSEMBLY = "GRCh37"
    SPECIES = "HUMAN"
    cli_help = "Merge vcfs from different callers."
    cli_options = [options.PAIRS, options.PAIRS_FROM_FILE]
    application_description = cli_help

    application_results = {
        "svs": {
            "frontend_type": "tsv-file",
            "description": "MERGED somatic SVS VCF.",
            "verbose_name": "Somatic SVS VCF",
            "external_link": None,
        }
    }
    application_settings = {
        "merge": "mergesvvcf",
        "cores": "1",
    }

    def get_experiments_from_cli_options(self, **cli_options):
        return cli_options["pairs"] + cli_options["pairs_from_file"]

    # def validate_experiments(self, targets, references):
    #     self.validate_bams(targets + references)
    #     #self.validate_dna_pairs(targets, references)
    #     self.validate_same_technique(targets, references)
    #     #self.validate_methods(targets + references, ["WG"])

    # def validate_settings(self, settings):
    #     self.validate_reference_genome(settings.reference)

    def get_command(self, analysis, inputs, settings):
        outdir = join(analysis.storage_url, "merged.vcf")
        target = analysis.targets[0]
        command = [
            settings.merge,
            "vcf1",
            "vcf2",
            "-o",
            outdir,
            "-l",
            "name1,name2"
        ]
        com = (" ".join(command))
        return com

    def get_analysis_results(self, analysis):
        results = {
            "svs": join(analysis.storage_url, "merged.vcf"),
        }

        for i in results.values():
            assert isfile(i), f"Missing result file {i}"
        return results
