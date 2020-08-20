import setuptools

with open("README.md", "r") as fh:
    l_description = fh.read()

setuptools.setup(
    name="Ulyxes PyAPI",
    version="1.0.0",
    author="Zoltan Siki",
    author_email="siki1958@gmail.com",
    description="Land surveyor's sensor driver library",
    long_description=l_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zsiki/ulyxes",
    packages=setuptools.find_packages(),
    install_requires=["pyserial"],
    classifiers=[
        "Environment :: Console"
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent"
    ],
)
