#!/usr/bin/python

# Copyright 2012 Digiknit Ltd (mike@digiknit.com)
# Inspired by:
#     lampshade.py
#         Copyright 2010 Makerbot Industries LLC
#         (http://www.thingiverse.com/thing:7664)
#         (https://github.com/makerbot/Makerbot/tree/master/scripts/lampshade)

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

# Usage example
# ./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./globe.png --output ./c_globe.bfb --zsmooth globe

import argparse
import math
import sys
import Image
import ConfigParser

# Constants
raft_margin = 5.00  # Margin in mm to increase raft radius beyond object boundary
max_bottom  = 10    # Maximum number of bottomLayers

def init():
    global layer, layerCount, rDeltaPerLayer, anglePerSegment, prefix, suffix
    
    getConfigFromArgs()
    getConfigFromFile()
    
    validateInputs()
    
    prefix = getGcodeFromFile(args.fh_prefix)
    suffix = getGcodeFromFile(args.fh_suffix)
    getImagePixels()

    layerCount = args.heightMm / printer_layer_height
    anglePerSegment = 2*math.pi/segments

def getConfigFromArgs():
    global args
    
    parser = argparse.ArgumentParser(description="""
        Programatically generate Gcode for an embossed object using a supplied image to modulate the
        amount of plastic extruded at each location.
    """)
    
    subparsers = parser.add_subparsers(dest='object_type')
    
    parser_cylinder = subparsers.add_parser('cylinder')
    parser_cone     = subparsers.add_parser('cone')
    parser_globe    = subparsers.add_parser('globe')
    
    parser.add_argument("-i", "--image",  dest="fh_image",  required=True, type=argparse.FileType('r') )
    parser.add_argument("-c", "--config", dest="fh_config", required=True, type=argparse.FileType('r') )
    parser.add_argument("-p", "--prefix", dest="fh_prefix", required=True, type=argparse.FileType('r') )
    parser.add_argument("-s", "--suffix", dest="fh_suffix", required=True, type=argparse.FileType('r') )
    
    parser.add_argument("-o", "--output", dest="fh_output", default=None, nargs='?', type=argparse.FileType('w') )
    
    parser.add_argument("-H", "--height", type=float, dest="heightMm", help="set the height of the object in mm", default=40)
    parser.add_argument("-z", "--zsmooth", action="store_true",dest="continuous", help="use continuous Z movement", default=False)
    parser.add_argument("-l", "--bottomLayers",type=int, help="number of layers in the floor")    
    parser.add_argument("-e", "--embossFactor", type=float, help="minumum ratio of embossing feed rate over normal feed rate", default=0.40)
    
    parser.add_argument("-v", "--verbose", action="count",dest="verbose", help="set verbosity -v -vv -vvv etc", default=0)
    
    parser_cylinder.add_argument("-r", "--radius", type=float, dest="radius", help="set the radius of a right cylinder in mm", default=25)
    
    parser_cone.add_argument(      "--rtop", type=float, dest="rTopMm",  help="set the top radius of a cone in mm", default=10.0)
    parser_cone.add_argument(      "--rbot", type=float, dest="rBottomMm", help="set the bottom radius of a cone in mm", default=25.0)
    
    parser_globe.add_argument("-r", "--radius", type=float, dest="radius", help="set the radius of a truncated globe in mm", default=25)
    
    try:
        args = parser.parse_args()
    except IOError, msg:
        parser.exit(str(msg))
    
    if args.fh_output != None:
        sys.stdout = args.fh_output
    
