# dynamic_app.py
import dynamic_dialog

class Prefs:
    def get(self, name):
        return "/default/path"

prefs = Prefs()
dynamic_dialog.show()
