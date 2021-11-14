import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pydano",
    version="0.0.6",
    author="Gaurav Arora",
    description="Library to interact with cardano network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',                
    package_dir={'':'pydano'},
    packages=setuptools.find_packages(exclude=['scripts'], include=['pydano', 'pydano.query', 'pydano.transaction', 'pydano.blockfrost'], where='pydano'),
    entry_points = {
        'console_scripts': ['pydano-cli=pydano.pydano_cli:main'],
    },
    install_requires=['blockfrost-python==0.3.1']
)
