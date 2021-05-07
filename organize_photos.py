import datetime
import glob
import os
import platform
import shutil
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS

# use Windows
output_image_dir = "intermediate_img"
input_pdf_dir = "input"


def exchange_pdf_to_image(file_path):
    """
    ファイル名の変更

    :param file_path: ファイル名（パス含む）
    :return: 変換後のファイル名
    """
    # ファイル名に設定する日時の取得
    file_date = get_date(file_path)

    # 保存用パスの設定とフォルダ生成
    file_directory = file_date.strftime("%Y%m")
    save_path = os.path.abspath(output_image_dir) + "/" + file_directory
    os.makedirs(save_path, exist_ok=True)

    # 保存ファイル名の設定
    new_file_name = file_date.strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(file_path)[1]
    new_file_path_base = save_path + "/IMG_" + new_file_name
    new_file_path = new_file_path_base + file_ext
    # print("1: ", new_file_path)

    # もし、同時刻のファイルが存在する場合、ファイル名に"_m[enum]"を追加する
    num = 0
    while os.path.exists(new_file_path):
        num += 1
        new_file_path = new_file_path_base + "_m" + str(num) + file_ext
        # print("2: ", new_file_path)

    new_path = file_path
    # new_path = shutil.copyfile(file_path, new_file_path)
    # new_path = shutil.move(file_path, new_file_path)

    # debug
    # 作成日時
    cd = datetime.datetime.fromtimestamp(os.path.getctime(new_path))
    # 更新日時
    md = datetime.datetime.fromtimestamp(os.path.getmtime(new_path))
    print("old: {0}, new: {1}, 作成日時： {2}, 更新日時： {3}".format(file_path, new_path, cd, md))
    return new_path


def get_exif_of_image(file_path):
    """
    Get EXIF of an image if exists.
    指定した画像のEXIFデータを取り出す

    :param file_path: ファイル名（パス含む）
    :return: exif_table Exif データを格納した辞書
    """
    # Exif データを取得
    # 存在しなければそのまま終了 空の辞書を返す
    try:
        im = Image.open(file_path)
        exif = im._getexif()
    except AttributeError:
        return {}
    except UnidentifiedImageError:
        return {}

    if not exif:
        return {}

    # タグIDそのままでは人が読めないのでデコードして
    # テーブルに格納する
    exif_table = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        exif_table[tag] = value
        print(tag, tag_id, value)
        # if "DateTimeOriginal" in tag:
        #     print(tag, tag_id, value)
        # if tag_id == 0x9003:
        #     print(tag, tag_id, value)

    return exif_table


def get_date(file_path):
    """
    exifに含まれている日付（取得できれば）か、
    ファイルの作成日時、更新日時のうち古い日付を返却する

    :param file_path: ファイル名（パス含む）
    :return: 日付
    """
    exif = get_exif_of_image(file_path)
    if "DateTimeOriginal" in exif:
        print("debug, a:", exif["DateTimeOriginal"])
        return datetime.datetime.strptime(exif["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
    else:
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


def run():
    os.makedirs(output_image_dir, exist_ok=True)
    # jpg_list = [p for p in glob.glob(input_pdf_dir + "/**", recursive=True) if re.search('/*\.(jpg|JPG|jpeg|png|gif|bmp)', str(p))]
    jpg_list = glob.glob(os.path.abspath(input_pdf_dir) + "/**/*.*", recursive=True)
    for file_path in jpg_list:
        exchange_pdf_to_image(file_path)


run()
