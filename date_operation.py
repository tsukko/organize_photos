import datetime
import os
import platform

# import win32com.client
# from PIL import Image
# from PIL.ExifTags import TAGS
import exifread
# Windows側でExiftoolのインストールが必須
import exiftool
import ffmpeg as ffmpeg

"""
以下のファイル形式で日時を取得できるようにする必要がある

静止画
JPG、JPEG ・・・カメラ撮影　EXIF:DateTimeOriginal
            FileModifyDateはダメで、ModifyDateの場合もあり
PNG　　　　・・・スクショ　FileModifyDate
HEIC 　　　・・・iPhoneの高効率フォーマット、今は使わない　DateTimeOriginal

動画
mov・・・iPhone　　FileModifyDate　CreateDateはダメ、CreationDate
avi・・・古めのデジカメ、一眼 FileModifyDate　DateTimeOriginal★
MTG・・・デジカメ　DateTimeOriginal
mp4・・・CreateDate　
mpg・・・FileModifyDate
"""


def get_date_from_filename(file_path):
    # 例：IMG_20160413_110810.mp4　→　20160413_110810
    filename_date = None
    try:
        file_ext = os.path.splitext(os.path.basename(file_path))[0][4:19]
        filename_date = datetime.datetime.strptime(file_ext, "%Y%m%d_%H%M%S")
        # print("filename_date: ", filename_date)
        filename_date = filename_date.timestamp()
    except Exception as e:
        print("get_date_from_filename. exception: {0}".format(e))
        return None

    return filename_date


