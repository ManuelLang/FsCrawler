#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import os
import subprocess
from pathlib import Path

from loguru import logger
from thumbnail import generate_thumbnail

from crawler.events.fileCrawledEventArgs import FileCrawledEventArgs
from interfaces.iPathProcessor import IPathProcessor
from models.path import PathModel
from models.path_type import PathType


class PreviewFileProcessor(IPathProcessor):

    def __init__(self, out_thumb_directory: Path) -> None:
        super().__init__()
        if not out_thumb_directory or not out_thumb_directory.is_dir():
            raise ValueError(f"The given path is not a valid directory: '{out_thumb_directory}'")
        self.out_thumb_directory = out_thumb_directory
        self.thumbs_width = 800
        self.thumb_cover_name = ''
        self.thumb_cover_suffix = '_Folder'
        self.thumb_cover_offset = 25
        self.nb_additional_frames = 10


    @property
    def processor_type(self) -> PathType:
        return PathType.FILE

    def process_path(self, crawl_event: FileCrawledEventArgs, path_model: PathModel):
        logger.debug(f"Computing file's thumbnail: {path_model}")
        options = {
            'trim': False,
            'height': self.thumbs_width,
            'width': self.thumbs_width,
            'quality': 85,
            'type': 'thumbnail'
        }
        try:
            output_file_path_cover = os.path.join(self.out_thumb_directory, f"{self.thumb_cover_name if self.thumb_cover_name else path_model.name}{self.thumb_cover_suffix}.png")
            command = subprocess.Popen(f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{path_model.full_path}\"",
                shell=True, stdout=subprocess.PIPE).stdout
            duration = command.read().decode()
            print(duration)

            # Cover image
            os.system(f"ffmpeg -y -ss {self.thumb_cover_offset} -i \"{path_model.full_path}\" -vf \"scale={self.thumbs_width}:-1\" \"{output_file_path_cover}\"")
            if self.nb_additional_frames > 0:
                # Evenly spaced thumbnails
                output_file_path_frames = os.path.join(self.out_thumb_directory, f"{path_model.name}_%03d.png")
                os.system(f"ffmpeg -i \"{path_model.full_path}\" -vf \"fps={self.nb_additional_frames}/{duration},scale={self.thumbs_width}:-1\" \"{output_file_path_frames}\"")

            # thumb_output_path = os.path.join(self.out_thumb_directory, f"{path_model.hash_md5}.png")
            # generate_thumbnail(crawl_event.path, thumb_output_path, options)
        except Exception as ex:
            logger.error(f"Unable to generate thumbnail from file '{path_model.full_path}': {ex}")
            raise ex


if __name__ == '__main__':
    inputs = [
        '/mnt/sda1/Test/I/.flv',
        '/mnt/sda1/Test/J/.mp4',
    ]
    i = 0
    pfp = PreviewFileProcessor(out_thumb_directory=Path('/home/sa-nas/Musique/test/'))
    for f in inputs:
        if not f:
            continue
        i += 1
        pfp.process_path(None, PathModel(root='/mnt/sda1/Test', path=f))

    # generate_thumbnail(input=input, output=output, options=options)
    print("Done!")

