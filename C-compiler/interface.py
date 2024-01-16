import sys
import CFFX
import YFFX
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QHBoxLayout, QWidget, QAction, QTextEdit, \
    QFileDialog, QDesktopWidget, QMessageBox, QLabel
from functools import partial


class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.center()  # 将窗口移动到屏幕中央

    def initUI(self):

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('文件')

        openFile = QAction('打开文件', self)
        openFile.triggered.connect(self.showDialog)
        fileMenu.addAction(openFile)

        saveFile = QAction('保存文件', self)
        saveFile.triggered.connect(self.saveDialog)
        fileMenu.addAction(saveFile)

        lexAnalysis = QAction('词法分析', self)
        lexAnalysis.triggered.connect(partial(self.analysisAction, '词法分析'))
        menubar.addAction(lexAnalysis)

        syntaxAnalysis = QAction('语法分析', self)
        syntaxAnalysis.triggered.connect(partial(self.analysisAction, '语法分析'))
        menubar.addAction(syntaxAnalysis)

        semanticAnalysis = QAction('语义分析', self)
        semanticAnalysis.triggered.connect(partial(self.analysisAction, '语义分析'))
        menubar.addAction(semanticAnalysis)

        intermediateCode = QAction('中间代码生成', self)
        intermediateCode.triggered.connect(partial(self.analysisAction, '中间代码生成'))
        menubar.addAction(intermediateCode)

        exitAction = QAction('退出', self)
        exitAction.triggered.connect(self.close)
        menubar.addAction(exitAction)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('C子集编译器')
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        main_layout = QVBoxLayout(self.centralWidget)

        # 嵌套的水平布局
        layout = QHBoxLayout()

        # 左侧大文本框
        self.textEdit1 = QTextEdit(self.centralWidget)
        layout.addWidget(self.textEdit1)

        # 右侧布局
        right_layout = QVBoxLayout()

        # 右上小文本框
        self.textEdit2 = QTextEdit(self.centralWidget)
        right_layout.addWidget(self.textEdit2)

        # 右下小文本框
        self.textEdit3 = QTextEdit(self.centralWidget)
        right_layout.addWidget(self.textEdit3)

        layout.addLayout(right_layout)

        # 在主布局中添加用于显示提示信息的QLabel
        self.noteLabel = QLabel('注意，修改源文件后需要重新运行所有分析文件', self.centralWidget)
        self.noteLabel.setStyleSheet("color: black; font-style: normal")
        main_layout.addLayout(layout)
        main_layout.addWidget(self.noteLabel)  # 添加到右侧布局中

    def center(self):
        # 获取窗口的尺寸
        qr = self.frameGeometry()

        # 获取主屏幕的尺寸并计算中心位置
        cp = QDesktopWidget().availableGeometry().center()

        # 移动窗口到屏幕中央
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, '打开文件', '', 'C Source Files (*.c);;All Files (*)')
        if fname[0]:
            with open(fname[0], 'r') as f:
                content = f.read()
                self.textEdit1.setPlainText(content)

    def saveDialog(self):
        fname = QFileDialog.getSaveFileName(self, '保存文件', '', 'C Source Files (*.c);;All Files (*)')
        if fname[0]:
            with open(fname[0], 'w') as f:
                f.write(self.textEdit1.toPlainText())

    def analysisAction(self, analysis_type):
        content = self.textEdit1.toPlainText()
        # 检查是否有内容
        if not content:
            QMessageBox.warning(self, '警告', '请先打开文件或输入源代码')
            return
        if analysis_type == '词法分析':
            # 调用词法分析的函数
            tokens, errors = CFFX.gettoken(content)

            # 在右上文本框中显示词法分析结果
            token_result = ""
            for token in tokens:
                token_result += f"{token.word} {token.code}\n"
            self.textEdit2.setPlainText(token_result)

            # 在右下文本框中显示词法分析中的错误信息
            error_result = "\n".join(errors)
            self.textEdit3.setPlainText(error_result)
            da1 = ''
            # 判断是否有词法错误
            if not errors:
                da1 += '词法分析完成!'
                self.textEdit3.setPlainText(da1)
        elif analysis_type == '语法分析':
            self.yufa()
        elif analysis_type == '语义分析':
            self.yuyi()
        elif analysis_type == '中间代码生成':
            self.middle()

    def yufa(self):
        YFFX.get_token()
        YFFX.parser()
        YFFX.write_quater()
        da2 = ""
        if not YFFX.wrong:
            da2 = "语法分析完成！"
        else:
            for i in YFFX.wrong:
                da2 += "语法错误" + ' ' + i + '\n'
        self.textEdit3.setPlainText(da2)

    def yuyi(self):
        YFFX.get_token()
        YFFX.parser()
        YFFX.write_quater()
        da2 = ""
        if not YFFX.semAnalyse:
            da2 = "语义分析完成！"
        else:
            for i in YFFX.semAnalyse:
                da2 += "语义错误" + ' ' + i + '\n'
        self.textEdit3.setPlainText(da2)

    # 中间代码生成
    def middle(self):
        try:
            da3 = ""
            for i in range(len(YFFX.quaternion)):  # 四元式
                da3 += str(i) + '   ' + str(YFFX.quaternion[i]) + '\n'
            self.textEdit3.setPlainText(da3)
        except Exception as e:
            print(f"middle 方法中发生错误：{e}")


def main():
    app = QApplication(sys.argv)
    ex = CodeEditor()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
