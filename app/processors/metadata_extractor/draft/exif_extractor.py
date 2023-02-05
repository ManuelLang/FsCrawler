img_path = '/Users/langm27/Downloads/photos_test/WP_20131006_005.jpg'

# https://medium.com/spatial-data-science/how-to-extract-gps-coordinates-from-images-in-python-e66e542af354
from exif import Image

with open(img_path, 'rb') as src:
    img = Image(src)
    print(src.name, img)
    print(img.list_all())

import PIL.Image

img = PIL.Image.open(img_path)
exif_data = img._getexif()

import PIL.ExifTags

exif_info = {
    PIL.ExifTags.TAGS[k]: v
    for k, v in img._getexif().items()
    if k in PIL.ExifTags.TAGS
}
print(exif_info)

# https://www.thepythoncode.com/article/extracting-image-metadata-in-python
# https://python3-exiv2.readthedocs.io/en/latest/tutorial.html
# https://auth0.com/blog/read-edit-exif-metadata-in-photos-with-python/
