from os.path import isfile, dirname, join, realpath

from cached_property import cached_property
from isabl_cli import AbstractApplication
from isabl_cli import options


from myapps.apps.delly.apps import Delly
from myapps.apps.gridss.apps import Gridss


class Filter(AbstractApplication):

    NAME = "FILTER"
    VERSION = "0.1"
    ASSEMBLY = "hg19_2"

    SPECIES = "HUMAN"
    cli_help = "Filtering output of gridss and delly."
    cli_options = [options.PAIRS, options.PAIRS_FROM_FILE]
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
        "filter": join(dir_path, "filtering.py"),
        "cores": "1",
    }

    @cached_property
    def _apps(self):
        return {
            "delly": Delly(),
            "gridss": Gridss(),
        }

    @cached_property
    def analyses_dependencies(self):
        return [
            {"app": self._apps["gridss"], "result": "svs", "name": "gridss_vcf"},
            {"app": self._apps["delly"], "result": "svs", "name": "delly_vcf"},
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
        return cli_options["pairs"] + cli_options["pairs_from_file"]

    def get_command(self, analysis, inputs, settings):
        outdir = analysis.storage_url
        outdir1 = join(outdir, "filt1.vcf")
        outdir2 = join(outdir, "filt2.vcf")

        return " ".join(
            map(
                str,
                [
                    settings.filter,
                    "-vcf1",
                    inputs["gridss_vcf"],
                    "-vcf1",
                    "gridss",
                    inputs["delly_vcf"],
                    "-o1",
                    outdir1,
                    "-o2",
                    outdir2,                    
                ],
            )
        )

    def get_analysis_results(self, analysis):
        results = {
            "svs": join(analysis.storage_url, "delly.bcf"),
        }

        for i in results.values():
            assert isfile(i), f"Missing result file {i}"
        return results