def get_date_from_metadata(file_path):
    """
    ffmpegの機能により、ファイルのメタ情報から「メディアの作成日時」を取得する
    別途、Windows側にffmpeg、Python側にffmpeg-pythonのインストールが必須
    mp4、movファイル、主に動画系

    :param file_path: ファイル名（パス含む）
    :return: creation_time（UNIX TIME） メディアの作成日時
    """
    creation_time = None
    try:
        probe = ffmpeg.probe(file_path)
        # if "streams"not in probe or "tags" not in probe or "creation_time" not in probe:
        if "streams" not in probe \
                or "tags" not in probe["streams"][0] \
                or "creation_time" not in probe["streams"][0]["tags"]:
            return None
        creation_time = probe["streams"][0]["tags"]["creation_time"]
        dt_utc = datetime.datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
        # dt_jst = dt_utc.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
        # print(dt_utc, ", utc timestamp(): ", dt_utc.timestamp())
        # print(dt_jst, ", jst timestamp(): ", dt_jst.timestamp())
        creation_time = dt_utc.timestamp()
    except Exception as e:
        print("get_date_from_metadata. file: {0}, exception: {1}".format(os.path.basename(file_path), e))
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
    # get_date_from_imageで同様のデータが取得
    Get EXIF of an image if exists.
    指定した画像のEXIFデータを取り出す
    画像のみ対応。動画（.MTSファイル）では取得不可

    :param file_path: ファイル名（パス含む）
    :return: exif_date EXIF DateTimeOriginal（UNIX TIME） 撮影日時
    """

    exif_date_time_original = None
    exif_image_datetime = None
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
        if not len(tags):
            return None, None
        if 'EXIF DateTimeOriginal' in tags.keys():
            datetime_original = tags['EXIF DateTimeOriginal'].values
            exif_date_time_original = datetime.datetime.strptime(datetime_original, "%Y:%m:%d %H:%M:%S").timestamp()
        if 'Image DateTime' in tags.keys():
            image_datetime = tags['Image DateTime'].values
            exif_image_datetime = datetime.datetime.strptime(image_datetime, "%Y:%m:%d %H:%M:%S").timestamp()

        # im = Image.open(file_path)
        # exif = im._getexif()
        # for tag_id, value in exif.items():
        #     tag = TAGS.get(tag_id, tag_id)
        #     if isinstance(tag, str) and "DateTimeOriginal" in tag:
        #         exif_date = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S").timestamp()
        #         break
    except Exception as e:
        print("get_date_from_exif_of_image. file: {0}, exception: {1}".format(os.path.basename(file_path), e))
        return None

    return exif_date_time_original, exif_image_datetime


def get_date_from_image(file_path):
    """
    Get EXIF of an image if exists.
    指定した画像のEXIFデータを取り出す

    :param file_path: ファイル名（パス含む）
    :return: exif_date EXIF DateTimeOriginal（UNIX TIME） 撮影日時
    """
    metadata = None
    ut_modify_date, ut_create_date, ut_create_date_quicktime, ut_creation_date_quicktime, ut_modify_date_xmp, ut_modify_date_exif,\
    ut_date_time_original_exif, ut_date_time_original_h264, ut_date_time_original_riff, ut_date_time_original_notes = None, None, None, None, None, None, None, None, None, None
    try:
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(file_path)
    except Exception as e:
        print("get_date_from_image. file: {0}, exception: {1}".format(os.path.basename(file_path), e))
        return [None, None, None, None, None, None, None, None, None, None]

    if not len(metadata):
        print("get_date_from_image. no data. file: {0}".format(os.path.basename(file_path)))
        return [None, None, None, None, None, None, None, None, None, None]

    create_date_file = metadata[0].get("File:FileCreateDate")
    if create_date_file:
        ut_create_date = datetime.datetime.strptime(create_date_file, "%Y:%m:%d %H:%M:%S%z").timestamp()

    create_date_quicktime = metadata[0].get("QuickTime:CreateDate")
    if create_date_quicktime:
        ut_create_date_quicktime = datetime.datetime.strptime(create_date_quicktime, "%Y:%m:%d %H:%M:%S").timestamp()

    creation_date_quicktime = metadata[0].get("QuickTime:CreationDate")
    if creation_date_quicktime:
        ut_creation_date_quicktime = datetime.datetime.strptime(creation_date_quicktime, "%Y:%m:%d %H:%M:%S%z").timestamp()

    modify_date_file = metadata[0].get("File:FileModifyDate")
    if modify_date_file:
        ut_modify_date = datetime.datetime.strptime(modify_date_file, "%Y:%m:%d %H:%M:%S%z").timestamp()

    modify_date_xmp = metadata[0].get("XMP:ModifyDate")
    if modify_date_xmp:
        ut_modify_date_xmp = datetime.datetime.strptime(modify_date_xmp, "%Y:%m:%d %H:%M:%S").timestamp()

    modify_date_exif = metadata[0].get("EXIF:ModifyDate")
    if modify_date_exif:
        ut_modify_date_exif = datetime.datetime.strptime(modify_date_exif, "%Y:%m:%d %H:%M:%S").timestamp()

    date_time_original_exif = metadata[0].get("EXIF:DateTimeOriginal")
    if date_time_original_exif:
        ut_date_time_original_exif = datetime.datetime.strptime(date_time_original_exif,
                                                                "%Y:%m:%d %H:%M:%S").timestamp()

    date_time_original_h264 = metadata[0].get("H264:DateTimeOriginal")
    if date_time_original_h264:
        ut_date_time_original_h264 = datetime.datetime.strptime(date_time_original_h264, '%Y:%m:%d %H:%M:%S%z').timestamp()

        # ut_date_time_original_h264 = datetime.datetime.strptime(date_time_original_h264,
        #                                                         "%Y:%m:%d %H:%M:%S").timestamp()

    date_time_original_riff = metadata[0].get("RIFF:DateTimeOriginal")
    if date_time_original_riff:
        ut_date_time_original_riff = datetime.datetime.strptime(date_time_original_riff,
                                                                "%Y:%m:%d %H:%M:%S").timestamp()

    date_time_original_notes = metadata[0].get("MakerNotes:DateTimeOriginal")
    if date_time_original_notes:
        ut_date_time_original_notes = datetime.datetime.strptime(date_time_original_notes,
                                                                 "%Y:%m:%d %H:%M:%S").timestamp()

    return [ut_create_date,
            ut_create_date_quicktime,
            ut_creation_date_quicktime,
            ut_modify_date,
            ut_modify_date_xmp,
            ut_modify_date_exif,
            ut_date_time_original_exif,
            ut_date_time_original_h264,
            ut_date_time_original_riff,
            ut_date_time_original_notes]


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
    exif_date_time_original, exif_image_datetime = None, None
    # exif_date_time_original, exif_image_datetime = get_date_from_exif_of_image(file_path)

    exif_date_list = get_date_from_image(file_path)
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

    date_list = [filename_date, creation_time, exif_date_time_original, exif_image_datetime, ct, mt]
    date_list.extend(exif_date_list)

    min_date = datetime.datetime.fromtimestamp(min([item for item in date_list if item]))
    # print("min_date: ", min_date, "|",
    #       "filename_date: ", filename_date,
    #       "creation_time: ", creation_time,
    #       "exif_date: ", exif_date,
    #       "ct: ", ct,
    #       "mt: ", mt)
    print("min_date: ", min_date, "|",
          "filename_date: ", print_date(filename_date),
          "creation_time: ", print_date(creation_time),
          "create_date", print_date(exif_date_list[0]),
          "creation_date_qt", print_date(exif_date_list[1]),
          "create_date_qt", print_date(exif_date_list[2]),
          "modify_date", print_date(exif_date_list[3]),
          "modify_date_xmp", print_date(exif_date_list[4]),
          "modify_date_exif", print_date(exif_date_list[5]),
          "date_time_original_exif", print_date(exif_date_list[6]),
          "date_time_original_h264", print_date(exif_date_list[7]),
          "date_time_original_riff", print_date(exif_date_list[8]),
          "date_time_original_notes", print_date(exif_date_list[9]),
          "exif_date_time_original: ", print_date(exif_date_time_original),
          "exif_image_datetime: ", print_date(exif_image_datetime),
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
