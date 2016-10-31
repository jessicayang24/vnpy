# encoding: UTF-8

import sys
import ctypes
import platform

from vtEngine import MainEngine
from ctaAlgo.uiStrategyWindow import *

#----------------------------------------------------------------------
def main():
    """主程序入口"""
    # 设置底部任务栏图标，win7以下请注释掉
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('vn.py demo')
    except:
        pass

    # 重载sys模块，设置默认字符串编码方式为utf8
    reload(sys)
    sys.setdefaultencoding('utf8')

    # # 设置Windows底部任务栏图标
    # if 'Windows' in platform.uname() :
    #     ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('vn.trader')

    # 初始化Qt应用对象
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('vnpy.ico'))
    app.setFont(BASIC_FONT)
    
    # 设置Qt的皮肤
    try:
        f = file("VT_setting.json")
        setting = json.load(f)    
        if setting['darkStyle']:
            import qdarkstyle
            app.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))
    except:
        pass
    
    # 初始化主引擎和主窗口对象
    mainEngine = MainEngine()
    mainWindow = MainWindow(mainEngine, mainEngine.eventEngine)
    mainWindow.showMaximized()
    
    # 在主线程中启动Qt事件循环
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
