import datetime
import glob
import os

# use Windows
import shutil

output_image_dir = "intermediate_img"
input_pdf_dir = "input"


def exchange_pdf_to_image(file_name):
    # 作成日時
    ct = os.path.getctime(file_name)
    cd = datetime.datetime.fromtimestamp(ct)

    # 更新日時
    mt = os.path.getmtime(file_name)
    md = datetime.datetime.fromtimestamp(mt)

    # 保存用パス
    file_directory = md.strftime("%Y%m")
    save_path = output_image_dir + "/" + file_directory
    output_setting(save_path)

    # 保存ファイル名
    new_file_name = md.strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(file_name)[1]
    new_file_path_base = save_path + "/" + new_file_name
    new_file_path = new_file_path_base + file_ext
    print("1: ", new_file_path)

    # もし、同時刻のファイルが存在する場合、ファイル名に"_[enum]"を追加する
    num = 0
    while os.path.exists(new_file_path):
        num += 1
        new_file_path = new_file_path_base + "_" + str(num) + file_ext
        print("2: ", new_file_path)

    shutil.copyfile(file_name, new_file_path)

    print(file_name, cd, md, new_file_name)


# 結果の出力用ディレクトリが存在しなければ、生成する
def output_setting(file_directory):
    if not os.path.exists(file_directory):
        os.makedirs(file_directory)


def run():
    output_setting(output_image_dir)
    pdf_list = glob.glob(input_pdf_dir + "/**/*.jpg")
    for file_name in pdf_list:
        exchange_pdf_to_image(file_name)


run()
