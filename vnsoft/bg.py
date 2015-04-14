import Image, ImageChops
import sys

if len(sys.argv)!=2:
    print "Please Input img name."
    sys.exit(0)

img = Image.open(sys.argv[1])
if img.mode != 'RGBA':
    img = img.convert("RGBA")

datas = img.getdata()
newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save(sys.argv[1].split(".")[0]+".png", "PNG")