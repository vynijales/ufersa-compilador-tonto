import os

from ui.widgets.code_editor import CodeEditor

class FileTab:
    def __init__(self, filename, content):
        self.filename = filename
        self.display_name = os.path.basename(filename)
        self.editor = CodeEditor()
        self.editor.setText(content)
        self.tokens = []
