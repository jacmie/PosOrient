# ![icon](src/resources/icon.png) PosOrient
KiCad plugin for positioning and orientation of footprints

## Features

- [x] get footprints position and orientation
- [x] work interactively, drag footprints and update data table
- [x] set new position, orientation and update PCB editor
- [x] save/open position, orientation configuration files
- [x] check log for changes
- [x] GUI highlighting and tooltips

![posOrient](images/posOrient.gif)

## Installation

Download release package from github on your local drive.
Open KiCad and the `Plugin and Content Manager`.
Click button `Install from File ...` and select the plugin zip package.
That's it, it's done!

The plugin should be available in the toolbar under the `PosOrient` icon: ![small_icon](src/plugins/icon.png)
or selecting in the menu: `Tools -> External Plugins`

## Use from KiCad

Create schematic with assigned footprints to the symbols. Open `PCB Editor` and `Update PCB from Schematic`.
You can provide the footprints to the `PCB Editor` by any possible means.

Run the plugin from the toolbar, or menu. If the `PCB editor` contains footprints the dialog window of the plugin will fill the data table. You can save and make backup of the data at any time. Drag the footprints in the main window with mouse, it's not necessary to close the plugin's dialog. Update new footprints positions in the data table with the `List` button. Change position and orientation in the data table. Changed cells are marked with yellow color. To make changes take effect press the `Orient` button, yellow marking will be cleared. Use spread sheet, or any other useful tool to manipulate the saved data and read it back to the data table. Got lost what you did? Follow the log, or just read in the backup. It's simple as that!