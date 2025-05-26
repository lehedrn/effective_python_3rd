# reorder_dialog.py
import reorder_app
import logging
logger = logging.getLogger(__name__)

class Dialog:
    def __init__(self, save_dir):
        self.save_dir = save_dir

save_dialog = Dialog(reorder_app.prefs.get("save_dir"))

def show():
    logger.info("Dialog shown with save_dir: %s", save_dialog.save_dir)
