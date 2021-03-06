from os.path import isfile
from os.path import join

from isabl_cli import AbstractApplication
from isabl_cli import options

from myapps.utils import get_docker_command

class Delly(AbstractApplication):

    NAME = "DELLY"
    VERSION = "2"
    ASSEMBLY = "hg19_2"

    #ASSEMBLY = "GRCh38"
    SPECIES = "HUMAN"
    cli_help = "Find structural variants with GRIDSS."
    cli_options = [options.PAIRS, options.PAIRS_FROM_FILE]
    application_description = cli_help

    application_results = {
        "svs": {
            "frontend_type": "tsv-file",
            "description": "DELLY somatic SVS VCF.",
            "verbose_name": "Somatic SVS VCF",
            "external_link": None,
        }
    }
    application_settings = {
        "delly": get_docker_command("dellytools/delly"),
        "bcftools": get_docker_command("dceoy/bcftools"),
        "reference": "reference_data_id:genome_fasta",
        "cores": "2",
    }


    def get_experiments_from_cli_options(self, **cli_options):
        return cli_options["pairs"] + cli_options["pairs_from_file"]

    def validate_experiments(self, targets, references):
        self.validate_bams(targets + references)
        self.validate_same_technique(targets, references)

    def validate_settings(self, settings):
        self.validate_reference_genome(settings.reference)

    def get_command(self, analysis, inputs, settings):
        outdir = join(analysis.storage_url, "delly.bcf")
        outdirvcf = join(analysis.storage_url, "delly.vcf")

        target = analysis.targets[0]
        reference = analysis.references[0]
        command = [
            settings.delly,
            "delly",
            "call",
            "-o",
            outdir,
            "-g",
            settings.reference,
            self.get_bam(reference),
            self.get_bam(target),
        ]
        command2 = [
            settings.bcftools,
            "view",
            outdir,
            ">",
            outdirvcf,            
        ]
        com = (" ".join(command))
        cmd2 = (" ".join(command2))
        return (com + f" && sudo touch {outdirvcf}" + f" && sudo chown -R ec2-user {outdirvcf}"
        + f" && {cmd2}")

    def get_analysis_results(self, analysis):
        results = {
            "svs": join(analysis.storage_url, "delly.vcf"),
        }

        for i in results.values():
            assert isfile(i), f"Missing result file {i}"
        return results
        
class DellyGRCh37(Delly):

    ASSEMBLY = "GRCh37"
    SPECIES = "HUMAN"


class DellyGRCm38(Delly):

    ASSEMBLY = "GRCh38"
    SPECIES = "HUMAN"
