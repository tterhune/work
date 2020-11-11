import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = [
    'requests',
    'urllib3',
    'colorama']
setuptools.setup(
    name="afc_tools",
    version="0.0.4",
    author="Tim Terhune",
    author_email="tim.terhune@hpe.com",
    description="AFC Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=['afc_tools/bin/display-switches',
             'afc_tools/bin/display-macs',
             'afc_tools/bin/display-neighbors',
             'afc_tools/bin/display-policies',
             'afc_tools/bin/setup-fabric',
             'afc_tools/bin/cleanup-afc-policies',
             'afc_tools/bin/display-peers'],
    url="https://github.com/tterhune/work",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
