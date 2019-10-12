from os.path import isfile, dirname, join, realpath

from cached_property import cached_property
from isabl_cli import AbstractApplication
from isabl_cli import options

from myapps.utils import get_docker_command
from myapps.apps.filtering.apps import Filter


class Merge(AbstractApplication):

    NAME = "MERGE"
    VERSION = "0.1"
    ASSEMBLY = "hg19_2"

    SPECIES = "HUMAN"
    cli_help = "Merging output of filtering."
    cli_options = [options.TARGETS]

    application_description = cli_help

    application_results = {
        "svs": {
            "frontend_type": "tsv-file",
            "description": "SVS VCF.",
            "verbose_name": "Somatic SVS VCF",
            "external_link": None,
        }
    }
    dir_path = dirname(realpath(__file__))
    application_settings = {
        "survivor": "cd /home/ec2-user/SURVIVOR/Debug &&",
        "cores": "1",
    }

    @cached_property
    def _apps(self):
        return {
            "filtering": Filter(),
        }

    @cached_property
    def analyses_dependencies(self):
        return [
            {"app": self._apps["filtering"], "result": "svs", "name": "filt1"},
            {"app": self._apps["filtering"], "result": "svs2", "name": "filt2"},
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
        outdirmerge = join(outdir, "merged.vcf")
        in1 = inputs["filt1"]
        in2 = inputs["filt2"]
        vcfs_paths = join(outdir,"vcfs_paths")
        f= open(vcfs_paths,"w+")
        f.write(in1)
        f.write("\n")
        f.write(in2)
        f.close()

        return " ".join(
            map(
                str,
                [
                    settings.survivor,
                    "./SURVIVOR merge",
                    vcfs_paths,
                    "100",
                    "2",
                    "1",
                    "1",
                    "0",
                    "30",
                    "-out2",
                    outdirmerge,  
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