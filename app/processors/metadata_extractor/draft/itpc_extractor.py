# pip install pillow

from PIL import Image, IptcImagePlugin

im = Image.open('/Users/langm27/Downloads/photos_test/WP_20131006_005.jpg')
iptc = IptcImagePlugin.getiptcinfo(im)

if iptc:
    for k, v in iptc.items():
        print("{} {}".format(k, repr(v.decode())))
else:
    print(" This image has no iptc info")


# We can user getter function to get values
# from specific IIM codes
# https://iptc.org/std/photometadata/specification/IPTC-PhotoMetadata
def get_caption():
    return iptc.get((2, 120)).decode() if iptc else ''


print(get_caption())
