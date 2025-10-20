from PyQt5 import QtWidgets, QtCore
import sys, os

class CloseableTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None, close_callback=None):
        super(CloseableTabWidget, self).__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        self.close_callback = close_callback  # Callback opcional

    def closeTab(self, currentIndex):
        if self.close_callback:
            self.close_callback(currentIndex)
        else:
            currentQWidget = self.widget(currentIndex)
            currentQWidget.deleteLater()
            self.removeTab(currentIndex)
