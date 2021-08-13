# Pet notice and search service [![Build Status](https://app.travis-ci.com/PetMonitor/pet-notice-and-search-service.svg?branch=main)](https://app.travis-ci.com/PetMonitor/pet-notice-and-search-service)

Server that will provide the API endpoints to handle pet similarity searches, along with all the operations concerning the notices.

## Install dependencies required to run the project

The server contains a `requirements.txt` file in the root folder. That file declares all the dependencies that are used by the service. In order to install them, just run the following command:

`pip3 install -r requirements.txt`
   
## Run locally

  Set up a python virtualenv and install dependencies:
  
    > cd pet-notice-and-search-service
    > virtualenv venv
    > source venv/bin/activate
    > pip3 install -r requirements.txt

  Run the app:

    > export FLASK_APP=src.main.app.py
    > flask run
 
  The app should have started and be ready to receive requests at http://localhost:5000

## Run tests locally

   > pytest src/test -vv
