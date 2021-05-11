import glob
import os
import shutil

from date_operation import get_date

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

    # もし、同時刻のファイルが存在し、かつ、同じファイルサイズ出ない場合、ファイル名に"_m[enum]"を追加する
    num = 0
    file_size = os.path.getsize(file_path)
    while os.path.exists(new_file_path) and os.path.getsize(new_file_path) != file_size:
        print("debug: ", file_path)
        print("debug: ", file_size, os.path.getsize(new_file_path))
        num += 1
        new_file_path = new_file_path_base + "_m" + str(num) + file_ext

    response_path = new_file_path
    # response_path = shutil.copyfile(file_path, new_file_path)
    # response_path = shutil.move(file_path, new_file_path)

    # print("old: {0}, new: {1}".format(file_path, response_path))
    return response_path


def run():
    os.makedirs(output_image_dir, exist_ok=True)
    # file_list = [p for p in glob.glob(input_pdf_dir + "/**", recursive=True) if re.search('/*\.(jpg|JPG|jpeg|JPEG|png|gif|bmp)', str(p))]
    file_list = [p for p in glob.glob(input_pdf_dir + "/**", recursive=True) if os.path.isfile(p)]
    for file_path in file_list:
        exchange_pdf_to_image(file_path)


if __name__ == '__main__':
    run()
