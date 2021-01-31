#QGIS用一括印刷マクロ
#ｖ2.0　凝ったフォームを作って、リストビューで印刷レイアウトを選択できるようにした。
#ｖ4.0　個別のフォームを作って、それをタブに追加できるようにした。
#　　　　　あとは、出力の種類毎にフォームを作って、このフォームのタブコントロールに追加していくだけ。
#v4.4 Githubにいれてみた。
#ｖ5.0予定　・印刷の中心位置を参照するレイヤと一つの印刷レイアウトを選択して、連続印刷
#　　　　　　　・中心位置設定れいや（に限らず？）、特定の地物をフィルタリングして表示
#　　　　　　　・もし印刷レイアウト上のテキストボックスのオブジェクトIDと参照レイヤの属性が一緒だったら、テキストボックス内に属性を入れる
#

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import *

#このまま実行しても、どうしてかこの実行ファイルのパスが受け取れないらしい。
#なので、仕方がないので、QGISプロジェクトファイルの配下のScriptディレクトリをアペンドするしかない？
import sys
import os
sys.path.append(os.getcwd() + "/scripts/")

#フォームのクラスをインポート タブの中身を集める
import batchprint1
import batchprint2

#--------------------------------------------------------
class window(QDialog):
    def __init__(self):
        QDialog.__init__(self,None)
        self.setWindowTitle("QGIS用一括印刷マクロ")

class form_batchprint_main(window):
    def __init__(self):
        super(form_batchprint_main, self).__init__()
        
        #tab1
        tab1 = QWidget()
        tab1content = batchprint1.form_batchprint1()
        tab1.setLayout(tab1content.exportLayout(self)) #ここで引数にこのクラスを入れておき、送った先で閉じてもらうようになっている
        
        tab2 = QWidget()
        tab2content = batchprint2.form_batchprint2()
        tab2.setLayout(tab2content.exportLayout(self))
        
        tab3 = QWidget()
        tab3content = batchprint2.form_batchprint2()
        tab3.setLayout(tab3content.exportLayout(self))
        
        tab4 = QWidget()
        tab4content = batchprint2.form_batchprint2()
        tab4.setLayout(tab4content.exportLayout(self))
        
        #tabたちをまとめる
        tabwidget = QTabWidget()
        tabwidget.insertTab(0,tab1,"印刷レイアウト一括出力")
        tabwidget.insertTab(1,tab2,"フィルタをかけて印刷レイアウト一括出力")
        tabwidget.insertTab(2,tab3,"地物イテレート出力")
        tabwidget.insertTab(3,tab4,"印刷フォームIDにデータいれながら出力")
        
        #mainwindowにtabを組み込む
        wholelayout = QVBoxLayout()
        wholelayout.addWidget(tabwidget)
        self.setLayout(wholelayout)





#--------------------------------------------------------
#プリントコンポーザのレイアウトリストを取得
selectform = form_batchprint_main()
selectform.exec_()
print("終了")