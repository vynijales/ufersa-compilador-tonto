import os

from ui.widgets.code_editor import CodeEditor
from ui.widgets.graph_viewer.graph_viewer import GraphViewer


class GenericTab:
    def __init__(self, title, widget, content):
        self.filename = title
        self.display_name = os.path.basename(title)
        self.editor = widget
        self.editor.setText(content)
        self.tokens = []
        self.errors = []


class FileTab(GenericTab):
    def __init__(self, title, content):
        super().__init__(title, CodeEditor(), content)


class GraphTab(GenericTab):
    def __init__(self, title, content):
        super().__init__(title, GraphViewer(), content)
