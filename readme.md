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

## Simulations

The [Simulations](docs/source/simulations/index.rst) pages show interactive
simulations inline in the page. Each simulation is a static page from its own
GitHub repository. A copy of each repository is in `docs/source/_extra/demos/`,
as a squashed git subtree.

| Simulation | Directory in `docs/source/_extra/demos/` | Repository | Branch |
|---|---|---|---|
| High Availability | `scylladb-ha-demo` | [tzach/scylladb-ha-demo](https://github.com/tzach/scylladb-ha-demo) | `master` |
| Tablets | `scylladb-tablets-demo` | [tzach/scylladb-tablets-demo](https://github.com/tzach/scylladb-tablets-demo) | `main` |
| Compaction Strategies | `compaction-viz` | [tzach/compaction-viz](https://github.com/tzach/compaction-viz) | `main` |
| Incremental Repair | `repair-viz` | [tzach/repair-viz](https://github.com/tzach/repair-viz) | `main` |
| Materialized Views and Secondary Indexes | `scylladb-mv-viz` | [tzach/scylladb-mv-viz](https://github.com/tzach/scylladb-mv-viz) | `main` |

Do not edit the files in `docs/source/_extra/demos/`. Make the changes in the
simulation repository, then update the copy in this repository.

### Update a simulation

1. Pull the latest version of the simulation into this repository. For example,
   for the Incremental Repair simulation:

       git subtree pull --prefix=docs/source/_extra/demos/repair-viz \
           https://github.com/tzach/repair-viz main --squash

   Use the directory, repository, and branch from the table above.

2. Build the site and examine the simulation page:

       make -C docs preview

   You do not have to change the simulation page. The build reads the
   `index.html` file of the simulation each time.

3. If the simulation looks different, make a new screenshot for the
   Simulations list page. For example:

       cd docs/source
       google-chrome --headless=new --hide-scrollbars --window-size=1440,900 \
           --virtual-time-budget=6000 \
           --screenshot=$PWD/_static/img/simulations/repair-viz.png \
           file://$PWD/_extra/demos/repair-viz/index.html

   If the simulation starts a tour on the first visit, the tour covers the
   screenshot. To prevent this, make a temporary copy of `index.html` that sets
   the "tour seen" key in `localStorage`, and make the screenshot from the copy.

4. If the features of the simulation changed, update the description in
   `docs/source/simulations/<name>.rst`.

### Add a simulation

1. Add the repository as a subtree:

       git subtree add --prefix=docs/source/_extra/demos/<repo> \
           https://github.com/<owner>/<repo> <branch> --squash

2. Add the page `docs/source/simulations/<name>.rst`, with a description, the
   simulation, and a link to the repository:

       .. simulation:: <repo>

3. Add the page to the `toctree` and add a `simulation-card` in
   `docs/source/simulations/index.rst`.

4. Make a screenshot in `docs/source/_static/img/simulations/<repo>.png`.

### Requirements for a simulation repository

The `simulation` directive (`docs/ext/simulations.py`) puts the simulation in
the page, in a shadow DOM. The script `docs/source/_static/js/simulations.js`
runs it. For this to work, the simulation must obey these rules:

* It is one static `index.html` file, with no build step. It can use local
  stylesheets from `<head>`.
* All scripts are inline, in `<body>`. Scripts in `<head>` do not run, and
  `<script src="...">` is not loaded.
* It does not use inline event handlers, such as `onclick="..."`. Use
  `addEventListener`.
* It finds elements with `document.getElementById()`,
  `document.querySelector()`, or `document.querySelectorAll()`. It does not use
  `window.document`.
* The markup in `<body>` does not use relative URLs, such as
  `<img src="image.png">`.
* The docs theme sets the light or dark theme with `data-theme` on the root
  element. The simulation must not set its own theme when it starts.

The simulation also continues to work as a standalone page. The "Open full
screen" link on each simulation page opens the standalone page.
