file_path = '/Users/langm27/Downloads/photos_test/01 - AqME - Hérésie.mp3'

import eyed3

audiofile = eyed3.load(file_path)

audiofile.tag.artist = "Token Entry"
audiofile.tag.album = "Free For All Comp LP"
audiofile.tag.album_artist = "Various Artists"
audiofile.tag.title = "The Edge"
audiofile.tag.track_num = 3

# audiofile.tag.save()
