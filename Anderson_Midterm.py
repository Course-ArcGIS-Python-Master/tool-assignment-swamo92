# Running this script will delineate a watershed for 3 points in Rhode Island and clip land use for that watershed.
# Before Beginning create two folders one that has the Digital Elevation Model (DEM) for Rhode Island and one that
# contains the outlet point shapefiles.

# Import the system modules
import arcpy, os

# Set the working directory, and turn on spatial analyst
arcpy.env.workspace = "S:\Gold_Lab\Seaver\Python\Midterm\Data" ## Set this to where your Digital Elevation Model and Landuse polygon live.
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
#
output_directory = "S:\Gold_Lab\Seaver\Python\Midterm\output" ## Set your output folder.
if not os.path.exists(output_directory):
     os.mkdir(output_directory)

# # Set variables for our input files
DEM = r"dem_spf"
Landuse = r"rilc11d.shp"
#
# ## Use the Fill tool to "fill" the Digital Elevation Model (DEM)
DEM_Fill = arcpy.gp.Fill_sa(DEM, output_directory + "\Fill" "")

# # Create flow direction model from the filled DEM
Flow_Direction = arcpy.gp.FlowDirection_sa(DEM_Fill, output_directory + "\Flow_dir", "NORMAL", "", "D8")

# # Now we can delineate watersheds for the desired outlet points.
arcpy.env.workspace = "S:\Gold_Lab\Seaver\Python\Midterm\Data\Outlet Points" # Set directory to where Outlet points live.

input_points = arcpy.ListFeatureClasses("*", "Point")
print "Watersheds will be delineated for " + str(input_points)

for pond in input_points:
    if "Cross" in pond:
         arcpy.gp.Watershed_sa(Flow_Direction, pond, "CR_Wshed", "")
    if "Potter" in pond:
         arcpy.gp.Watershed_sa(Flow_Direction, pond, "PH_Wshed", "")
    if "Woonsocket" in pond:
         arcpy.gp.Watershed_sa(Flow_Direction, pond, "WS_Wshed", "")

# Convert delineated watersheds to polygon shapefiles.
watersheds = arcpy.ListRasters("*", "GRID")

for basin in watersheds:
    if "cr_" in basin:
        arcpy.RasterToPolygon_conversion(in_raster=basin, out_polygon_features=output_directory + "\CrossMills",
                                   simplify="SIMPLIFY", raster_field="VALUE", create_multipart_features="SINGLE_OUTER_PART",
                                   max_vertices_per_feature="")
    if "ph_" in basin:
        arcpy.RasterToPolygon_conversion(in_raster=basin, out_polygon_features=output_directory + "\PotterHill",
                                          simplify="SIMPLIFY", raster_field="VALUE",
                                          create_multipart_features="SINGLE_OUTER_PART",
                                          max_vertices_per_feature="")
    if "ws_" in basin:
        arcpy.RasterToPolygon_conversion(in_raster=basin, out_polygon_features=output_directory + "\Woonsocket",
                                         simplify="SIMPLIFY", raster_field="VALUE",
                                         create_multipart_features="SINGLE_OUTER_PART",
                                         max_vertices_per_feature="")

# Now we can clip landuse to the watersheds.

arcpy.env.workspace = output_directory
polygon_list = arcpy.ListFeatureClasses("*", "Polygon")

for polygon in polygon_list:
    if "Cross" in polygon:
        arcpy.Clip_analysis(Landuse, polygon, "CM_Landuse", "")
    if "Potter" in polygon:
        arcpy.Clip_analysis(Landuse, polygon, "PH_Landuse", "")
    if "Woonsocket" in polygon:
        arcpy.Clip_analysis(Landuse, polygon, "WO_Landuse", "")
