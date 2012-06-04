# These files provide a (hopefully portable) way to generate embossed 3D printed objects.
# They were developed for the Bits from Bytes BfB3000 printer, but judicious editing of new
# copies of the config, prefix and suffix files should be all that's required to get this to
# work for other Gcode-based printers.
# 
# Copyright 2012 Digiknit Ltd (mike@digiknit.com)
#
# Inspired by:
#     lampshade.py
#         Copyright 2010 Makerbot Industries LLC
#         (http://www.thingiverse.com/thing:7664)
#         (https://github.com/makerbot/Makerbot/tree/master/scripts/lampshade)
#
# GNU Copyleft Statement
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# File manifest:
#     README.txt
#         This file!
# 
# Python script:
#     emboss.py
#         Use to generate the Gcode output files for the desired embossed object (Expects Python 2.7.x)
# 
# Test suite:
#     test_suite.sh
#         A Bash script to exercise the various options and test the parameter validation code
#         Also this generates a small selection of example output files.
# 
# Config files:
#     BfB3000_config.txt
#         Configuration parameters for a Bits from Bytes BfB3000 printer. Duplicate and edit for your machine.
#     BfB3000_prefix.txt
#         Initialise extruder/bed position, warm up (for ABS!), nozzle wipe routines prior to extrusion. Duplicate and edit for your machine.
#     BfB3000_suffix.txt
#         Home the extruder, cool down and lower the bed commands. Duplicate and edit for your machine.
# 
# Images
#     bfblogo.png
#         Version of the BfB logo (best for globe objects
#     globe.png
#         Earth projection (best for globe objects
# 
# Output objects:
#     b2_cylinder.bfb
#     c_cone.bfb
#     c_cylinder.bfb
#     c_globe.bfb
# 

# Config file format
#
# [Comments]
# printer_manufacturer = Bits from Bytes Ltd    (string, just for your reference)
# printer_model = BfB3000                       (string, just for your reference)
# extruded_material = ABS                       (string, just for your reference)
# 
# [Printer]
# feed_rate = 960                               (float, this is the 'regular' feed rate for your printer/material/layer thickness)
# move_rate = 30000                             (float, this is the feed rate when NOT extruding)
# flow_rate = 200                               (float, this is the value given to the extruder to get the filament flowing)
# layer_height = 0.25                           (float. in mm)
# extrusion_width = 0.5                         (float, in mm is the 'regular' bead width for your printer/material/layer thickness)
# max_height = 200.0                            (float, in mm. The maximum height of a printed object for your printer, excluding raft)
# max_radius = 100.0                            (float, in mm. The maximum radius (approx half the width / depth) of your printer's bed)
# max_overhang = 50.0                           (float, in degrees. The smallest acute overhang angle your printer can produce without drooping)
# 
# [Gcode]
# gcode_flow = M108                             (string, the gcode command to set the extruder flow rate. Flow value is appended as the 'S' parameter)
# gcode_start = M101                            (string, the gcode command to start the extruder)
# gcode_stop = M103                             (string, the gcode command to start the extruder)
# 
# [Raft_Base]
# feed_multiplier = 0.75                        (float, multiplied with the 'base' feed rate to get the effective feed rate for the bottom layer of the raft)
# flow_multiplier = 3.00                        (float, multiplied with the 'base' flow rate to get the effective flow rate for the bottom layer of the raft)
# cruise_height = 0.7                           (float, in mm. Sets the height of the extruder above the bed for the bottom raft layer)
# 
# [Raft_Interface]
# feed_multiplier = 1.00                        (float, multiplied with the 'base' feed rate to get the effective feed rate for the top layer of the raft)
# flow_multiplier = 1.50                        (float, multiplied with the 'base' flow rate to get the effective flow rate for the top layer of the raft)
# cruise_height = 1.0                           (float, in mm. Sets the height of the extruder above the bed for the top raft layer)
#
# Usage:
#        emboss.py [-h] -i FH_IMAGE -c FH_CONFIG -p FH_PREFIX -s FH_SUFFIX
#                  [-o [FH_OUTPUT]] [-H HEIGHTMM] [-z] [-l BOTTOMLAYERS]
#                  [-e EMBOSSFACTOR] [-v]
#                  {cylinder,cone,globe} ...
# 
# Programatically generate Gcode for an embossed object using a supplied image
# to modulate the amount of plastic extruded at each location.
# 
# positional arguments:
#   {cylinder,cone,globe}
# 
# optional arguments:
#   -h, --help            show this help message and exit
#   -i FH_IMAGE, --image FH_IMAGE
#   -c FH_CONFIG, --config FH_CONFIG
#   -p FH_PREFIX, --prefix FH_PREFIX
#   -s FH_SUFFIX, --suffix FH_SUFFIX
#   -o [FH_OUTPUT], --output [FH_OUTPUT]
#   -H HEIGHTMM, --height HEIGHTMM
#                         set the height of the object in mm
#   -z, --zsmooth         use continuous Z movement
#   -l BOTTOMLAYERS, --bottomLayers BOTTOMLAYERS
#                         number of layers in the floor
#   -e EMBOSSFACTOR, --embossFactor EMBOSSFACTOR
#                         minumum ratio of embossing feed rate over normal feed
#                         rate
#   -v, --verbose         set verbosity -v -vv -vvv etc
# 
# Usage example
# ./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./globe.png --output ./c_globe.bfb --zsmooth globe