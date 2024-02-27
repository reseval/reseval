from pathlib import Path
from setuptools import find_packages, setup


def long_description():
    """Generate description to post on PyPi"""
    with open('README.md', encoding='utf8') as file:
        return file.read()


def package_data():
    """Get the non-python files that should be included in release"""
    module_directory = Path(__file__).parent / 'reseval'
    assets_directory = module_directory / 'assets'

    # Package data should be paths relative to package
    return {'reseval': [
        str(path.relative_to(module_directory))
        for path in assets_directory.rglob('*')]}


# Setup
setup(
    name='reseval',
    description='Reproducible Subjective Evaluation',
    version='0.1.6',
    author='Max Morrison, Brian Tang, Gefei Tan, Bryan Pardo',
    author_email='maxrmorrison@gmail.com',
    url='https://github.com/reseval/reseval',
    install_requires=[
        'appdirs>=1.4.4',
        'boto3>=1.21.3',
        'matplotlib>=3.5.2',
        'mysql-connector-python>=8.0.28',
        'psutil>=5.9.0',
        'python-dotenv>=0.19.2',
        'pyyaml>=6.0',
        'rich>=11.2.0',
        'scipy>=1.8.0',
        'xmltodict>=0.12.0',
        'heroku3>=5.1.4'],
    packages=find_packages(),
    package_data=package_data(),
    long_description=long_description(),
    long_description_content_type='text/markdown',
    keywords=[
        'annotation',
        'audio',
        'ab',
        'abx',
        'crowdsourcing',
        'evaluation',
        'image',
        'mos',
        'mushra',
        'speech',
        'subjective'])
