import os
from os.path import isfile
from os.path import join

from isabl_cli import AbstractApplication
from isabl_cli import options
from myapps import constants

from myapps.utils import get_docker_command


class Gridss(AbstractApplication):

    NAME = "GRIDSS"
    VERSION = "2.2.2"
    #ASSEMBLY = "GRCh38"
    ASSEMBLY = "hg19"

    SPECIES = "HUMAN"
    cli_help = "Find structural variants with GRIDSS."
    cli_options = [options.PAIRS, options.PAIRS_FROM_FILE]
    application_description = cli_help

    application_results = {
        "svs": {
            "frontend_type": "tsv-file",
            "description": "GRIDSS somatic SVS VCF.",
            "verbose_name": "Somatic SVS VCF",
            "external_link": None,
        },
        "assembly_bam": {
            "frontend_type": "igv_bam:assembly_bam_bai",
            "description": "Gridss Assembled Bam",
            "verbose_name": "Assembly Bam",
            "external_link": None,
        },
        "assembly_bam_bai": {
            "frontend_type": None,
            "description": "Gridss Assembled Bam Index",
            "verbose_name": "Assembly Bam Index",
            "external_link": None,
        },
    }
    application_settings = {
        "config": "/mnt/efs/myisabl/config.txt",
        "blacklist": "/mnt/efs/myisabl/wgEncodeDacMapabilityConsensusExcludable.bed",        
        "gridss": get_docker_command("papaemmelab/docker-gridss"),
        "reference": "reference_data_id:genome_fasta",
        "cores": "1",
    }


    def get_experiments_from_cli_options(self, **cli_options):
        return cli_options["pairs"] + cli_options["pairs_from_file"]

    def validate_experiments(self, targets, references):
        self.validate_bams(targets + references)
        self.validate_dna_pairs(targets, references)
        self.validate_same_technique(targets, references)
        #self.validate_methods(targets + references, ["WG"])

    def validate_settings(self, settings):
        self.validate_reference_genome(settings.reference)

    def get_command(self, analysis, inputs, settings):
        outdir = analysis.storage_url
        tumor = analysis.targets[0]
        normal = analysis.references[0]
        #x="/home/danielavt/cli2/myapps/myapps/apps/gridss/config.txt"
        return (
            f"cd {outdir} && "
            f"{settings.gridss} "
            f"CONFIGURATION_FILE={settings.config} "
            f"WORKING_DIR={outdir} "
            f"REFERENCE_SEQUENCE={settings.reference} "
            f"INPUT={self.get_bam(normal)} "
            f"INPUT_LABEL={normal.system_id} "
            f"INPUT={self.get_bam(tumor)} "
            f"INPUT_LABEL={tumor.system_id} "
            f"OUTPUT={join(outdir, 'somatic.sv.vcf')} "
            f"ASSEMBLY={join(outdir, 'somatic.gridss.assembly.bam')} "
            f"BLACKLIST={settings.blacklist} "
            f"WORKER_THREADS={settings.cores} "
            f"&& sudo chown -R ec2-user {outdir}"
            f"&& rm -rf {join(outdir, f'{normal.system_id}.bam.gridss.working')} "
            f"&& rm -rf {join(outdir, f'{tumor.system_id}.bam.gridss.working')}"
        )

    def get_analysis_results(self, analysis):
        results = {
            "svs": join(analysis.storage_url, "somatic.sv.vcf"),
            "assembly_bam": join(analysis.storage_url, "somatic.gridss.assembly.bam"),
            "assembly_bam_bai": join(
                analysis.storage_url, "somatic.gridss.assembly.bai"
            ),
        }

        for i in results.values():
            assert isfile(i), f"Missing result file {i}"

        return results

class GridssGRCh37(Gridss):

    ASSEMBLY = "GRCh37"
    SPECIES = "HUMAN"


class GridssGRCm38(Gridss):

    ASSEMBLY = "GRCh38"
    SPECIES = "HUMAN"