from pathlib import Path
from setuptools import find_packages, setup

# Description on pypi
with open('README.md', encoding='utf8') as file:
    long_description = file.read()


def package_data():
    """Get the non-python files that should be included in release"""
    module_directory = Path(__file__).parent / 'reseval'
    assets_directory = module_directory / 'assets'
    files = [
        str(file.relative_to(assets_directory))
        for file in assets_directory.rglob('*')]

    # Don't ship node_modules, survey template, or client build artifacts
    files = [
        file for file in files
        if file.parts[0] != 'node_modules' and
        file.parts[1] not in ['build', 'node_modules'] and
        file.stem not in ['assignments.json', 'config.json', 'survey.xml']]

    # Package data should be paths relative to package
    return {
        'reseval': [
            (module_directory / 'assets' / file).relative_to(module_directory)
            for file in files]}


# Setup
setup(
    name='reseval',
    description='Reproducible Subjective Evaluation',
    version='0.0.1',
    author='Interactive Audio Lab',
    author_email='interactiveaudiolab@gmail.com',
    url='https://github.com/interactiveaudiolab/reseval',
    install_requires=[
        'boto3==1.21.3',
        'mysql-connector-python==8.0.28',
        'psutil==5.9.0',
        'python-dotenv==0.19.2',
        'pyyaml==6.0',
        'rich==11.2.0',
        'scipy==1.8.0',
        'xmltodict==0.12.0',
        'heroku3==5.1.4'],
    packages=find_packages(),
    package_data=package_data(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=[
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
