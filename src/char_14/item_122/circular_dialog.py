# circular_dialog.py
import circular_app

class Dialog:
    def __init__(self, save_dir):
        self.save_dir = save_dir

save_dialog = Dialog(circular_app.prefs.get("save_dir"))

def show():
    print("Showing the dialog!")
