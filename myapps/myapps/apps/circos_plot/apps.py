from os.path import isfile, join

from cached_property import cached_property
from isabl_cli import AbstractApplication
from isabl_cli import options

from myapps.utils import get_docker_command
from myapps.apps.merge.apps import Merge


class Circos(AbstractApplication):

    NAME = "CIRCOS"
    VERSION = "0.1"
    ASSEMBLY = "hg19_2"

    SPECIES = "HUMAN"
    cli_help = "Circos plot."
    cli_options = [options.TARGETS]

    application_description = cli_help

    application_results = {
        "circos_png": {
            "frontend_type": "image",
            "description": "Circos image.",
            "verbose_name": "Circos image",
            "external_link": None,
        }
    }
    application_settings = {
        "docker_pysam": "docker run -it --entrypoint '' -v /mnt/efs/myisabl:/mnt/efs/myisabl danielrbroad/pysamdocker /bin/bash ",
        "make_circos": "/mnt/efs/myisabl/circos/make_circos.r",
        "circos_prep": "python /mnt/efs/myisabl/circos/circos_prep.py",
        "cores": "1",
        "docker_circos": get_docker_command("danielavarelat/circosr"),
        "docker_py": get_docker_command("danielrbroad/pysamdocker"),
        "bed": "/mnt/efs/myisabl/circos/circos_genes.bed",
        "cns": "/mnt/efs/myisabl/circos/empty.cns",
    }

    @cached_property
    def _apps(self):
        return {
            "merge": Merge(),
        }

    @cached_property
    def analyses_dependencies(self):
        return [
            {"app": self._apps["merge"], "result": "svs", "name": "merge"},
        ]

    def get_dependencies(self, targets, references, settings):
        inputs = {}
        analyses = []
        for dependency in self.analyses_dependencies:
            input_name = dependency["name"]
            inputs[input_name], key = self.get_result(
                targets[0],
                application_key=dependency["app"].primary_key,
                application_name=dependency["app"].NAME,
                result_key=dependency["result"],
                targets=targets,
                references=references,
            )
            analyses.append(key)
        return analyses, inputs

    def get_experiments_from_cli_options(self, **cli_options):
        return [([i], []) for i in cli_options["targets"]]

    def validate_experiments(self, targets, references):
        self.validate_one_target_no_references(targets, references)
        
    def command_prep(self, analysis, inputs, settings):
        inp = inputs["merge"]
        outdir = analysis.storage_url
        return " ".join(
            map(
                str,
                [
                    settings.docker_py,
                    settings.circos_prep,
                    "-cns",
                    settings.cns,
                    "-vcf",
                    inp,
                    "-o",
                    outdir,
                    " && ",               
                ],
            )
        )

    def get_command(self, analysis, inputs, settings):
        cmd = self.command_prep(analysis, inputs, settings)
        outdir = analysis.storage_url
        outcircos = join(outdir, "circos.png")
        circostsv = join(outdir, "circos_svs.tsv")
        circossegs = join(outdir, "segs.csv ")
        return " ".join(
            map(
                str,
                [
                    cmd,
                    settings.make_circos,
                    circostsv,
                    settings.bed,
                    circossegs,
                    outcircos,
                    "&& sudo chown -R ec2-user {}".format(outdir),               
                ],
            )
        )

    def get_analysis_results(self, analysis):
        results = {
            "svs": join(analysis.storage_url, "merged.vcf"),
        }

        for i in results.values():
            assert isfile(i), f"Missing result file {i}"
        return results
