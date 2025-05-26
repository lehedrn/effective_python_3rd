# configure_dialog.py
import logging
logger = logging.getLogger(__name__)

class Dialog:
    def __init__(self):
        self.save_dir = None

    def show(self):
        logger.info("Dialog shown with save_dir: %s", self.save_dir)

save_dialog = Dialog()

def configure():
    from configure_app import prefs
    save_dialog.save_dir = prefs.get("save_dir")
