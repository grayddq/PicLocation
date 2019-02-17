# -*- coding: utf-8 -*-
import exifread, requests, os, optparse


class Pic_Location:
    def __init__(self, pic_dir='', pic=''):
        self.pic_dir, self.pic = pic_dir, pic
        # 百度ak信息，可自行申请
        self.ak = 'YiSITcGEkm7z6ITj54gKVQbuTiQno7u8'

    def run(self):
        return self.dir_file() if self.pic_dir else [self.exifread_infos(self.pic)]

    # 遍历图片目录，非递归遍历获取图片信息数组
    def dir_file(self):
        files = [os.path.join(self.pic_dir, i) for i in os.listdir(self.pic_dir) if not os.path.isdir(i)]
        infos = [self.exifread_infos(pic) for pic in files]
        return infos

    # 获取照片时间、设备、经纬度信息
    # photo参数：照片文件路径
    def exifread_infos(self, photo):
        if not os.path.exists(photo):
            return {}
        f = open(photo, 'rb')
        tags = exifread.process_file(f)

        try:
            # 拍摄时间
            time = tags["EXIF DateTimeOriginal"].printable
            # 纬度
            LatRef = tags["GPS GPSLatitudeRef"].printable
            Lat = tags["GPS GPSLatitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
            Lat = float(Lat[0]) + float(Lat[1]) / 60 + float(Lat[2]) / float(Lat[3]) / 3600
            if LatRef != "N":
                Lat = Lat * (-1)
            # 经度
            LonRef = tags["GPS GPSLongitudeRef"].printable
            Lon = tags["GPS GPSLongitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
            Lon = float(Lon[0]) + float(Lon[1]) / 60 + float(Lon[2]) / float(Lon[3]) / 3600
            if LonRef != "E":
                Lon = Lon * (-1)
            # 拍摄设备
            device = tags["Image Make"].printable + tags["Image Model"].printable
            f.close()
            # 拍摄地址
            addr = self.get_location(Lon, Lat)
            return {'photo': photo, 'lon': Lon, 'lat': Lat, 'time': time, 'device': device, 'addr': addr}
        except:
            return {}

    # 根据经纬度获取地址信息
    def get_location(self, lon, lat):
        items = {'location': str(lat) + "," + str(lon), 'ak': self.ak, 'output': 'json'}
        header = {'Referer': '1.grayddq.top'}
        res = requests.get('http://api.map.baidu.com/geocoder/v2/', params=items, headers=header).json()
        return res['result']['formatted_address'] if res['status'] == 0 else ""


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-d", "--dir", dest="dir", help=u"target dir，demo: -d /home/root/")
    parser.add_option("-p", "--pic", dest="pic", help=u"target photo，demo: -p 1.jpg")
    options, _ = parser.parse_args()
    if options.dir or options.pic:
        infos = Pic_Location(pic_dir=options.dir).run() if options.dir else Pic_Location(pic=options.pic).run()
        for info in infos:
            if len(info)>0:
                print (u"图片：%s\n拍摄设备：%s\n拍摄时间：%s\n拍摄地址：%s\n经度：%s\n纬度：%s\n******************" % (
                    info['photo'], info['device'], info['time'], info['addr'], info['lon'], info['lat']))
    else:
        parser.print_help()