def getConfigFromFile():
    global comment_manufacturer,       comment_model,              comment_material
    global printer_base_feed_rate,     printer_base_move_rate,     printer_base_flow_rate
    global printer_layer_height,       printer_extrusion_width,     printer_max_height
    global printer_max_radius,         printer_max_overhang
    global gcode_flow_cmd,             gcode_start_cmd,            gcode_stop_cmd
    global raft_base_feed_multiplier,  raft_base_flow_multiplier,  raft_base_cruise_height
    global raft_iface_feed_multiplier, raft_iface_flow_multiplier, raft_iface_cruise_height

    # Example config file:
    #
    # [Comments]
    # printer_manufacturer = Bits from Bytes Ltd
    # printer_model = BfB3000
    # extruded_material = ABS
    # 
    # [Printer]
    # feed_rate = 960
    # move_rate = 30000
    # flow_rate = 200
    # extrusion_width = 0.5
    # 
    # [Gcode]
    # gcode_flow = M108
    # gcode_start = M101
    # gcode_stop = M103
    # 
    # [Raft_Base]
    # feed_multiplier = 0.75
    # flow_multiplier = 3.00
    # cruise_height = 0.7
    # 
    # [Raft_Interface]
    # feed_multiplier = 1.00
    # flow_multiplier = 1.50
    # cruise_height = 1.0
    # 
    
    config = ConfigParser.SafeConfigParser()
    
    config.readfp(args.fh_config)
    
    comment_manufacturer        = config.get('Comments', 'Printer_Manufacturer')
    comment_model               = config.get('Comments', 'Printer_Model')
    comment_material            = config.get('Comments', 'Extruded_Material')
    
    printer_base_feed_rate      = config.getfloat('Printer', 'feed_rate')
    printer_base_move_rate      = config.getfloat('Printer', 'move_rate')
    printer_base_flow_rate      = config.getfloat('Printer', 'flow_rate')
    printer_layer_height        = config.getfloat('Printer', 'layer_height')
    printer_extrusion_width     = config.getfloat('Printer', 'extrusion_width')
    printer_max_height          = config.getfloat('Printer', 'max_height')
    printer_max_radius          = config.getfloat('Printer', 'max_radius')
    printer_max_overhang        = config.getfloat('Printer', 'max_overhang')
    
    gcode_flow_cmd              = config.get('Gcode', 'gcode_flow')
    gcode_start_cmd             = config.get('Gcode', 'gcode_start')
    gcode_stop_cmd              = config.get('Gcode', 'gcode_stop')
    
    raft_base_feed_multiplier   = config.getfloat('Raft_Base', 'feed_multiplier')
    raft_base_flow_multiplier   = config.getfloat('Raft_Base', 'flow_multiplier')
    raft_base_cruise_height     = config.getfloat('Raft_Base', 'cruise_height')
    
    raft_iface_feed_multiplier  = config.getfloat('Raft_Interface', 'feed_multiplier')
    raft_iface_flow_multiplier  = config.getfloat('Raft_Interface', 'flow_multiplier')
    raft_iface_cruise_height    =  config.getfloat('Raft_Interface', 'cruise_height')
    
    if args.verbose > 0:
        print >> sys.stderr, "Comments:"
        print >> sys.stderr, "          Manufacturer: " + comment_manufacturer
        print >> sys.stderr, "         Printer model: " + comment_model
        print >> sys.stderr, "     Extruded material: " + comment_material
        print >> sys.stderr, "Printer:"
        
        print >> sys.stderr, "        Base Feed Rate: %.2f" % ( printer_base_feed_rate )
        print >> sys.stderr, "        Base Move Rate: %.2f" % ( printer_base_move_rate )
        print >> sys.stderr, "        Base Flow Rate: %.2f" % ( printer_base_flow_rate )
        print >> sys.stderr, "       Extrusion Width: %.2f" % ( printer_extrusion_width )
        print >> sys.stderr, "            Max Height: %.2f" % ( printer_max_height )
        print >> sys.stderr, "            Max Radius: %.2f" % ( printer_max_radius )
        print >> sys.stderr, "          Min Overhang: %.2f" % ( printer_max_overhang )
        print >> sys.stderr, "Gcode:"
        print >> sys.stderr, "        Set Flow Speed: " + gcode_flow_cmd
        print >> sys.stderr, "        Start Extruder: " + gcode_start_cmd
        print >> sys.stderr, "         Stop Extruder: " + gcode_stop_cmd
        print >> sys.stderr, "Raft Base:"
        print >> sys.stderr, "       Feed Multiplier: %.2f\t(%.2f)" % ( raft_base_feed_multiplier, printer_base_feed_rate * raft_base_feed_multiplier)
        print >> sys.stderr, "       Flow Multiplier: %.2f\t(%.2f)" % ( raft_base_flow_multiplier, printer_base_feed_rate * raft_base_flow_multiplier)
        print >> sys.stderr, "         Cruise Height: %.2f" % ( raft_base_cruise_height)
        print >> sys.stderr, "Raft interface:"
        print >> sys.stderr, "       Feed Multiplier: %.2f\t(%.2f)" % ( raft_iface_feed_multiplier, printer_base_feed_rate * raft_iface_feed_multiplier)
        print >> sys.stderr, "       Flow Multiplier: %.2f\t(%.2f)" % ( raft_iface_flow_multiplier, printer_base_feed_rate * raft_iface_flow_multiplier)
        print >> sys.stderr, "         Cruise Height: %.2f" % ( raft_iface_cruise_height )

