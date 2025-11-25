from setuptools import setup, find_packages

with open ("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="MLOps_user_survival_prediction",
    version="1.0.0",
    author="Zeygler",
    packages=find_packages(),
    install_requires=requirements,
)