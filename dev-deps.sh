#/bin/bash
# This is a workflow helper script to extract dependencies-only from pyprojects.toml and install them.
# We don't want to build, package and install current project to site-packages for causing namespace conflicts.
python -m piptools compile -o requirements-dev.txt pyproject.toml
pip install -r requirements-dev.txt
rm requirements-dev.txt
