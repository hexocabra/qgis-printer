#QGIS用一括印刷マクロ
#ｖ2.0　凝ったフォームを作って、リストビューで印刷レイアウトを選択できるようにした。
#ｖ3.0予定　・印刷の中心位置を参照するレイヤと一つの印刷レイアウトを選択して、連続印刷
#　　　　　　　・中心位置設定れいや（に限らず？）、特定の地物をフィルタリングして表示
#　　　　　　　・もし印刷レイアウト上のテキストボックスのオブジェクトIDと参照レイヤの属性が一緒だったら、テキストボックス内に属性を入れる

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import *

from qgis.core import *
from qgis.utils import *

#--------------------------------------------------------
class window(QDialog):
    def __init__(self):
        QDialog.__init__(self,None)
        self.setWindowTitle("QGIS用一括印刷マクロ")


class form_batchprint1(window):
    def __init__(self):
        super(form_batchprint1, self).__init__()
        
        #答え
        self.kotae = None
        
        #size
        self.setFixedSize(400,500)
        
        #set whole layout
        self.setLayout(self.exportLayout(None))
        
    def exportLayout(self,mainwindow):
        print(QgsProject)
        #ここでイベント関数宣言しないとイベントが持ってこれないみたい
        #ここでメインウィンドウの引数があるのは、このメソッドを読んだ本体であり、それを閉じれるようにしている。
        def listClicked(self):
            print("リストクリック")
            pass
            
        def pushOk(formobj,mainwindow):
            sidx = formobj.listview_layouts.selectedIndexes()
            kekka = [a.data() for a in sidx]
            formobj.kotae_layouts = kekka
            
            sidx = formobj.listview_exporttype.selectedIndexes()
            kekka = [a.data() for a in sidx]
            formobj.kotae_exporttype = kekka
            
            if len(formobj.kotae_layouts) > 0 and len(formobj.kotae_exporttype) > 0:
                formobj.close()
                if mainwindow is not None:
                    mainwindow.close()
                shori(formobj)
            else:
                ret = QMessageBox.information(None, "一括印刷", "エクスポートタイプか印刷レイアウトが選択されていません", QMessageBox.Yes)
                
                
        def pushCancel(formobj,mainwindow):
            print("キャンセルボタンを押しました")
            formobj.kotae_layouts = []
            formobj.kotae_exporttype = []
            #閉じる
            formobj.close()
            if mainwindow is not None:
                mainwindow.close()
                
        def shori(formobj):
            #ここに印刷関係の処理を書いちゃうことにする。
            convtype =formobj.kotae_exporttype[0]
            layouts = [layout for layout in formobj.layouts if layout.name() in formobj.kotae_layouts]
            #
            print(convtype)
            print([layout.name() for layout in layouts])
            #
            #フォルダ選択ダイアログ
            folder = str(QFileDialog.getExistingDirectory(QMainWindow(), "出力先のフォルダを選択してください"))
            #
            
            #プログレスバー
            progressMessageBar = iface.messageBar().createMessage("作成中・・・")
            progress = QProgressBar()
            progress.setMaximum(len(layouts))
            progress.setAlignment(Qt.AlignLeft)
            progressMessageBar.layout().addWidget(progress)
            iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)
            
            
            for li,layout in enumerate(layouts):
                progress.setValue(li+1)
                QApplication.processEvents()
                
                
                #エクスポータ
                export = QgsLayoutExporter(layout.atlas().layout())
                
                #出力
                if convtype == "jpg":
                    fpath = folder + "/{0}.jpg".format(layout.name())
                    kekka = export.exportToImage(fpath, settings=export.ImageExportSettings())
                elif convtype == "pdf":
                    fpath = folder + "/{0}.pdf".format(layout.name())
                    kekka = export.exportToPdf(fpath, settings=export.PdfExportSettings())
                
                print("出力完了： {0}".format(layout.name()))
                
            #プログレスバー終了メッセージ
            iface.messageBar().clearWidgets()
            iface.messageBar().pushMessage("完了しました :", duration=5)
            
        #印刷レイアウトリストを取得
        projectInstance = QgsProject.instance()
        layoutmanager = projectInstance.layoutManager()
        self.layouts = layoutmanager.printLayouts()
        layoutnames = [[layout.name()] for layout in self.layouts] #縦方向のリストを作る必要がある
        
        #make form listview
        self.listview_layouts = QListView()
        self.listview_layouts.clicked.connect(listClicked)
        self.listview_layouts.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        self.listview_exporttype = QListView()
        self.listview_exporttype.clicked.connect(listClicked)
        #self.listview_exporttype.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        #input Data
        self.headers = []
        self.model = MyTableModel(layoutnames,self.headers)
        self.listview_layouts.setModel(self.model)
        
        self.listview_exporttype.setModel(MyTableModel([["jpg"],["pdf"]],[]))
        
        #make label
        self.setumei0 = QLabel(self)
        self.setumei0.setText("★印刷レイアウトを一括印刷します★")
        
        self.setumei1 = QLabel(self)
        self.setumei1.setText("1.出力ファイルのタイプを選んでください。")
        
        self.setumei2 = QLabel(self)
        self.setumei2.setText("2.出力する印刷レイアウトを選んでください（複数選択可）。")
        
        #make Buttons
        self.buttonOk = QPushButton("OK",self)
        self.buttonCancel = QPushButton("Cancel",self)
        
        #set button group
        self.group = QButtonGroup()
        self.group.addButton(self.buttonOk)
        self.group.addButton(self.buttonCancel)
        
        #set Signal, Slot
        self.buttonOk.clicked.connect(lambda :pushOk(self,mainwindow)) #引数をトル場合は、ラムダ式を使う
        self.buttonCancel.clicked.connect(lambda :pushCancel(self,mainwindow))
        
        #set Holizontal layout
        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.setumei1)
        hlayout1.addWidget(self.setumei2)
        
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.listview_exporttype)
        hlayout2.addWidget(self.listview_layouts)
        
        hlayout3 = QHBoxLayout()
        hlayout3.addWidget(self.buttonOk)
        hlayout3.addWidget(self.buttonCancel)
        
        #set Vertical layout
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.setumei0)
        self.vlayout.addLayout(hlayout1)
        self.vlayout.addLayout(hlayout2)
        self.vlayout.addLayout(hlayout3)
        
        return self.vlayout

class MyTableModel(QAbstractTableModel):
    def __init__(self, list, headers = [], parent = None):
        QAbstractTableModel.__init__(self, parent)
        self.list = list
        self.headers = headers
    
    def rowCount(self, parent):
        return len(self.list)
    
    def columnCount(self, parent):
        return len(self.list[0])
    
    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def data(self, index, role):
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            return self.list[row][column]
        
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.list[row][column]
            return value
    
    def setData(self, index, value, role = Qt.EditRole):
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            self.list[row][column] = value
            self.dataChanged.emit(index, index)
            return True
        return False
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self.headers):
                    return self.headers[section]
                else:
                    return "not implemented"
            else:
                return "item %d" % section



#
print("__name__ = ",__name__)
if __name__ == '__console__':
    #--------------------------------------------------------
    #フォームを表示
    selectform = form_batchprint1()
    selectform.exec_()
    #
    print("おわり")



