# developers.scylladb.com

This is the static site for [developers.scylladb.com](https://developers.scylladb.com). 
It is built using Sphinx and hosted on GitHub Pages.

## Prerequisites

To build the site, you need to have Python 3.10 installed. 
Recommended way to install Python is using [Homebrew](https://brew.sh/) with venv.

    brew install python@3.10
    python3.10 -m pip install --user --upgrade pip
    python3.10 -m pip install --user virtualenv
    python3.10 -m venv .venv
    source .venv/bin/activate

Install the required packages:

    pip install poetry

## Building the site

To build the site, you need to have Sphinx installed.

    make -C docs setup

## Running the site locally

To run the site locally, you need to have Sphinx installed.

    make -C docs preview

