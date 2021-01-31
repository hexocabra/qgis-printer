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

class form_batchprint2(window):
    def __init__(self):
        super(form_batchprint2, self).__init__()
        
        #答え
        self.kotae = None
        
        #size
        self.setFixedSize(500,600)
        
        self.setLayout(self.exportLayout(None))
        
    def exportLayout(self,mainwindow):
        #イベント用関数たち
        def pushOk(formobj,maiwindow):
            sidx = formobj.listview_layouts.selectedIndexes()
            kekka = [a.data() for a in sidx]
            self.kotae_layouts = kekka
            
            sidx = formobj.listview_exporttype.selectedIndexes()
            kekka = [a.data() for a in sidx]
            formobj.kotae_exporttype = kekka
            
            formobj.kotae_filterfomula = formobj.tab1joken
            
            sidx = formobj.listview_layers.selectedIndexes()
            kekka = [a.data() for a in sidx]
            formobj.kotae_targetlayers = kekka
            
            sidx = formobj.listview_layerattributes.selectedIndexes()
            kekka = [a.data() for a in sidx]
            formobj.kotae_targetattributes = kekka
            
            #入力チェック
            errorari = False
            if len(formobj.kotae_layouts) == 0 or len(formobj.kotae_exporttype) == 0:
                errorari = True
                formobj.attention.setText("エクスポートタイプか印刷レイアウトが選択されていません\n")
                
            if errorari == False:
                formobj.close()
                if mainwindow is not None:
                    mainwindow.close()
                shori(formobj)
            
            
        def pushCancel(formobj,maiwindow):
            print("キャンセルボタンを押しました")
            formobj.kotae_layouts = []
            formobj.kotae_exporttype = []
            #閉じる
            formobj.close()
            if mainwindow is not None:
                mainwindow.close()
            
        def listClicked(formobj,maiwindow):
            pass
        
        def tab1joken_changed(formobj,maiwindow):
            #フィルタ条件式を変化させたら起動
            siki = formobj.tab1joken.text()
            
            #変数を定義 "layout.name()[0:5]"
            layout = layouts[0]
            kekka = eval(siki)
            formobj.tab1jokenkekka.setText(kekka)
        
        def canvaslayersClicked(formobj,maiwindow):
            #フィルタ対象のレイヤリストをクリックした時
            #フィルタする属性リストを選択するリストビューを更新する
            sidx = formobj.listview_layers.selectedIndexes()
            kekka = [a.data() for a in sidx] #テキストの状態
            formobj.selectedCanvasLayers = [a for a in formobj.canvaslayers if a.name() in kekka] #テキストからオブジェクトを吸い出す
            
            #１つ目の選択レイヤから属性リストを取り出す
            features = formobj.selectedCanvasLayers[0].getFeatures()
            featureslist = [f for f in features]#そのままイテレーションできない
            featureheaders = [[a] for a in featureslist[0].fields().names()] #ヘッダー名のリストの縦書き
            
            #属性リストを更新
            #self.listview_layers = QListView()
            formobj.listview_layerattributes.setModel(MyTableModel(featureheaders,[]))
            
        def shori(formobj):
            #まだ途中、レイヤの名前からキーワードをとって、そのキーワードでレイヤにフィルタをかける
            
            #出力タイプ
            convtype =selectform.kotae_exporttype[0]
            
            #出力するレイアウトリスト
            layouts = [layout for layout in layouts if layout.name() in selectform.kotae_layouts]
            
            #式
            filterfomula = selectform.tab1joken.text()
            
            #フィルタ対象のレイヤリスト
            filtertargetlayers = selectform.self.selectedCanvasLayers
            
            #フィルタする属性名
            filterattributename = self.tab1joken
            
            print(convtype)
            print([layout.name() for layout in layouts])
            
            #フォルダ選択ダイアログ
            folder = str(QFileDialog.getExistingDirectory(QMainWindow(), "出力先のフォルダを選択してください"))
            
            for layout in layouts:
                
                if filterfomula != "":
                    #filter ON
                    keyword = eval(filterfomula)
                    
                    #レイヤに表示フィルタをかける
                    for layer in filtertargetlayers:
                        layer.setSubsetString( '"{0}" = {1}'.format(filterattributename,keyword) )
                
                
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
                
            #フィルタを解除
            for layer in filtertargetlayers:
                layer.setSubsetString('')
            print("おわり")
            
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #印刷レイアウトリストを取得
        projectInstance = QgsProject.instance()
        layoutmanager = projectInstance.layoutManager()
        self.layouts = layoutmanager.printLayouts()
        layoutnames = [[layout.name()] for layout in self.layouts] #縦方向のリストを作る必要がある
        
        #make form listview
        self.listview_layouts = QListView()
        self.listview_layouts.clicked.connect(lambda :listClicked(self,mainwindow))
        self.listview_layouts.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        self.listview_exporttype = QListView()
        self.listview_exporttype.clicked.connect(lambda:listClicked(self,mainwindow))
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
        
        #フィルタ条件式のテキストボックス
        self.tab1jokentext = QLabel(self)
        self.tab1jokentext.setText("３．layout.name()[0:5]　というような式をかける")
        self.tab1joken = QLineEdit(self)
        self.tab1joken.textChanged.connect(lambda :tab1joken_changed(self,mainwindow))
        self.tab1joken.setText("")
        self.tab1jokenkekka = QLabel(self)
        self.tab1jokenkekka.setText("結果")
        tab1jokenboxh = QHBoxLayout()
        tab1jokenboxh.addWidget(self.tab1joken)
        tab1jokenboxh.addWidget(self.tab1jokenkekka)
        tab1jokenbox = QVBoxLayout()
        tab1jokenbox.addWidget(self.tab1jokentext)
        tab1jokenbox.addLayout(tab1jokenboxh)
        
        #フィルタ対象のレイヤリスト
        canvas = iface.mapCanvas()
        self.canvaslayers = canvas.layers()
        self.canvaslayernames = [[a.name()] for a in self.canvaslayers]
        self.listview_layers = QListView()
        self.listview_layers.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listview_layers.clicked.connect(lambda :canvaslayersClicked(self,mainwindow))
        self.listview_layers.setModel(MyTableModel(self.canvaslayernames,[]))
        
        #フィルタ対象のレイヤのどの属性でフィルタをするか　レイヤ０の地物リストを出して、そこから選ぶ
        layerattributes = [["フィルタするレイヤを左で選んでください。"]]
        self.listview_layerattributes = QListView()
        self.listview_layerattributes.setModel(MyTableModel(layerattributes,[]))
        
        #フィルタ対象のレイヤリストのレイアウト
        filtertargetlayout = QHBoxLayout()
        filtertargetlayout.addWidget(self.listview_layers)
        filtertargetlayout.addWidget(self.listview_layerattributes)
        
        
        
        #set Holizontal layout
        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.setumei1)
        hlayout1.addWidget(self.setumei2)
        
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.listview_exporttype)
        hlayout2.addWidget(self.listview_layouts)
        
        
        
        #make Buttons
        self.buttonOk = QPushButton("OK",self)
        self.buttonCancel = QPushButton("Cancel",self)
        
        #set Signal, Slot
        self.buttonOk.clicked.connect(lambda :pushOk(self,mainwindow))
        self.buttonCancel.clicked.connect(lambda :pushCancel(self,mainwindow))
        
        #set button group
        self.group = QButtonGroup()
        self.group.addButton(self.buttonOk)
        self.group.addButton(self.buttonCancel)
        
        hlayout3 = QHBoxLayout()
        hlayout3.addWidget(self.buttonOk)
        hlayout3.addWidget(self.buttonCancel)
        
        #注意出力
        self.attention = QLabel(self)
        self.attention.setText("****")
        self.attention.setStyleSheet("QLabel{ color: rgb(255, 0, 0)}")
        
        
        #set Vertical layout
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.setumei0)
        vlayout.addLayout(hlayout1)
        vlayout.addLayout(hlayout2)
        vlayout.addLayout(tab1jokenbox)
        vlayout.addLayout(filtertargetlayout)
        vlayout.addLayout(hlayout3)
        vlayout.addWidget(self.attention)
        return vlayout
        
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






#--------------------------------------------------------
if __name__ == '__console__':
    selectform = form_batchprint2()
    selectform.exec_()
    
    