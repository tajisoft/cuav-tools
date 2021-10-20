#encoding:utf-8

import os
import sys
from pprint import pprint

import piexif
from PIL import Image
from fractions import Fraction
import pyexiv2

targetDir = sys.argv[1]
print('target dir %s' % targetDir)

if not os.path.exists(targetDir):
    print('Not found %s' % targetDir)
    sys.exit()

def to_deg(value, loc):                                                                                                                                               
    if value < 0:                                                                                                                                                    
       loc_value = loc[0]                                                                                                                                       
    elif value > 0:                                                                                                                                                  
       loc_value = loc[1]
    else:                                                                                                                                                            
       loc_value = ""                                                                                                                                           
    abs_value = abs(value)
    deg =  int(abs_value)                                                                                                                                        
    t1 = (abs_value-deg)*60                                                                                                                                      
    minu = int(t1)                                                                                                                                                
    sec = round((t1 - minu)* 60, 5)
    return (deg, minu, sec, loc_value) 

def change_to_rational(number):
    f = Fraction(str(number))                                                                                                                                    
    return (f.numerator, f.denominator)    

def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)

lat, lng = 35.0000000, 139.0000000
lat_deg = to_deg(lat, ['S', 'N'])
lng_deg = to_deg(lng, ['W', 'E'])
exif_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
exif_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))
for f in find_all_files(targetDir):
    if 'jpg' in f:
        img = Image.open(f)
        exif_dict = piexif.load(img.info['exif'])
        gps_info = exif_dict['GPS']
        pprint(exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal])
        
        # m = pyexiv2.ImageMetadata(f)
        # m.read()
        # print(m.exif_keys)
        # print(m['Exif.Photo.DateTimeOriginal'].value.timetuple())
        
        exif_dict[piexif.ImageIFD.DateTime] = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
        pprint(exif_dict.keys())
        if len(gps_info) > 0:
            continue
        else:
            print('Fix %s' % f)
            gps_info[piexif.GPSIFD.GPSLatitudeRef] = 'N'
            gps_info[piexif.GPSIFD.GPSLatitude] = ((43, 1), (17414, 1000), (0, 1))
            gps_info[piexif.GPSIFD.GPSLongitudeRef] = 'E'
            gps_info[piexif.GPSIFD.GPSLongitude] = ((143, 1), (14211, 1000), (0, 1))
            gps_info[piexif.GPSIFD.GPSAltitude] = (572, 1)
            gps_info[piexif.GPSIFD.GPSVersionID] = (2, 0, 0, 0)
            gps_info[18] = 'WGS84'
            exif_bytes = piexif.dump(exif_dict)
            img.save(f, exif=exif_bytes)