def validateInputs():
    global base_radius
    if args.heightMm <= 0:
        print "Aborted."
        print "If specified, object height(%.2f) must be greater than zero." % ( args.heightMm )
        exit(1)
    elif args.heightMm > printer_max_height:
        print "Aborted."
        print "If specified, object height(%.2f) must be no more than %.2f." % ( args.heightMm, printer_max_height )
        exit(1)
    
    if (args.bottomLayers == None):
        args.bottomLayers = 0;
    elif (args.bottomLayers <= 0 ):
        print "Aborted."
        print "If specified, bottomLayers (%d) must be greater than zero." % ( args.bottomLayers )
        exit(1)
    elif (args.bottomLayers > max_bottom ):
        print "Aborted."
        print "If specified, bottomLayers (%d) must be no more than %d." % ( args.bottomLayers, max_bottom )
        exit(1)

    if ( args.embossFactor < 0.25 ) or ( args.embossFactor > 1.00 ):
        print "Aborted."
        print "If specified, embossFactor (%.2f) must be between 0.25 and 1.00." % ( args.embossFactor )
        exit(1)
    
    if args.object_type == 'cylinder':
        base_radius = args.radius
        
        if ( args.radius < 5.00 ) or ( args.radius > printer_max_radius ):
            print "Aborted."
            print "If specified, radius (%.2f) must be between 5.00 and %.2f." % ( args.radius, printer_max_radius )
            exit(1)
    
    elif args.object_type == 'cone':
        base_radius = args.rBottomMm
        
        if ( args.rBottomMm < 5.00 ) or ( args.rBottomMm > printer_max_radius ):
            print "Aborted."
            print "If specified, rbot (%.2f) must be between 5.00 and %.2f." % ( args.rBottomMm, printer_max_radius )
            exit(1)
        
        if ( args.rTopMm < 5.00 ) or ( args.rTopMm > printer_max_radius ):
            print "Aborted."
            print "If specified, rtop (%.2f) must be between 5.00 and %.2f." % ( args.rTopMm, printer_max_radius )
            exit(1)
        
        if ( args.rTopMm >= args.rBottomMm ):
            print "Aborted."
            print "If specified, rtop (%.2f) must be less than rbot." % ( args.rTopMm )
            exit(1)
            
        if ( args.heightMm / ( args.rBottomMm - args.rTopMm ) ) < math.tan(math.radians(printer_max_overhang)):
            print "Aborted."
            print "As given, height, rtop, rbot creates an overhang angle (%.2f) less than the minimum (%.2f)" % ( math.degrees( math.atan(args.heightMm / ( args.rBottomMm - args.rTopMm ))), printer_max_overhang )
            exit(1)
        
        
    elif args.object_type == 'globe':
        base_radius = args.radius
        
        if ( args.radius <= 5.00 ) or ( args.radius > 50.00 ):
            print "Aborted."
            print "If specified, radius (%.2f) must be between 5.00 and 50.00." % ( args.radius )
            exit(1)
        
        if ( ( args.heightMm / 2 ) > 0.8 * args.radius ):
            
            print "Aborted."
            print "Globe height(%.2f) is too large relative to the selected radius(%.2f)." % ( args.heightMm, args.radius )
            print "Extreme overhangs will not print."
            print "Maximum height for this radius is: (%.2f)." % ( args.radius * 1.6 )
            
            exit(1)
            
def getGcodeFromFile(filehandle):
    if filehandle is None:
        code=""
    else:
        code = filehandle.read().splitlines()
        filehandle.close()
    return code

