import datetime
import os
import platform
import shutil
from pprint import pprint

import cv2
import ffmpeg as ffmpeg
import sys, time

import win32com.client
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS


def get_date_from_exif_of_image(file_path):
    """
    Get EXIF of an image if exists.
    指定した画像のEXIFデータを取り出す

    :param file_path: ファイル名（パス含む）
    :return: exif_table Exif データを格納した辞書
    """
    # Exif データを取得
    # 存在しなければそのまま終了 空の辞書を返す
    exif_date = None
    try:
        im = Image.open(file_path)
        exif = im._getexif()
        exif_table = {}
        if not exif:
            return {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_table[tag] = value
            print(tag, tag_id, value)
            if "DateTimeOriginal" in tag:
                exif_date = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")

            # if isinstance(tag, str) and "DateTimeOriginal" in tag:
            #     exif_date = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
            #     break
    except AttributeError:
        return {}
    except UnidentifiedImageError:
        return {}



    # タグIDそのままでは人が読めないのでデコードして
    # テーブルに格納する
    # exif_table = {}
    # for tag_id, value in exif.items():
    #     tag = TAGS.get(tag_id, tag_id)
    #     exif_table[tag] = value
    #     print(tag, tag_id, value)
    #     if isinstance(tag, str) and "DateTimeOriginal" in tag:
    #         exif_date = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    #         break
    #     # if "DateTimeOriginal" in tag:
    #     #     print(tag, tag_id, value)
    #     # if tag_id == 0x9003:
    #     #     print(tag, tag_id, value)


    return exif_date


def get_date_from_metadata(file_path):
    """
    ffmpegの機能により、ファイルのメタ情報から「メディアの作成日時」を取得する
    別途、ffmpegのインストールが必須

    :param file_path: ファイル名（パス含む）
    :return: 日付
    """
    # cap = cv2.VideoCapture(file_path)
    # print(cap)
    # aaaaa, img = cap.read()
    # print("dfasdfads:", aaaaa)
    # a = cap.getBackendName()
    # b = cap.get(cv2.detail.TIMELAPSER_CROP)
    # # c = cap.get(cv2.d)
    # print("fourcc: " + int(cap.get(cv2.CAP_PROP_FOURCC)).to_bytes(4, "little").decode("utf-8"))

    creation_time = None
    try:
        probe = ffmpeg.probe(file_path)
        # for stream in probe['streams']:
        #
        #     print('stream {0}: {1}'.format(stream['index'], stream['codec_type']))
        #     print(stream)  # Python3.8からsort_dicts=Falseが使える
        #     print('')

        creation_time = probe['streams'][0]["tags"]["creation_time"]
        # JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
        # # print(time.asctime(time.localtime(aa)))
        # date_dt = datetime.datetime.strptime(creation_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        # print(date_dt)
        # s ="2021-05-01T03:46:37.000000Z"
        # # d = datetime.datetime.fromisoformat(s)
        # # print(d)
        dt_utc = datetime.datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
        print(dt_utc)
        print(dt_utc.tzinfo)
        dt_jst = dt_utc.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
        print("======")
        print(dt_jst)

        creation_time = dt_jst
    except Exception as e:
        print("no creation_time from metadata. exception: {0}".format(e))
        return None

    return creation_time


def get_date_from_win32com(file_path):
    """
    win32com.clientの機能により、ファイルのメタ情報から「メディアの作成日時」を取得する
    GetDetailsOfの第二引数iColの値が変わる可能性があるため未使用

    :param file_path: ファイル名（パス含む）
    :return: 日付
    """
    folder_name, file_name = os.path.split(file_path)
    sh = win32com.client.Dispatch('Shell.Application')
    fol = sh.NameSpace(folder_name)
    fol_item = fol.ParseName(file_name)
    # for index in range(208, 500):
    #     print("index: {0}, data: {1}".format(index, fol.GetDetailsOf(folitem, index)))
    creation_time = fol.GetDetailsOf(fol_item, 208)
    # ex. 2021/05/01 12:46
    print("creation_time: ", creation_time)
    return creation_time


def get_date(file_path):
    """
    exifに含まれている日付（取得できれば）か、
    ファイルの作成日時、更新日時のうち古い日付を返却する

    :param file_path: ファイル名（パス含む）
    :return: 日付
    """
    creation_time = get_date_from_metadata(file_path)
    exif_date = get_date_from_exif_of_image(file_path)
    print("creation_time: {0}, exif_date: {1}".format(creation_time, exif_date))

    # 作成日時
    if platform.system() == 'Windows':
        ct = os.path.getctime(file_path)
    else:
        stat = os.stat(file_path)
        try:
            ct = stat.st_birthtime
        except AttributeError:
            ct = stat.st_mtime
            print("debug, c: ", ct)

    # 更新日時
    mt = os.path.getmtime(file_path)
    print("debug, b: ", datetime.datetime.fromtimestamp(min(ct, mt)))
    return datetime.datetime.fromtimestamp(min(ct, mt))
