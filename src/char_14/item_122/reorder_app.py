# reorder_app.py
class Prefs:
    def get(self, name):
        return "/default/path"

prefs = Prefs()

import reorder_dialog

def show_dialog():
    reorder_dialog.show()
