from setuptools import setup

setup(
    name="pywu",
    version="1.1",
    author="Dan Hasting",
    author_email="dan@hasting.info",
    url="https://github.com/dh4/pywu",
    license="BSD",
    description="A simple python script for fetching data from Weather Underground's API.",
    long_description=open("README.rst").read(),
    packages=["pywu"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: POSIX",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],

    entry_points={
        'console_scripts': [
            'pywu = pywu.pywu:main'
        ]
    },
)
