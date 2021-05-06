import datetime
import glob
import os
import shutil
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS

# use Windows
output_image_dir = "intermediate_img"
input_pdf_dir = "input"


def exchange_pdf_to_image(file_name):
    """
    ファイル名の変更

    :param file_name: ファイル名（パス含む）
    :return: 変換後のファイル名
    """
    # debug
    # 作成日時
    ct = os.path.getctime(file_name)
    cd = datetime.datetime.fromtimestamp(ct)
    # 更新日時
    mt = os.path.getmtime(file_name)
    md = datetime.datetime.fromtimestamp(mt)

    # ファイル名に設定する日時の取得
    file_date = get_date(file_name)

    # 保存用パスの設定とフォルダ生成
    file_directory = file_date.strftime("%Y%m")
    save_path = os.path.abspath(output_image_dir) + "/" + file_directory
    os.makedirs(save_path, exist_ok=True)

    # 保存ファイル名の設定
    new_file_name = file_date.strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(file_name)[1]
    new_file_path_base = save_path + "/IMG_" + new_file_name
    new_file_path = new_file_path_base + file_ext
    # print("1: ", new_file_path)

    # もし、同時刻のファイルが存在する場合、ファイル名に"_m[enum]"を追加する
    num = 0
    while os.path.exists(new_file_path):
        num += 1
        new_file_path = new_file_path_base + "_m" + str(num) + file_ext
        # print("2: ", new_file_path)

    # new_path = shutil.copyfile(file_name, new_file_path)
    new_path = shutil.move(file_name, new_file_path)

    print(file_name, new_file_name, ", file_date:", file_date, ", 作成日時：", cd, ", 更新日時：", md)
    return new_path


def get_exif_of_image(file):
    """
    Get EXIF of an image if exists.
    指定した画像のEXIFデータを取り出す

    :param file: ファイル名（パス含む）
    :return: exif_table Exif データを格納した辞書
    """
    # Exif データを取得
    # 存在しなければそのまま終了 空の辞書を返す
    try:
        im = Image.open(file)
        exif = im._getexif()
    except AttributeError:
        return {}
    except UnidentifiedImageError:
        return {}

    # タグIDそのままでは人が読めないのでデコードして
    # テーブルに格納する
    exif_table = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        exif_table[tag] = value

    return exif_table


def get_date(file_name) -> datetime:
    """
    exifに含まれている日付（取得できれば）か、
    ファイルの作成日時、更新日時のうち古い日付を返却する

    :param file_name: ファイル名（パス含む）
    :return: 日付
    """
    exif = get_exif_of_image(file_name)
    if "DateTimeOriginal" in exif:
        # strftime() で新しい名前のフォーマットを指定
        # print("debug, a:", exif["Date\\\\\\TimeOriginal"])
        return datetime.datetime.strptime(exif["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
    else:
        # 作成日時
        ct = os.path.getctime(file_name)
        # 更新日時
        mt = os.path.getmtime(file_name)
        # print("debug, b: ", datetime.datetime.fromtimestamp(min(ct, mt)))
        return datetime.datetime.fromtimestamp(min(ct, mt))


def run():
    os.makedirs(output_image_dir, exist_ok=True)
    # jpg_list = [p for p in glob.glob(input_pdf_dir + "/**", recursive=True) if re.search('/*\.(jpg|JPG|jpeg|png|gif|bmp)', str(p))]
    jpg_list = glob.glob(os.path.abspath(input_pdf_dir) + "/**/*.*", recursive=True)
    for file_name in jpg_list:
        exchange_pdf_to_image(file_name)


run()
