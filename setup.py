from setuptools import setup, find_packages

setup(
    name='wikipediatrie',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click==6.6',
        'lz4==0.8.2',
        'colorama==0.3.7',
    ],
    entry_points='''
        [console_scripts]
        wikipediatrie=wikipediatrie.cli:cli
    ''',
)