def makeRaft():
    "Generate a raft"
    
    if raft_base_cruise_height > 0:
        z = raft_base_cruise_height
        
        print "%s S%.2f" % ( gcode_flow_cmd, printer_base_flow_rate * raft_base_flow_multiplier )
        
        points = makeRaftPoints( base_radius + raft_margin )
        
        p = points[0]
        print "G1 X%.2f Y%.2f Z%.2f F%.1f" % ( p[0],p[1],z,printer_base_move_rate )
        
        print "%s" % ( gcode_start_cmd )
        
        for p in points[1:]:
            print "G1 X%.2f Y%.2f Z%.2f F%.1f" % (p[0],p[1],z,printer_base_feed_rate * raft_base_feed_multiplier)
            
        print "%s" % ( gcode_stop_cmd )
    
    if raft_iface_cruise_height > 0:
        z = raft_iface_cruise_height
        
        print "%s S%.2f" % ( gcode_flow_cmd, printer_base_flow_rate * raft_iface_flow_multiplier )
        
        points = makeRaftPoints( base_radius + raft_margin )
        
        p = points[0]
        print "G1 X%.2f Y%.2f Z%.2f F%.1f" % ( p[1],p[0],z,printer_base_move_rate )
        
        print "%s" % ( gcode_start_cmd )
        
        for p in points[1:]:
            print "G1 X%.2f Y%.2f Z%.2f F%.1f" % (p[1],p[0],z,printer_base_feed_rate * raft_iface_feed_multiplier)
            
        print "%s" % ( gcode_stop_cmd )

