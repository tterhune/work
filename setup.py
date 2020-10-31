import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = [
    'requests',
    'urllib3',
]

setuptools.setup(
    name="afc_test",
    version="0.0.1",
    author="Tim Terhune",
    author_email="tim.terhune@hpe.com",
    description="AFC test scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tterhune/work",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
