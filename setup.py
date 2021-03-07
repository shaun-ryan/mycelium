import pathlib
from setuptools import setup
from setuptools_databricks import DatabricksBuild
import os


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="mycelium",
    cmdclass={"build_databricks_project": BuildDatabricksProject},
    version_config={
        "template": "{tag}",
        "dev_template": "{tag}.dev{ccount}",
        "dirty_template": "{tag}.dev{ccount}.dirty",
        "starting_version": "0.0.1",
        "version_callback": None,
        "version_file": None,
        "count_commits_from_version_file": False
    },
    setup_requires=['setuptools-git-versioning'],
    description="Databricks Framework Utilities",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/semanticinsight/mycelium",
    author="Shaun Ryan",
    author_email="shaun_chiburi@hotmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["mycelium"],
    install_requires=[
          'PyYAML'
      ],
    zip_safe=False
)