def makeRaftPoints(radius):
    "Returns an array of points defining a circular raft layer"
    
    points = [( -radius, 0 )]
    
    x = -radius
    y = 0
    
    # FIXME - should be able to set the coarseness of the raft
    
    incr = ( 2 * radius ) / ( ( 2 * radius ) // ( 4 * printer_extrusion_width ) + 1 )
    
    direction=1
    
    while x <= radius:
        
        x = x + incr
        y = math.sqrt( abs (radius**2 - x**2 ) )
        
        points.append( ( x,  y * direction ) )
        points.append( ( x, -y * direction ) )
        
        direction = direction * -1

    return points

def makeBase():
    if args.bottomLayers > 0:
        print "(Base)"
        for i in range( 1, args.bottomLayers + 1 ):
            makeBaseLayer(i)

def makeBaseLayer(layer):
    "Generate a spiral base layer"

    z = raft_iface_cruise_height + printer_layer_height * ( layer )
    
    points = makeSpiralPoints( base_radius + printer_extrusion_width)
    
    if (layer % 2) == 0:
        points.reverse()
        p = points[0]
        print "G1 X%.2f Y%.2f Z%.2f F%.1f" % ( p[0], p[1], z, printer_base_move_rate )
        
        print "%s" % ( gcode_start_cmd )
    
        for p in points[1:]:
            print "G1 X%.2f Y%.2f Z%.2f F%.1f" % ( p[0], p[1], z, printer_base_feed_rate )
    else:    
        p = points[0]
        print "G1 X%.2f Y%.2f Z%.2f F%.1f" % ( p[0], -p[1], z, printer_base_move_rate )
        
        print "%s" % ( gcode_start_cmd )
    
        for p in points[1:]:
            print "G1 X%.2f Y%.2f Z%.2f F%.1f" % ( p[0], -p[1], z, printer_base_feed_rate )
       
    print "%s" % ( gcode_stop_cmd )

def makeSpiralPoints(radius):
    "Returns an array of points defining a spiral from the inside out"
    global extrusionWidth
    segmentLen = 2.0
    last = (0,0)
    points = [last]
    theta = math.pi/2
    r = theta * printer_extrusion_width / (2*math.pi)
    while r <= radius:
        points.append( (r*math.cos(theta), r*math.sin(theta)) )
        tDelta = math.atan( segmentLen / r )
        theta = theta + tDelta
        r = theta * printer_extrusion_width / (2*math.pi)
    return points

def getImagePixels():
    global im, pixels, segments
    im = Image.open(args.fh_image).convert("L")
    pixels = im.load()
    segments = max(20,im.size[0])

def getPixelValue( layer, segment ):
    # Luminance values from 0.00 (black, slow feed rate) to 1.00 (white, normal feed rate) are returned
    x = segment
    y = ( im.size[1] - int( float( im.size[1] * layer ) / layerCount ) ) - 1
    return ( pixels[x,y] / 256.0 )

def makeShape():
    print "(%s start)" % ( args.object_type.capitalize() )
    
    pos = getShapeXYZ( 1, 0 )
    print "G1 X%.2f Y%.2f Z%.2f F%.1f" % ( pos[0], pos[1], pos[2], printer_base_move_rate )

    if args.continuous:
        # Start extruding and don't stop until all layers are done
        print "%s" % ( gcode_start_cmd )
    
    for layer in range( 1, int(layerCount) ):
        if not args.continuous:
            # Start extruding at the beginning of each layer
            print "%s" % ( gcode_start_cmd )
        
        for segment in range(1, segments):
            pos = getShapeXYZ( layer, segment )
            value = getPixelValue( layer, segment )
            
            feedrate = printer_base_feed_rate - ( printer_base_feed_rate * ( ( 1 - value ) * ( 1 - args.embossFactor ) ) )
            #
            # white pixel: value = 1.00; args.embossFactor = 0.60
            # feedrate = printer_base_feed_rate - ( printer_base_feed_rate * ( ( 1 - 1 ) * ( 1 - args.embossFactor ) ) )
            # feedrate = printer_base_feed_rate - ( printer_base_feed_rate * ( 0 * ( 1 - args.embossFactor ) ) )
            # feedrate = printer_base_feed_rate * 1.0
            #
            # grey pixel: value = 0.50; args.embossFactor = 0.60
            # feedrate = printer_base_feed_rate - ( printer_base_feed_rate * ( ( 1 - 0.5 ) * ( 1 - args.embossFactor ) ) )
            # feedrate = printer_base_feed_rate - ( printer_base_feed_rate * ( 0.5 * ( 1 - args.embossFactor ) ) )
            # feedrate = printer_base_feed_rate - ( printer_base_feed_rate * ( 0.5 * 0.4 ) )
            # feedrate = printer_base_feed_rate - ( printer_base_feed_rate * ( 0.2 ) )
            # feedrate = printer_base_feed_rate * 0.8
            #
            # black pixel: value = 0.00; args.embossFactor = 0.60
            # feedrate = printer_base_feed_rate - ( printer_base_feed_rate * ( ( 1 - 0.0 ) * ( 1 - args.embossFactor ) ) )
            # feedrate = printer_base_feed_rate - ( printer_base_feed_rate * ( 1 - args.embossFactor ) )
            # feedrate = printer_base_feed_rate - ( printer_base_feed_rate * 0.4 )
            # feedrate = printer_base_feed_rate * 0.6
             
            print "G1 X%.2f Y%.2f Z%.2f F%.1f" % ( pos[0], pos[1], pos[2], feedrate )
            
        if not args.continuous:
            # Stop extruding at the end of each layer
            print "%s" % ( gcode_stop_cmd )
        
        pos = getShapeXYZ( layer + 1, 0 )
        if args.continuous:
            value = getPixelValue( layer, segment )
            feedrate = printer_base_feed_rate * ( 1 - ( ( 1 - args.embossFactor ) * value ) )
            
            print "G1 X%.2f Y%.2f Z%.2f F%.1f" % ( pos[0], pos[1], pos[2], feedrate )
        else:
            print "G1 X%.2f Y%.2f Z%.2f F%.1f" % ( pos[0], pos[1], pos[2], printer_base_move_rate )
        
    if args.continuous:
        # Stop extruding only once all layers are done
        print "%s" % ( gcode_stop_cmd )

    print "(%s end)" % ( args.object_type.capitalize() )

def getShapeXYZ( layer, segment ):
    angle = anglePerSegment * segment

    z = raft_iface_cruise_height + ( layer + args.bottomLayers ) * printer_layer_height
    if args.continuous:
        z = z + (printer_layer_height * (float(segment)/segments))
    
    if args.object_type   == 'cylinder':
        r = args.radius
    
    elif args.object_type == 'cone':
        r = args.rBottomMm - ( ( args.rBottomMm - args.rTopMm ) * ( layer / layerCount ) )
    
    elif args.object_type == 'globe':
        layerH = ( ( layer / layerCount ) * args.heightMm ) - ( args.heightMm / 2 );
        r = math.sqrt( abs ( math.pow( args.radius, 2 ) - math.pow( layerH, 2 ) ) );
    
    x = -math.sin(angle) * r
    y = math.cos(angle) * r
    
    return ( x, y, z )

init()

for line in prefix:
    print line
        
if ( raft_base_cruise_height > 0 ) or ( raft_iface_cruise_height > 0 ):
    makeRaft()
    
makeBase()

makeShape()

for line in suffix:
    print line