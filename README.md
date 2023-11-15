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
sudo mkdir -p /var/lib/mysql/
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

## Architecture

[TODO]

## TODO

* Add path roots to params and use this as a root. Remove it from the path, for taking into account path string which
  is *after* the root part
* Parametize paths to be crawled (with click)
* Filters in config file
* docker file to run as a container
