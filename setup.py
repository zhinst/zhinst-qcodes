# Copyright (C) 2020 Zurich Instruments
#
# This software may be modified and distributed under the terms
# of the MIT license. See the LICENSE file for details.


import os
import setuptools


requirements = [
    "numpy>=1.13",
    "setuptools>=40.1.0",
    "zhinst>=21.8",
    "zhinst-toolkit>=0.2.0",
    "qcodes>=0.14.0",
    "attrs",
]


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zhinst-qcodes",
    description="Zurich Instruents drivers for QCoDeS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhinst/zhinst-qcodes",
    author="Zurich Instruments",
    author_email="info@zhinst.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
    ],
    keywords="zhinst sdk quantum qcodes",
    packages=setuptools.find_namespace_packages(
        where="src", exclude=["test*"], include=["zhinst.*"]
    ),
    package_dir={"": "src"},
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.6",
    zip_safe=False,
)
