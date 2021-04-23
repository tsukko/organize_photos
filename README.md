# organize_photos
organize_photos (Python)

# 仕様
./input フォルダ配下に画像ファイルを作成年月日の情報を元に整理する。  
outputパスは以下となる。  
`./intermediate_img/YYYYMM/YYYYMMDD_hhmmss.jpg`

## 例
- コマンド
```
python organize_photos.py
```
- ファイル類
```
./input/0001/aaa.jpg
./input/0001/bbb.jpg
./input/0002/bbb.jpg
./input/0002/test/bbb.jpg
```
- 変換結果
```
./intermediate_img/200401/20040110_121212.jpg
./intermediate_img/200401/20040111_121300.jpg
./intermediate_img/200402/20040201_121300.jpg
./intermediate_img/200402/20040201_121300_1.jpg
```
もし作成年月日が秒単位で同じものが存在してた場合、ファイル名の最後に「_1」「_2」、、、のように**アンダースコア＋1から始まる整数**を追加する。

# 作成した背景
Macbookの写真アプリが微妙で、他で管理したいのだが、画像ファイルの取り出しが何十万枚もあるとちょっとやりづらかった。

# 今後の展望
- jpgの拡張子以外に対象にすべき拡張子を洗い出して対応する
- 作成日、更新日、ファイルサイズが同じだったら無視させたい
- inputとoutputをもうちょっと柔軟にする（引数とか）
