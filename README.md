# Basic CMS for MaNGOS Projects

A very simple CMS page for MaNGOS projects. The purpose of this project is to provide a registration page to link to the realmd database and create new accounts.

## Getting Started

These instructions will give you a copy of the project up and running on
your local machine. Tested on Ubuntu 20.04 WSL.

### Prerequisites

Run the following:
- `sudo apt-get install libmariadb-dev python3-dev`
- `pip install -r requirements.txt`

### Installing

Once the pre-requisites above have been installed, do the following:
- `export FLASK_APP=main.py`
- `flask run`

Your local server should be running at http://localhost:5000
