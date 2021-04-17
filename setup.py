from setuptools import setup, find_packages
import jp_dict

packages = find_packages(
        where='.',
        include=['jp_dict*']
)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyclay-jp_dict',
    version=jp_dict.__version__,
    description='Utilities used for parsing jisho and kotobank definitions from browser history.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cm107/jp_dict",
    author='Clayton Mork',
    author_email='mork.clayton3@gmail.com',
    license='MIT License',
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pylint==2.4.4',
        'beautifulsoup4>=4.8.0',
        'pandas',
        'lxml',
        'tzlocal',
        'seaborn',
        'pyclay-common_utils @ https://github.com/cm107/common_utils/archive/master.zip',
        'pyclay-logger @ https://github.com/cm107/logger/archive/master.zip'
    ],
    python_requires='>=3.7'
)