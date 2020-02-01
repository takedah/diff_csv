from setuptools import setup


setup(
    name="diff_csv",
    version="0.0.2",
    description="extract the difference between twoCSV files which have the same structure.",
    long_description=readme,
    author="Hiroki Takeda",
    author_email="takedahiroki@gmail.com",
    url="https://github.com/takedah/diff_csv",
    license="MIT",
    install_requires=["pandas", "numpy"],
    packages=find_packages(exclude=["tests"]),
)
