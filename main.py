from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout
import sys
import importlib

from widgets.hierarchy import Hierarchy
from widgets.inspector import Inspector
from widgets.view import View
from data.database import Database

class Editor(QWidget):
    def __init__(self):
        super().__init__()
        innerLayout = QHBoxLayout(self)

        data = Database()

        hierarchy = Hierarchy(data)
        view = View(data)
        inspector = Inspector(data)

        innerLayout.addWidget(hierarchy)
        innerLayout.addWidget(view)
        innerLayout.addWidget(inspector)

if __name__ == "__main__":
    # Check for needed libraries
    if importlib.util.find_spec("PySide2") is None:
        print("This application requires the PySide2 library. Consider installing it with pip")
        exit(1)

    app = QApplication(sys.argv)

    editor = Editor()
    editor.show()

    sys.exit(app.exec_())
