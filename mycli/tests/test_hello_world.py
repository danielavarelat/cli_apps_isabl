from os.path import join

from click.testing import CliRunner
from isabl_cli.test import utils
from isabl_cli import api
from isabl_cli import factories

from mycli.apps import HelloWorldApp


def test_hello_world_app(tmpdir, datadir, commit):
    # path to hello_world test data
    hello_world_datadir = join(datadir, "hello_world")
    raw_data = [
        dict(
            file_url=join(hello_world_datadir, "test.txt"),
            file_data=dict(extra="annotations"),
            file_type="FASTQ_R1",
        ),
    ]

    # create dummy experiment
    meta_data = factories.ExperimentFactory(raw_data=raw_data)
    meta_data["sample"]["individual"]["species"] = "HUMAN"
    meta_data["storage_url"] = hello_world_datadir
    meta_data.pop("identifier", None)
    experiment_a = api.create_instance("experiments", identifier="a", **meta_data)
    meta_data["projects"] = experiment_a.projects
    experiment_b = api.create_instance("experiments", identifier="b", **meta_data)

    # overwrite default configuration for the default client
    app = HelloWorldApp()
    app.application.settings.default_client = {
        "default_message": "Hello from Elephant Island.",
        "echo_path": tmpdir.docker("ubuntu", "echo")
    }

    # run application and make sure results are reported
    analyses = utils.assert_run(
        application=app,
        tuples=[([experiment_a], []), ([experiment_b], [])],
        commit=commit,
        results=["output", "count", "input"],
    )

    if commit:
        # assert individual level merge worked
        total_count = sum(i.results.count for i in analyses)
        individual_level_analyses = api.get_analyses(
            application__pk=app.individual_level_auto_merge_application.pk,
            individual_level_analysis=experiment_a.sample.individual.pk
        )

        assert len(individual_level_analyses) == 1
        assert individual_level_analyses[0].results.count == total_count

        # assert project level merged worked
        project_level_analyses = api.get_analyses(
            application__pk=app.project_level_auto_merge_application.pk,
            project_level_analysis=experiment_a.projects[0].pk
        )

        assert len(project_level_analyses) == 1
        assert project_level_analyses[0].results.count == total_count

        # assert we can rerun from command line given protect_results = False
        runner = CliRunner()
        params = [
            "--commit",
            "--message",
            "Hello, Im Shackleton",
            "-fi", "sample.individual", experiment_a.sample.individual.pk
        ]

        result = runner.invoke(app.as_cli_command(), params)
        assert "SUCCEEDED" in result.output
        assert "Submitting individual merge" in result.output
