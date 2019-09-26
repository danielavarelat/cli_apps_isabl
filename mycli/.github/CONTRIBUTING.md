# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given. This project could always use more documentation, whether as part of the README, in docstrings, or even on the web in blog posts articles, and such.

Submmit an [issue] if you found a bug or have a great idea for a new feature!

## Development

Follow these steps for local development:

1. Bet you've read the [Zen Of Python].

1. Clone your mycli locally:

        git clone git@github.com:isabl-io/mycli.git

1. Create a branch for local development:

        git pull
        git checkout -b name-of-your-bugfix-or-feature

    Now you can make your changes locally.

1. Create a test in:

        mycli/tests

1. Run [pytest] with [coverage], [pylint] and [pydocstyle] using Docker Compose:

        bash ./tests/test-with-compose.sh

    If you have a development Isabl API instance running, simply use [pytest]:

        py.test tests --cov=mycli

    To just check that your changes pass [pylint] and [pydocstyle] requirements:

        pylint --rcfile=.pylintrc mycli
        pydocstyle --config=.pydocstylerc mycli

1. Commit your changes and push your branch to GitHub (see our [`.gitmessage`] template):

        git add .
        git config commit.template .gitmessage
        git commit -m ":emoji-name: your short and nice description"
        git push origin name-of-your-bugfix-or-feature

    `emoji-name` should be one of the following:

    | emoji | name                 | type of change              |
    | ----- | -------------------- | --------------------------- |
    | 🚀    | `:rocket:`           | new feature                 |
    | 🐛    | `:bug:`              | bug fix                     |
    | 📝    | `:memo:`             | changes to documentation    |
    | 🎨    | `:art:`              | formatting  no code change  |
    | 🔧    | `:wrench:`           | refactoring production code |
    | ✅     | `:white_check_mark:` | adding/editing test logic   |
    | 👕    | `:shirt:`            | no production code change   |
    | 💎    | `:gem:`              | bump to new version         |

    If you are suggesting a new version make sure you are following the [semantic versioning] guidelines and then update the [`VERSION`] file:

        git add mycli/VERSION
        git commit -m ":gem: bump to version 0.1.0"

1. Submit a [pull request] through the GitHub website.

[`.gitmessage`]: ../.gitmessage
[`VERSION`]: ../isabl-io/VERSION
[coverage]:https://coverage.readthedocs.io
[pull request]: https://github.com/isabl-io/mycli/compare
[pulls]: https://github.com/isabl-io/mycli/pulls
[pydocstyle]: http://www.pydocstyle.org/en
[pylint]: https://www.pylint.org/
[pytest-env]: https://github.com/MobileDynasty/pytest-env
[pytest]: https://docs.pytest.org/en/latest/
[semantic versioning]: http://semver.org/
[zen of python]: https://www.python.org/dev/peps/pep-0020/#the-zen-of-python
