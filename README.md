# zenodo-batch-uploader
Wrap Zenodo Uploader https://github.com/NCAR/data-tools/zenodo_create.py

# Quickstart
You need Docker.

You need a Zenodo sandbox token.

Clone this repo.  
Clone https://github.com/NCAR/data-tools  
Copy files from this repo into data-tools (location of zenodo_create.py)  
Populate dataset_shortnames.txt file with the names of datasets you want to upload.  
Create a `.env` file like this:

DOWNLOADS_PATH=<path to downloads directory, probably creataed by the dataset-downloader>
ZENODO_TOKEN=<Zenodo Sandbox Token>* 

* If you want to use production token, the batch_upload.py code has to be tweaked to remove the --test args in "run_upload".
  
Run: 
docker compose build
docker compose up
