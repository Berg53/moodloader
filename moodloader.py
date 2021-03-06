#! /usr/bin/python3

# ########################## Copyrights and license ##############################
#                                                                                #
# This file is part of MoodLoader. http://github.com/JamesWrigley/MoodLoader/    #
#                                                                                #
# MoodLoader is free software: you can redistribute it and/or modify it under    #
# the terms of the GNU General Public License as published by the Free Software  #
# Foundation, either version 3 of the License, or (at your option) any later     #
# version.                                                                       #
#                                                                                #
# MoodLoader is distributed in the hope that it will be useful, but WITHOUT ANY  #
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS      #
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. #
#                                                                                #
# You should have received a copy of the GNU General Public License along with   #
# MoodLoader. If not, see <http://www.gnu.org/licenses/>.                        #
#                                                                                #
# ################################################################################

import re
import os
import sys
import shutil
from PyQt4 import QtGui, QtCore
from moodloader_ui import MoodLoader

class MainWindow(MoodLoader):
    """
    Subclass the GUI for the main window. We implement '__init__()' here, and
    also set up connections for the widgets.
    """

    def __init__(self):
        ### Create some system variables ###
        self.config_dir = self.get_config_path()
        self.open_dialog_dir = os.path.expanduser("~")


        super(MoodLoader, self).__init__()
        self.initUI()

        ### Set up connections ###
        self.install_map_button.clicked.connect(lambda: self.install_mod("/maps/"))
        self.install_cam_mod_button.clicked.connect(lambda: self.install_mod("/campaign/"))
        self.install_global_mod_button.clicked.connect(lambda: self.install_mod("/global/"))

        ### Set up the QListView's
        self.populate_listviews()
#        for view in [self.map_mods_listview, self.cam_mods_listview, self.global_mods_listview]:
#            view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
#            view.connect(view, QtCore.signal("customContextMenuRequested(QPoint)"),
#                         self.listview_menu)


    def get_config_path(self):
        """
        Get the path of the config folder of the latest version of WZ on the
        users computer.
        """
        matching_dir_versions = [float(re.findall(r'\d+\.\d+', directory)[0])
                                 for directory in os.listdir(os.path.expanduser("~"))
                                 if re.match(".warzone2100-\d+\.\d+", directory)]

        if len(matching_dir_versions) >= 1:
            return(os.path.expanduser("~") + "/.warzone2100-" + str(max(matching_dir_versions)))
        else:
            self.statusbar.showMessage("No config folder found!")
            return("")


    def install_mod(self, mod_type):
        """
        Install a map to the /.warzone2100-xx/maps folder.
        Note that even the name of the argument is 'mod_type', it's actually
        the folder name the map is to be installed into (i.e. '/maps/' for a map mod).
        """
        mod_path = QtGui.QFileDialog.getOpenFileName(self, "Select Mod", self.open_dialog_dir, "WZ Mods (*.wz);; All files (*.*)")
        mod_install_path  = self.config_dir + mod_type
        mod_name = os.path.basename(mod_path)

        # Check that all cases are covered before installing
        if not mod_path:
            return
        elif not os.path.isdir(mod_install_path):
            os.mkdir(mod_install_path)
        elif os.path.isfile(mod_install_path + mod_name):
            self.statusbar.showMessage("Mod already installed!")
            return

        shutil.copy(mod_path, mod_install_path)
        self.populate_listviews()
        self.statusbar.showMessage("Map installed!")
        self.open_dialog_dir = os.path.dirname(mod_path) # Note that we reset 'self.open_dialog_dir' to the last used folder


    def condense_mod(self, mod_name):
        if len(mod_name) > 64:
            mod_name = re.findall(".*-", mod_name)[0]
            return(mod_name[:-1])
        else:
            return(mod_name.replace(".wz", ""))


    def populate_listviews(self):
        """
        Gets a list of map, campaign, and global mods, and populates their
        respective QListView's with them.
        """
        # We need this to elide the text
        mod_size = QtCore.QSize(50, 15)

        if os.path.isdir(self.config_dir + "/maps/"):
            map_mods = [mod for mod in os.listdir(self.config_dir + "/maps/")
                        if os.path.isfile(self.config_dir + "/maps/" + mod)]
            for mod in map_mods:
                mod_item = QtGui.QStandardItem(self.condense_mod(mod))
                mod_item.setSizeHint(mod_size)
                mod_item.setToolTip(mod)
                mod_item.setEditable(False)
                self.map_data_model.appendRow(mod_item)

        if os.path.isdir(self.config_dir + "/campaign"):
            cam_mods = [mod for mod in os.listdir(self.config_dir + "/campaign/")
                        if os.path.isfile(self.config_dir + "/campaign/" + mod)]
            for mod in cam_mods:
                mod_item = QtGui.QStandardItem(self.condense_mod(mod))
                mod_item.setSizeHint(mod_size)
                mod_item.setToolTip(mod)
                mod_item.setEditable(False)
                self.cam_data_model.appendRow(mod_item)

        if os.path.isdir(self.config_dir + "/global/"):
            global_mods = [mod for mod in os.listdir(self.config_dir + "/global/")
                           if os.path.isfile(self.config_dir + "/global/" + mod)]
            for mod in global_mods:
                mod_item = QtGui.QStandardItem(self.condense_mod(mod))
                mod_item.setSizeHint(mod_size)
                mod_item.setToolTip(mod)
                mod_item.setEditable(False)
                self.global_data_model.appendRow(mod_item)


    def listview_menu(self):
        """
        Called when a QListView item is right-clicked on, lets the user delete
        the selected mod.
        """
        menu = QtGui.QMenu("Options", self)
        #        menu.addAction


def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
