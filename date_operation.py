import datetime
import os
import platform
import ffmpeg as ffmpeg
# import win32com.client
# from PIL import Image
# from PIL.ExifTags import TAGS
import exifread


def get_date_from_filename(file_path):
    # 例：IMG_20160413_110810.mp4　→　20160413_110810
    filename_date = None
    try:
        file_ext = os.path.splitext(os.path.basename(file_path))[0][4:19]
        filename_date = datetime.datetime.strptime(file_ext, "%Y%m%d_%H%M%S")
        # print("filename_date: ", filename_date)
        filename_date = filename_date.timestamp()
    except Exception as e:
        # print("get_date_from_filename. exception: {0}".format(e))
        return None

    return filename_date


def get_date_from_metadata(file_path):
    """
    ffmpegの機能により、ファイルのメタ情報から「メディアの作成日時」を取得する
    別途、ffmpegのインストールが必須

    :param file_path: ファイル名（パス含む）
    :return: creation_time（UNIX TIME） メディアの作成日時
    """
    creation_time = None
    try:
        probe = ffmpeg.probe(file_path)
        creation_time = probe['streams'][0]["tags"]["creation_time"]
        dt_utc = datetime.datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
        # dt_jst = dt_utc.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
        # print(dt_utc, ", utc timestamp(): ", dt_utc.timestamp())
        # print(dt_jst, ", jst timestamp(): ", dt_jst.timestamp())
        creation_time = dt_utc.timestamp()
    except Exception as e:
        # print("no creation_time from metadata. exception: {0}".format(e))
        return None

    return creation_time


# def get_date_from_win32com(file_path):
#     """
#     win32com.clientの機能により、ファイルのメタ情報から「メディアの作成日時」を取得する
#     GetDetailsOfの第二引数iColの値が変わる可能性があるため未使用
#
#     :param file_path: ファイル名（パス含む）
#     :return: 日付
#     """
#     folder_name, file_name = os.path.split(file_path)
#     sh = win32com.client.Dispatch('Shell.Application')
#     fol = sh.NameSpace(folder_name)
#     fol_item = fol.ParseName(file_name)
#     # for index in range(0, 210):
#     #     print("index: {0}, data: {1}".format(index, fol.GetDetailsOf(fol_item, index)))
#     creation_time = fol.GetDetailsOf(fol_item, 208)
#     # aaaa = datetime.datetime.strptime(creation_time, "%Y/%m/%d %H:%M").timestamp()
#     # ex. 2021/05/01 12:46
#     print("creation_time: ", creation_time)
#     return creation_time


def get_date_from_exif_of_image(file_path):
    """
    Get EXIF of an image if exists.
    指定した画像のEXIFデータを取り出す

    :param file_path: ファイル名（パス含む）
    :return: exif_date EXIF DateTimeOriginal（UNIX TIME） 撮影日時
    """
    exif_date = None
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
        if 'EXIF DateTimeOriginal' in tags.keys():
            datetime_original = tags['EXIF DateTimeOriginal'].values
            exif_date = datetime.datetime.strptime(datetime_original, "%Y:%m:%d %H:%M:%S").timestamp()
            return exif_date

        # im = Image.open(file_path)
        # exif = im._getexif()
        # for tag_id, value in exif.items():
        #     tag = TAGS.get(tag_id, tag_id)
        #     if isinstance(tag, str) and "DateTimeOriginal" in tag:
        #         exif_date = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S").timestamp()
        #         break
    except Exception as e:
        # print("no exif_date. exception: {0}".format(e))
        return None

    return exif_date


def get_date(file_path):
    """
    exifに含まれている日付（取得できれば）か、
    ファイルの作成日時、更新日時のうち古い日付を返却する

    :param file_path: ファイル名（パス含む）
    :return: 日付
    """
    # file名の日時
    filename_date = get_date_from_filename(file_path)
    # メタ情報「メディアの作成日時」
    creation_time = get_date_from_metadata(file_path)
    # EXIF「撮影日時」
    exif_date = get_date_from_exif_of_image(file_path)
    # 作成日時
    if platform.system() == 'Windows':
        ct = os.path.getctime(file_path)
    else:
        stat = os.stat(file_path)
        try:
            ct = stat.st_birthtime
        except AttributeError:
            ct = stat.st_mtime
            # print("debug, c: ", ct)
    # 更新日時
    mt = os.path.getmtime(file_path)

    min_date = datetime.datetime.fromtimestamp(min(
        [item for item in [filename_date, creation_time, exif_date, ct, mt] if item]
    ))
    # print("min_date: ", min_date, "|",
    #       "filename_date: ", filename_date,
    #       "creation_time: ", creation_time,
    #       "exif_date: ", exif_date,
    #       "ct: ", ct,
    #       "mt: ", mt)
    print("min_date: ", min_date, "|",
          "filename_date: ", print_date(filename_date),
          "creation_time: ", print_date(creation_time),
          "exif_date: ", print_date(exif_date),
          "ct: ", print_date(ct),
          "mt: ", print_date(mt))

    # もし、日付を強制的に指定したい場合、ここで指定する
    # min_date = datetime.datetime.strptime("20030801_025102", "%Y%m%d_%H%M%S")
    return min_date


def print_date(date):
    if date:
        return datetime.datetime.fromtimestamp(date)
    else:
        return date
