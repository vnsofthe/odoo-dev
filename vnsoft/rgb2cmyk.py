import Image, ImageChops
import sys

if len(sys.argv)!=2:
    print "Please Input img name."
    sys.exit(0)

img = Image.open(sys.argv[1])
if img.mode != 'RGB':
    print sys.argv[1]+" is not RGB."
    sys.exit(0)
    img = img.convert("RGB")

width,height = img.size
cmyk = Image.new("CMYK",(width,height),(0,0,0,255))

datas = img.getdata()
newData = []
for item in datas:
    
    if item[0]<130 and item[1]<130 and item[2]<130:
        newData.append((0,0,0,255))
        continue
    
    newData.append((0,0,0,0))
cmyk.putdata(newData)

cmyk.save(sys.argv[1].split(".")[0]+"_1.jpg")