from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime


from db_declaration import ImageInfo,Person, PersonOnImage, Faces, Base
import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS



class FileTreeReader:
    def __init__(self):
        engine = create_engine('sqlite:///photos.db', echo=True)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

        self.fileList = []
        self.imageList = [];

    def readTree(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                self.fileList.append(os.path.join(root, file))

    def readExifTags(self):
        for img in self.fileList:
            f= Image.open(img)
            tags = self.get_exif_data(f)
            geolog = self.get_lat_lon(tags)

            image = ImageInfo()
            image.path = img
            image.name = img
            image.format = f.format
            image.lat = geolog[0]
            image.lon = geolog[1]
            image.dateTime = datetime.strptime(self._get_if_exist(tags, "DateTimeOriginal"), "%Y:%m:%d %H:%M:%S") #TODO: catch no datetime
            self.imageList.append(image);

    def saveToDb(self):
        s = self.session
        for img in self.imageList:
            s.add(img)
        s.commit()

    def get_exif_data(self, image):
        """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
        exif_data = {}
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]

                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value

        return exif_data

    def _get_if_exist(self, data, key):
        if key in data:
            return data[key]

        return None

    def _convert_to_degress(self, value):
        """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)

    def get_lat_lon(self, exif_data):
        """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
        lat = None
        lon = None

        if "GPSInfo" in exif_data:
            gps_info = exif_data["GPSInfo"]

            gps_latitude = self._get_if_exist(gps_info, "GPSLatitude")
            gps_latitude_ref = self._get_if_exist(gps_info, 'GPSLatitudeRef')
            gps_longitude = self._get_if_exist(gps_info, 'GPSLongitude')
            gps_longitude_ref = self._get_if_exist(gps_info, 'GPSLongitudeRef')

            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = self._convert_to_degress(gps_latitude)
                if gps_latitude_ref != "N":
                    lat = 0 - lat

                lon = self._convert_to_degress(gps_longitude)
                if gps_longitude_ref != "E":
                    lon = 0 - lon

        return lat, lon


trav = FileTreeReader()
trav.readTree('C:/Users\Enrico\PycharmProjects\Photos\Test')
trav.readExifTags()
trav.saveToDb()