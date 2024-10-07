from fast_crawler import crawl
from index_files import process_files

def process():
    crawl()             # List all files on drive and store paths in DB
    process_files()     # Index files with post-processing (fetch from DB and extract metadata)

if __name__ == '__main__':
    process()