from setuptools import setup, find_packages

setup(
    name="mkdocs-user-defined-values",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": [
            "user-defined-values = mkdocs_user_defined_values.plugin:UserDefinedValues"
        ]
    },
    install_requires=["mkdocs>=1.4"],
)