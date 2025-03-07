from setuptools import setup, find_packages

setup(
    name='CVXlab',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'cvxpy',
        'openpyxl',
        'pytest',
    ],
    author='Matteo V. Rocco',
    author_email='matteovincenzo.rocco@polimi.it',
    description='...',
    url='https://github.com/pyESM-project/pyesm',
)
