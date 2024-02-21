from typing import List
from urllib.parse import quote

from database.data_manager import PathDataManager


class PlayListItem:
    def __init__(self, path: str = ''):
        super().__init__()
        self.path: str = path

    def __str__(self):
        location = (self.path.replace(' ', '%20')
                    .replace('#', '%23')
                    .replace('$', '%24')
                    .replace('&', '%26')
                    .replace('\'', '%27')
                    .replace('(', '%28*')
                    .replace(')', '%29*'))
        return (f"<track>"
                f"  <location>file://{location}</location>"
                f"</track>") if self.path else ''

class PlayList:
    def __init__(self, file_paths: List[PlayListItem] = []):
        super().__init__()
        self.file_paths= file_paths

    def __str__(self):
        res = """<?xml version="1.0" encoding="UTF-8"?>
<playlist xmlns="http://xspf.org/ns/0/" xmlns:vlc="http://www.videolan.org/vlc/playlist/ns/0/" version="1">
	<trackList>\n"""
        for item in self.file_paths:
            res += f"{item}\n"

        res += """	</trackList>
</playlist>"""
        return res


if __name__ == '__main__':
    data_manager: PathDataManager = PathDataManager()
    paths = data_manager.find_paths_by_prefix_and_name(
        path_prefix='/media/sa-nas/1ca37148-c9db-4660-b617-2d797356e44b1/Test/',
        name='++++', mime_type='video')
    pl = PlayList()
    for p in paths:
        pl.file_paths.append(PlayListItem(p.full_path))
    with open('out.xspf', 'w') as outfile:
        outfile.write(str(pl))
    print('Done!')
