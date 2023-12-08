# Licence

Please note, that software is free for use, provided as is, under the `GNU Affero General Public License v3.0` (GNU
AGPLv3) licence. This enforces the following rules:
![AGPLv3 summary](./docs/GNU%20AGPLv3.png)

# FsCrawler

A File-System crawler written in Python, based on `pathlib` module: os-agnostic, this software will walk through all
files and directories from the given root path (for local files or network shares).

With powerful filtering system, it makes it easy to ignore some file types, name patterns, can limit the crawling depth
or the size of files to be crawled, etc... See the [filters package](./app/filters) for more details.

The crawler is implemented using event-driven architecture, events are raised along the process: crawlStarting,
crawlProgress, crawlError, pathFound, pathSkipped, crawlCompleted, etc... See the [events package](./app/crawler/events)
for more details.

Observers are notified about these events, in order to take action, or event stop the process based on some conditions.

A [QueueObserver](./app/observers/queue_observer.py) is provided to simply store the events for de-coupled processing.

[Path processors](./app/processors) can then take some actions on crawled files and directories, i.e. compute hash, get
MIME-type, extract text (for indexing using search engine for example), generate thumbnail, extract metadata (ie.e
ID3-tag for audio files, ITPC or EXIF for pictures).

These processors are invoked through a queue consumer.

## How to run it

### Prerequisites

#### Build virtual env

```bash
python3 -m venv venv
```

#### Install dependencies

First install libmagic and my-sql client on your machine. Example for mac:
```bash
brew install libmagic mysql-client pkg-config
export PKG_CONFIG_PATH="/opt/homebrew/opt/mysql-client/lib/pkgconfig"
```

For Linux:
```bash
sudo apt install -y mysql-client default-libmysqlclient-dev
# sudo apt install -y postgresql-client
```

Then:
```bash
source venv/bin/activate
pip3 install -r requirements.txt
```

#### Spin up database

```bash
sudo mkdir -p /media/sa-nas/docker_vol_db/maria_db/fs_crawler/
cd docker/
docker-compose up -d
``` 

Note: if you change DB password in docker-compose.yml, you need to trash the volume and start the container again, 
like [this](https://www.geekyhacker.com/how-to-resolve-mysql-access-denied-in-docker-compose/):
```bash
docker-compose down -v
```

#### Run it

```bash
PYTHONPATH=app python3 -m crawler_entry_point
```

#### All in one

```bash
source venv/bin/activate
cd docker
docker-compose up -d
PYTHONPATH=app python3 -m crawler_entry_point
```

#### Performance

##### Crawling

Log output:
```bash
Crawled path '<xyz>>' [1275998.22 Mb / 9149 files]
2023-11-22 22:36:23.840 | SUCCESS  | app.crawler.file_system_crawler:start:322 - Found 10171 paths (total of 1275998.22 Mb) in 0:01:34.295316 sec
	- 888 directories
	- 8725 files processed (total of 1191892.33 Mb)
```
That gives a bandwidth of 13.5 Gb/sec for finding files&dirs, apply all filters on them and raise events to the queue.

##### Processing

The longest operation here is to compute file hashes. That is done to check whether the content of a file has changed 
or not, and also to compare files (i.e. find duplicates).
```bash
Crawled 8725 files (total of 1246.09 Gb) in 1:42:42.769598 sec
```

That gives 1.246 Tb for 6163 sec, or 0.2 Gb/sec.

Running for the second time is much faster, as the crawler will check files that are already processed, to avoid 
process them again if the path and the size have not changed
```bash
Crawled 8725 files (total of 1246.09 Gb) in 0:00:39.391930 sec
```

## Architecture

[TODO]

## TODO

* Add path roots to params and use this as a root. Remove it from the path, for taking into account path string which
  is *after* the root part
* Parametize paths to be crawled (with click)
* Filters in config file
* docker file to run as a container
