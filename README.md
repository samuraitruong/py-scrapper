# py-scrapper
A python application to scrap &amp; clone static website


## Get started
### Install dependencies

You need install python3 to run this script

```
pip3 install -r requirements.txt
```

### Run 

Example command

```
python3 app/main.py --url https://chungta.vn --output www --resource-threads=50 --threads=50 --force=true --download_resources=False

```
This will crawl https://chungta.vn and write output into www folder.

#### Commandline Args
```

usage: main.py [-h] [--url URL] [--output OUTPUT] [--threads THREADS]
               [--resource-threads RESOURCE_THREADS] [--force FORCE]
               [--download_resources DOWNLOAD_RESOURCES]

Website scrapper info.

optional arguments:
  -h, --help            show this help message and exit
  --url URL             Url of website
  --output OUTPUT       Output folder
  --threads THREADS     Number of threads to run to fetch html page in
                        concurences
  --resource-threads RESOURCE_THREADS
                        Number of threads to run to fetch resources just as
                        image, video
  --force FORCE         Remove history and download everything again
  --download_resources DOWNLOAD_RESOURCES
                        Download images, js, css, and other files

 ```



### WIP
- Restore session from database to duplication 
- 
