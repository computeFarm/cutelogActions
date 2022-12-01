# This file has been altered from the `__main__.py` file in the original
# commit c6f8681 of https://github.com/busimus/cutelog repository on
# 2022-11-07.
#
# It is used under the original repository's MIT license.
#

import json
import os
import qtpy
import subprocess
import sys

if not qtpy.PYQT5 and not qtpy.PYSIDE2:
    if sys.platform == 'linux':
        sys.exit("Error: a compatible Qt library couldn't be imported.\n"
                 "Please install python3-pyqt5 (or just python-pyqt5) from your package manager.")
    else:  # this technically shouldn't ever happen
        sys.exit("Error: a compatible Qt library couldn't be imported.\n"
                 "Please install it by running `pip install pyqt5")

baseDir = os.getcwd()

try :
  configPath = os.path.join(
  os.path.expanduser('~'),
    '.config',
    'cutelogActions',
    'config.json'
  )
  with open(configPath, 'r') as configFile :
    config = json.loads(configFile.read())
except Exception as err:
  print(repr(err))
  config = {
    'editor' : 'xterm -e nano +{line} {fullPath}'
  }

############################################################################
# BEGIN python monkey patch

# The following is a monkey patch taken from `logger_tab.py` file in the
# original commit c6f8681 of https://github.com/busimus/cutelog repository
# on 2022-12-01.
#
# It is used under the original repository's MIT license.
#

from functools import partial
from qtpy.QtWidgets import QMenu
import cutelog.logger_tab

def cla_open_logger_table_menu(self, position):
  # Needed as a workaround for when the header column count is 0 and it becomes invisible
  if self.table_header.column_count == 0:
    self.open_header_menu(position)
    return
  selected = self.loggerTable.selectedIndexes()
  if not selected:
    return
  row_index = selected[0]
  record = self.get_record(row_index)
  menu = QMenu(self)
  if record.file :
    editSource = menu.addAction("Edit source")
    editSource.triggered.connect(partial(self.editSource, record.dir, record.file, record.line))
  view_message = menu.addAction("View message")
  view_message.triggered.connect(partial(self.open_text_view_dialog, row_index, False))
  if record.exc_text:
    view_traceback = menu.addAction("View traceback")
    view_traceback.triggered.connect(partial(self.open_text_view_dialog, row_index, True))
  menu.popup(self.table_header_view.viewport().mapToGlobal(position))

cutelog.logger_tab.LoggerTab.open_logger_table_menu = cla_open_logger_table_menu

def editSource(self, fileDir, file, line) :
  if line    is None : line = 0
  if fileDir is None : fileDir = '.'
  fullPath = os.path.join(baseDir, fileDir, file)
  subprocess.Popen(
    config['editor'].format(
      fullPath=fullPath,
      line=line
    ),
    shell=True, stdin=None, stdout=None, stderr=None, close_fds=True
  )

cutelog.logger_tab.LoggerTab.editSource = editSource

# FINSH python monkey patch
############################################################################

def main():
    global baseDir
    import signal
    from cutelog.config import ROOT_LOG, CONFIG
    from cutelog.main_window import MainWindow
    from cutelog.resources import qCleanupResources
    from qtpy.QtGui import QIcon
    from qtpy.QtWidgets import QApplication

    try :
      baseDirIndex = sys.argv.index('--base_dir')
      baseDir = sys.argv[baseDirIndex + 1]
    except :
      pass # it is ok to ignore this

    print(f"Base dir: [{baseDir}]")

    if sys.platform == 'win32':
        import ctypes
        appid = 'busimus.cutelog'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/cutelog.png'))
    mw = MainWindow(ROOT_LOG, app)
    CONFIG.set_option('listen_host', '127.0.0.1')
    CONFIG.set_option('default_serialization_format', 'json')
    signal.signal(signal.SIGINT, mw.signal_handler)

    sys.exit(app.exec_())
    qCleanupResources()

if __name__ == '__main__':
    main()
