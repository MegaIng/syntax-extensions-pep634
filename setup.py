from setuptools import setup, find_packages, find_namespace_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='syntax_extensions_pep634',

    version='0.0.1',

    description='A pattern matching implementation ',

    url='https://github.com/MegaIng/syntax-extensions',

    author='MegaIng',
    author_email='trampchamp@hotmail.de',

    package_dir={'': 'src'},

    packages=find_namespace_packages(where='src'),  # Required

    python_requires='>=3.5, <4',  # TODO: to be decided
    install_requires=['syntax_extensions_base']
)
