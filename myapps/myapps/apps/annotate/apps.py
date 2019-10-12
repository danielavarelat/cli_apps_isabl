from os.path import isfile, dirname, join, realpath

from cached_property import cached_property
from isabl_cli import AbstractApplication
from isabl_cli import options

from myapps.utils import get_docker_command
from myapps.apps.merge.apps import Merge


class Annot(AbstractApplication):

    NAME = "ANOT"
    VERSION = "0.1"
    ASSEMBLY = "hg19_2"

    SPECIES = "HUMAN"
    cli_help = "Annotation with OncoKB."
    cli_options = [options.TARGETS]

    application_description = cli_help

    application_results = {
        "svs": {
            "frontend_type": "tsv-file",
            "description": "BED file with annotations.",
            "verbose_name": "Bed annotation",
            "external_link": None,
        }
    }
    dir_path = dirname(realpath(__file__))
    application_settings = {
        "svanno": "cd /mnt/efs/myisabl/svanno &&",
        "cores": "1",
        "docker_pysam": get_docker_command("danielrbroad/pysamdocker"),

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

    def get_command(self, analysis, inputs, settings):
        outdir = analysis.storage_url
        outbed = join(outdir, "annotation.bed")
        inp = inputs["merge"]
        return " ".join(
            map(
                str,
                [
                    settings.svanno,
                    settings.docker_pysam,
                    "python /mnt/efs/myisabl/svanno/svanno.py",
                    "-i",
                    inp,
                    "-o",
                    outbed,
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
