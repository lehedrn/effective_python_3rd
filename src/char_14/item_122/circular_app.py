# circular_app.py
import circular_dialog

class Prefs:
    def get(self, name):
        return "/default/path"

prefs = Prefs()
circular_dialog.show()
