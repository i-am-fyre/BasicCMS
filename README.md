# Basic CMS for MaNGOS Projects

A very simple CMS page for MaNGOS projects. The purpose of this project is to provide a registration page to link to the realmd database and create new accounts.

## Features

- Register accounts
- Player login
- Administrator login
- Change password
- View character summaries

## Getting Started

These instructions will give you a copy of the project up and running on
your local machine. Tested on Ubuntu 20.04 WSL.

### Prerequisites

Run the following:
- `sudo apt-get install libmariadb-dev python3-dev python3-flask python3-pip`
- `sudo git clone https://github.com/i-am-fyre/BasicCMS`
- `cd BasicCMS`
- `pip install -r requirements.txt`

### Configuration

You can set your database information in `config.ini`.
You can select which expansions of MaNGOS the user can register for within the `register.html`.

### Starting Up

Once the pre-requisites above have been installed and configurations are set, do the following:
- `export FLASK_APP=main.py`
- `flask run --port=4830 --host=0.0.0.0`
  
Your local server should then be running at http://localhost:4830
- **Note:** Change "localhost" to the IP of your machine hosting the app.


## Screenshots
![MangosRegister](https://user-images.githubusercontent.com/58180427/162591117-71d84e9b-f769-4d8d-a5a3-457ef0180c80.png)
![MangosChangePW](https://user-images.githubusercontent.com/58180427/162652190-31ccf1b1-2261-49a3-a6c3-1673d9eb1ebf.png)
![MangosCharacters](https://user-images.githubusercontent.com/58180427/163526589-fa30c3ad-806a-411c-b854-00d84391df31.png)
