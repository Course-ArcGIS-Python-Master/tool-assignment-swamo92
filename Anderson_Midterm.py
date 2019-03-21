# Running this script will delineate a watershed for 3 outlet points in Rhode Island and clip lakes for that watershed.
# Before running this script, create two folders one that has the Digital Elevation Model (DEM) and lakes shapefile for
# Rhode Island and one that contains the outlet point shapefiles. Lines 10, 15, and 30 need to be set to the path directories
# of these folders.

# Import the system modules
import arcpy, os

# Set the working directory, environment, scratch workspace, and turn on spatial analyst
input_workspace = "S:\Gold_Lab\Seaver\Python\Midterm\Data" ### Set this to where your Digital Elevation Model and Lakes data live.
arcpy.env.workspace = input_workspace
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True # This will overwrite previous outputs if the script is run multiple times.

scratch_directory = "S:\Gold_Lab\Seaver\Python\Midterm\scratch2" ### Set your scratch folder, this will be deleted later on.
if not os.path.exists(scratch_directory):
     os.mkdir(scratch_directory)

# Set variables for our input files
DEM = r"dem_spf"
Lakes = r"lakes5k10.shp"

# Use the Fill tool to "fill" the Digital Elevation Model (DEM)
DEM_Fill = arcpy.gp.Fill_sa(DEM, scratch_directory + "\Fill" "")

# Create flow direction model from the filled DEM
Flow_Direction = arcpy.gp.FlowDirection_sa(DEM_Fill, scratch_directory + "\Flow_dir", "NORMAL", "", "D8")

# Now we can delineate watersheds for the desired outlet points.
arcpy.env.workspace = "S:\Gold_Lab\Seaver\Python\Midterm\Data\Outlet Points" ### Set directory to where Outlet points live!!!

input_points = arcpy.ListFeatureClasses("*", "Point")
print "Watersheds will be delineated for... " + str(input_points)

for pond in input_points:
    if "Cross" in pond:
         arcpy.gp.Watershed_sa(Flow_Direction, pond, scratch_directory + "\CR_Wshed", "")
    if "Potter" in pond:
         arcpy.gp.Watershed_sa(Flow_Direction, pond, scratch_directory + "\PH_Wshed", "")
    if "Woonsocket" in pond:
         arcpy.gp.Watershed_sa(Flow_Direction, pond, scratch_directory + "\WS_Wshed", "")

# Convert delineated watersheds to polygon shapefiles.
arcpy.env.workspace = scratch_directory
watersheds = arcpy.ListRasters("*", "GRID")
print "converting watershed rasters to polygons..."

for basin in watersheds:
    if "cr_" in basin:
        arcpy.RasterToPolygon_conversion(in_raster=basin, out_polygon_features=input_workspace + "\CrossMills",
                                   simplify="SIMPLIFY", raster_field="VALUE", create_multipart_features="SINGLE_OUTER_PART",
                                   max_vertices_per_feature="")
    if "ph_" in basin:
        arcpy.RasterToPolygon_conversion(in_raster=basin, out_polygon_features=input_workspace + "\PotterHill",
                                          simplify="SIMPLIFY", raster_field="VALUE",
                                          create_multipart_features="SINGLE_OUTER_PART",
                                          max_vertices_per_feature="")
    if "ws_" in basin:
        arcpy.RasterToPolygon_conversion(in_raster=basin, out_polygon_features=input_workspace + "\Woonsocket",
                                         simplify="SIMPLIFY", raster_field="VALUE",
                                         create_multipart_features="SINGLE_OUTER_PART",
                                         max_vertices_per_feature="")

# Now we can clip lakes to the watersheds.

arcpy.env.workspace = input_workspace
polygon_list = arcpy.ListFeatureClasses("*", "Polygon")
print "Clipping lakes to watersheds..."

for polygon in polygon_list:
    if "CrossMills" in polygon:
        arcpy.Clip_analysis(Lakes, polygon, "CM_Lakes", "")
    if "PotterHill" in polygon:
        arcpy.Clip_analysis(Lakes, polygon, "PH_Lakes", "")
    if "Woonsocket" in polygon:
        arcpy.Clip_analysis(Lakes, polygon, "WO_Lakes", "")

# Last we delete the scratch output folder.

arcpy.Delete_management(os.path.join(scratch_directory))