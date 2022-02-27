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

    # # Directories within assets directory to include
    # directories = ['client/public', 'client/src', 'server']
    # directories = [Path(directory) for directory in directories]

    # # Loose files within assets directory to include
    # files = [
    #     'client/package-lock.json',
    #     'client/package.json',
    #     'client/Procfile',
    #     'client/static.json'
    #     'package-lock.json',
    #     'package.json',
    #     'Procfile',
    #     'server.ts',
    #     'tsconfig.json']
    # files = [Path(file) for file in files]

    # # Add all files in directories
    # for directory in directories:
    #     files.extend(
    #         file.relative_to(assets_directory)
    #         for file in (assets_directory / directory).rglob('*'))

    # # Add directories themselves
    # files.extend(directories)

    # # Non-recursively add client directory
    # files.append(Path('client'))

    # Package data should be paths relative to package
    return {'reseval': [str(path) for path in assets_directory.rglob('*')]}


# Setup
setup(
    name='reseval',
    description='Reproducible Subjective Evaluation',
    version='0.0.1',
    author='Max Morrison, Brian Tang, Gefei Tan, Bryan Pardo',
    author_email='maxrmorrison@gmail.com',
    url='https://github.com/reseval/reseval',
    install_requires=[
        'appdirs==1.4.4',
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
    long_description=long_description(),
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
