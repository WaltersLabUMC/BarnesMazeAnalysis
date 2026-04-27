import math
from tkinter.filedialog import asksaveasfilename, askdirectory
import os.path
from os import listdir
import pandas as pd
import numpy as np
import math
class CoordsDataset:
    def __init__(self, coord_files_dict:list, exp_days:tuple, table_size_cm:float, num_holes:int, hole_entry_zone_cm:float):
        self.coord_files_dict = coord_files_dict
        self.exp_days = exp_days
        self.table_size_cm = table_size_cm
        num_holes = num_holes
        self.hole_entry_zone_cm = hole_entry_zone_cm

        ## SET UP SKELETON FOR HOLE COORDS DATAFRAME
        hole_col_names = ["day_hole", "x_coord", "y_coord"]
        hole_col0_vals = []
        day_no = exp_days[0]
        for day_range in range(exp_days[0], exp_days[1]+1):
            for i in range(1,num_holes+1):
                hole_col0_vals.append(f"DAY{day_no}_H{i}")
            day_no+=1
        self.hole_coords = pd.DataFrame(columns = hole_col_names)
        self.hole_coords = pd.DataFrame({'day_hole': hole_col0_vals, 'x_coord': None, 'y_coord': None})

        ## SET UP SKELETON FOR TABLE COORDS DATAFRAME
        table_column_names = ["day_hole", "x_coord", "y_coord"]
        self.table_coords = pd.DataFrame(columns = table_column_names)
        row_no = 0
        day_no = exp_days[0]
        bp_list = ["TOP", "BOT", "LEFT", "RIGHT"]
        for day_range in range(exp_days[0], exp_days[1]+1):
            bp_no = 0
            for bp in range(4):
                self.table_coords.loc[row_no, "day_hole"] = f"DAY{day_no}_{bp_list[bp_no]}"
                bp_no+=1
                row_no+=1
            day_no+=1
        
        ## EMPTY DICT FOR HOLE COORD DICT
        self.hole_coords_dict = {}

        ## SET UP DICT FOR CENTER TABLE COORDS
        self.table_center_coods_dict = {}
        day_no = self.exp_days[0]
        for day_range in range(self.exp_days[0], self.exp_days[1]+1):
            self.table_center_coods_dict[f"DAY{day_no}_center_coords"] = 0
            day_no+=1

        ## SET UP SKELETON FOR REPORT
        self.coords_summary = {"px_to_cm_conversion": "", "hole_entry_zone_cm": hole_entry_zone_cm, "hole_entry_zone_px": "", "table_size_cm": table_size_cm,  "table_size_px": ""} #, "table_centers_by_day": ""}

        ## EXECUTE PROGRAM
        self.generate_summary()

    def __repr__(self):
        return str(self.coords_summary)

    def generate_summary(self):
        self.csv_to_df()
        self.center_of_table()
        self.px_to_cm()
        self.save_to_csv()
        self.print_coords_summary()

    def csv_to_df(self):
        for key, value in self.coord_files_dict.items():
            ## READ CSV AND TRANSPOSE DATA
            df = pd.read_csv(self.coord_files_dict[key]).T
            ## SET COL NAMES AS ITEMS FROM FIRST ROW; DELETE HEADER ROWS
            df.columns = df.iloc[0]
            df = df[3:]
            ## RESET INDEX
            df = df.reset_index()

            ## CHANGE "bodyparts" TO MATCH "day_hole" IN hole_coords
            df["bodyparts"] = f"{key}_" + df["bodyparts"].astype(str)

            ## SEPARATE OUT X AND Y COORDS THEN MERGE INTO CORRECT COLS IN DATAFRAMES
            ## HOLE COORDS
            df_hole_x_coords = self.get_coords(df, "holes", "x")
            self.merge_coords_to_class(df_hole_x_coords, "holes", "x")
            df_hole_y_coords = self.get_coords(df, "holes", "y")
            self.merge_coords_to_class(df_hole_y_coords, "holes", "y")
            ## TABLE COORDS
            df_table_x_coords = self.get_coords(df, "table", "x")
            self.merge_coords_to_class(df_table_x_coords, "table", "x")
            df_table_y_coords = self.get_coords(df, "table", "y")
            self.merge_coords_to_class(df_table_y_coords, "table", "y")
            
            ## ADD DICT OF CURRENT DAY COORDS TO MASTER COORD DICT
            self.make_table_coord_dict(df_hole_x_coords, df_hole_y_coords)

    def get_coords(self, df, obj_type:str, coord_type:str):
        ## "coord_type" SHOULD BE "x" OR "y"
        ## "obj_type" SHOULD BE "holes" OR "table"
        is_not_hole = df["bodyparts"].str.contains("TOP|BOT|LEFT|RIGHT")
        if obj_type == "holes":
            is_coord_type_vals = df["coords"] == coord_type
            coord_type_vals = df[is_coord_type_vals & ~is_not_hole]
            return coord_type_vals
        else:
            is_coord_type_vals = df["coords"] == coord_type
            coord_type_vals = df[is_coord_type_vals & is_not_hole]
            return coord_type_vals
        
    def make_table_coord_dict(self, x_coords, y_coords):
        coords = dict(zip(x_coords["bodyparts"], zip(x_coords["labeled-data"].astype(float).round().astype(int), y_coords["labeled-data"].astype(float).round().astype(int))))
        self.hole_coords_dict[x_coords.iloc[1,1][0:4]] = coords

    def merge_coords_to_class(self, coord_vals, obj_type:str, coord_type:str):
        ## "coord_vals" SHOULD BE YOUR FILTERED X_COORD VALS OR YOUR FILTERED Y_CORD VALS
        ## "obj_type" SHOULD BE "holes" OR "table"
        ## "coord_type" SHOULD BE "x" OR "y"
        if obj_type == "holes":
            temp_merge = pd.merge(self.hole_coords, coord_vals[['bodyparts', 'labeled-data']],
                                left_on="day_hole", right_on="bodyparts", how='left')
            self.hole_coords[f"{coord_type}_coord"] = temp_merge['labeled-data'].combine_first(self.hole_coords[f"{coord_type}_coord"])
        else:
            temp_merge = pd.merge(self.table_coords, coord_vals[['bodyparts', 'labeled-data']],
                                left_on="day_hole", right_on="bodyparts", how='left')
            self.table_coords[f"{coord_type}_coord"] = temp_merge['labeled-data'].combine_first(self.table_coords[f"{coord_type}_coord"])

    def center_of_table(self):
        c1 = 0
        c2 = 1
        c3 = 2
        c4 = 3
        dict_key = self.exp_days[0]
        for i in range(1, (len(self.table_coords)//4)+1):
            avg_x = (float(self.table_coords.loc[c1, "x_coord"]) + float(self.table_coords.loc[c2, "x_coord"]) + float(self.table_coords.loc[c3, "x_coord"]) + float(self.table_coords.loc[c4, "x_coord"])) / 4
            avg_y = (float(self.table_coords.loc[c1, "y_coord"]) + float(self.table_coords.loc[c2, "y_coord"]) + float(self.table_coords.loc[c3, "y_coord"]) + float(self.table_coords.loc[c4, "y_coord"])) / 4
            self.table_center_coods_dict[f"DAY{dict_key}_center_coords"] = (round(avg_x), round(avg_y))
            c1+=4
            c2+=4
            c3+=4
            c4+=4
            dict_key+=1
        
    def px_to_cm(self):
        all_conv_facts = []
        c1 = 0
        c2 = 1
        for i in range(1,(len(self.table_coords)//2)+1):
            coords1 = (float(self.table_coords.loc[c1, "x_coord"]), float(self.table_coords.loc[c1, "y_coord"]))
            coords2 = (float(self.table_coords.loc[c2, "x_coord"]), float(self.table_coords.loc[c2, "y_coord"]))
            px_dist = math.sqrt((coords1[0] - coords2[0])**2 + (coords1[1] - coords2[1])**2)
            all_conv_facts.append(self.table_size_cm / px_dist)
            c1+=2
            c2+=2
        avgd_conv_fact = float(np.average(all_conv_facts))
        self.coords_summary["px_to_cm_conversion"] = avgd_conv_fact
        self.coords_summary["hole_entry_zone_px"] = round((self.hole_entry_zone_cm / avgd_conv_fact), 1)
        self.coords_summary["table_size_px"] = round((self.table_size_cm / avgd_conv_fact), 1)

    def save_to_csv(self):
        self.hole_coords.to_csv("hole_coords.csv", header = False, index = False)
        self.table_coords.to_csv("table_coords.csv", header = False, index = False)
        report_df = self.create_avgs_df()
        report_df.to_csv("coord_summary_values.csv", header = True, index = True)

    def create_avgs_df(self):
        main_df = pd.DataFrame([self.coords_summary])
        table_center_df = pd.DataFrame(list(self.table_center_coods_dict.items()))
        table_center_df = table_center_df.set_index(0).T
        table_center_df.columns.name = None
        table_center_df.reset_index(drop=True, inplace=True)
        combined_df = pd.concat([main_df, table_center_df], axis =1)
        return combined_df
        
    def print_coords_summary(self):
        print(f"pixels to cm conversion factor: {self.coords_summary["px_to_cm_conversion"]}")
        print(f"A hole entry zone with a diameter of {self.coords_summary["hole_entry_zone_cm"]} cm is equivalent to a diameter of {self.coords_summary["hole_entry_zone_px"]} pixels")
        print(f"A Barnes Maze table with a diameter of {self.coords_summary["table_size_cm"]} cm is equivalent to a diameter of {self.coords_summary["table_size_px"]} pixels")
        print(f"Barnes Maze table centers by day: {self.table_center_coods_dict}")


def analyze(**kwargs):
    parameters = __parse_analyze__arguments(kwargs)
    reports = []
    dynamic_velocity_reports = []
    for path in parameters['filepaths']:
        track = __csv_file_to_track(path, parameters['x_shift'], parameters['y_shift'])
        reports.append(Report(track, parameters['rois'][__trial_to_lookup(track)], parameters['fps'], parameters['cm_per_pixel']))
        if parameters['dynamic_velocity'] is not None:
            vel_report = DynamicVelocityReport(track, parameters['dynamic_velocity'], parameters['fps'], parameters['cm_per_pixel'])
            samp_row = [val for subdict in vel_report.dynamic_vel_dict for val in vel_report.dynamic_vel_dict[subdict].values()]
            dynamic_velocity_reports.append(samp_row)
    __reports_to_csv(reports, dynamic_velocity_reports, parameters['outpath'], next(iter(parameters['rois'].values())), parameters['rounding_digits'])

def __parse_analyze__arguments(kwargs):
    folderpath = None
    filepaths = []
    outpath = None
    rois = None
    fps = 30.0
    cm_per_pixel = 0.0
    rounding_digits = -1
    x_shift = 0.0
    y_shift = 0.0
    target_hole = "H1"
    quad_centers = None 
    hole_entry_diameter = 0.0
    quad_diameter = 0.0
    day = None
    dynamic_velocity = None

    if "target_hole" in kwargs:
        target_hole = kwargs['target_hole']
    if "quad_centers" in kwargs:
        quad_centers = kwargs["quad_centers"]
        if quad_centers is not None and len(quad_centers) <= 0:
                raise IndexError("You must provide 4 valid holes to serve as quadrant centers")
    if "hole_entry_diameter" in kwargs:
        hole_entry_diameter = float(kwargs['hole_entry_diameter'])
    if "quad_diameter" in kwargs:
        quad_diameter = float(kwargs['quad_diameter'])

    if "rois" in kwargs:
        input_roi_dict = kwargs['rois']
        if input_roi_dict == None:
            raise ValueError("ROIs not provided or not in valid formatting")
        rois = __get_rois(input_roi_dict, target_hole, quad_centers, hole_entry_diameter, quad_diameter)
        if len(rois) == 0:
            raise OSError("User provided no valid circular ROIs or did not format ROI input correctly")

    if "fps" in kwargs:
        fps = float(kwargs['fps'])
        if fps <= 0.0:
            raise IndexError("Frames per second cannot be less than or equal to zero")

    if "cm_per_pixel" in kwargs:
        cm_per_pixel = float(kwargs['cm_per_pixel'])
        if cm_per_pixel <= 0.0:
            raise IndexError("Centimeters per pixel cannot be less than or equal to zero")

    if "rounding_digits" in kwargs:
        rounding_digits = int(kwargs['rounding_digits'])

    if "x_shift" in kwargs:
        x_shift = float(kwargs['x_shift'])

    if "y_shift" in kwargs:
        y_shift = float(kwargs['y_shift'])

    if "folderpath" in kwargs:
        path = kwargs["folderpath"]
        if not os.path.isdir(kwargs['folderpath']):
            raise FileNotFoundError(f"No such input directory: {kwargs['folderpath']}")
        __get_csv_files_from_directory(filepaths, path)
    else:
        folder = askdirectory(title="Select a Folder Containing .CSV Files", mustexist=True)
        if folder:
            __get_csv_files_from_directory(filepaths, folder)
        if len(filepaths) == 0:
            raise OSError("Directory contains no valid input files")

    if "outpath" in kwargs:
        if type(kwargs["outpath"]) is str:
            outpath = kwargs["outpath"]
        else:
            outpath = str(kwargs["outpath"])
    else:
        file = asksaveasfilename(filetypes=[("Comma Separated Values File", ".csv")], defaultextension=".csv")
        if file:
            outpath = file
        else:
            raise OSError("User did not provide an output path")
        
    if "dynamic_velocity" in kwargs:
        dynamic_velocity = kwargs["dynamic_velocity"]

    return {'folderpath': folderpath, 'filepaths': filepaths, 'outpath': outpath, 'rois': rois, 'fps': fps, 'cm_per_pixel': cm_per_pixel, 'rounding_digits': rounding_digits, 'x_shift': x_shift, 'y_shift': y_shift, "dynamic_velocity": dynamic_velocity }


def __get_rois(input_rois:dict, target_hole:str, quad_centers, hole_entry_diameter:float = 0.0, quad_diameter:float = 0.0):
    hole_radius = hole_entry_diameter / 2
    quad_radius = quad_diameter / 2
    rois = []

    for i in range(len(input_rois)):
        subdict_key = [key for key in input_rois.keys()][i]
        for item in input_rois[subdict_key].items():
            ids = item[0].replace("DAY", "D").split("_")
            rois.append((ids[0], ids[1], float(item[1][0]), float(item[1][1]), int(''.join(c for c in ids[1] if c.isdigit()))))
    rois.sort(key=lambda tup: tup[4])

    if quad_centers is None:
        circles = {}
        for r in rois:
            if r[0] not in circles.keys():
                circles[r[0]] = []
            circles[r[0]].append(Circle(Point(r[2], r[3]), hole_radius, r[1]))
        return circles

    if quad_centers is not None:
        Q1_center = quad_centers[0]
        Q2_center = quad_centers[1]
        Q3_center = quad_centers[2]
        Q4_center = quad_centers[3]
        qSwaps = {Q1_center: 'Quad1', Q2_center: 'Quad2', Q3_center: 'Quad3', Q4_center: 'Quad4'}
        circles = {}
        qcircles = {}

        for r in rois:
            if r[0] not in circles.keys():
                circles[r[0]] = []
            circles[r[0]].append(Circle(Point(r[2], r[3]), hole_radius, r[1]))
            if r[1] in (Q1_center, Q2_center, Q3_center, Q4_center):
                if r[0] not in qcircles.keys():
                    qcircles[r[0]] = []
                qcircles[r[0]].append(Circle(Point(r[2], r[3]), quad_radius, qSwaps[r[1]]))

        for q in qcircles:
            for c in qcircles[q]:
                circles[q].append(c)
        return circles

def __get_csv_files_from_directory(csvlist: list[str], path: str):
    for f in listdir(path):
        fullpath = os.path.join(path, f)
        if os.path.isfile(fullpath):
            if fullpath.lower().endswith(".csv"):
                if fullpath.lower().startswith("output_") == False:
                    csvlist.append(fullpath)

def __csv_file_to_track(path: str, x_shift: float=0.0, y_shift: float=0.0):
    rows = []
    with open(path, 'r') as file:
        for line in file:
            rows.append(line.strip().split(','))
    del rows[0]
    bodyparts = []
    x = 1
    while x < len(rows[0]):
        bodyparts.append(rows[0][x])
        x += 3
    del rows[0]
    del rows[0]
    track = Track()
    id_and_trial = os.path.basename(path)[0:11].split(" - ")
    track.id = id_and_trial[0]
    track.trial = id_and_trial[1]
    for row in rows:
        for i, bodypart in enumerate(bodyparts):
            track.addStop(bodypart, Point(float(row[1 + (3 * i)]) + x_shift, float(row[2 + (3 * i)]) + y_shift))
    return track

class Point():
    def __init__(self, x: float=0.0, y: float=0.0):
        self.x = x
        self.y = y

class Track():
    def __init__(self):
        self.stops: dict[str, list[Point]] = {}
        self.distanceTraveled = 0.0
        self.totalTime = 0.0
        self.id = ''
        self.trial = ''

    def addStop(self, name: str, location: Point=None):
        if name not in self.stops:
            self.stops[name] = []
        self.stops[name].append(location)

    def totalStops(self):
        return len(next(iter(self.stops.values()), None))

def __trial_to_lookup(track: Track):
    return track.trial[:2]

class Circle():
    def __init__(self, center: Point=None, radius: float=1.0, label: str="hole"):
        self.center = center
        if center is None:
            self.center = Point(0.0, 0.0)
        self.radius = radius
        self.label = label

    def containsPoint(self, point: Point):
        distance = math.dist((self.center.x, self.center.y), (point.x, point.y))
        if distance <= self.radius:
            return True
        return False

# A report of data based on the track.
class Report():
    def __init__(self, track: Track, rois: list[Circle], fps: float=30.0, cm_per_pixel: float=0.0):

        circles = []

        for circle in rois:
            circles.append(circle)

        self.id = track.id
        self.trial = track.trial

        totalStops = track.totalStops()
        secondsBetweenStops = 1.0 / fps

        self.trialDuration = (totalStops - 1) / fps

        self.totalRuntimeSeconds = float((totalStops - 1)) * secondsBetweenStops

        self.subReports: list[Subreport] = []

        for bodypart in track.stops:

            report = Subreport(bodypart)

            clock = 0.0

            currentVisitLabel = None
            currentVisitStart = -1.0

            lastKnownLocation = track.stops[bodypart][0]


            for i, stop in enumerate(track.stops[bodypart]):

                if i == 0:
                    continue

                clock += secondsBetweenStops

                report.distanceTraveled += math.dist((stop.x, stop.y), (lastKnownLocation.x, lastKnownLocation.y))

                visitingHole = False
                for c in circles:
                    if c.containsPoint(stop):
                        visitingHole = True
                        if currentVisitLabel is None:
                            # Starting a visit.
                            currentVisitLabel = c.label
                            currentVisitStart = clock
                        elif currentVisitLabel != c.label:
                            # Back-to-back visits of different holes.
                            report.visits.append(Visit(currentVisitLabel, currentVisitStart, clock - currentVisitStart))
                            currentVisitLabel = c.label
                            currentVisitStart = clock
                        break

                if currentVisitLabel is not None:
                    if visitingHole == False or i == len(track.stops[bodypart]) - 1:
                        report.visits.append(Visit(currentVisitLabel, currentVisitStart, clock - currentVisitStart))
                        currentVisitLabel = None
                        currentVisitStart = -1.0

                lastKnownLocation = stop

            report.averageVelocity = report.distanceTraveled / self.totalRuntimeSeconds

            report.distanceTraveledCm = report.distanceTraveled * cm_per_pixel

            report.averageVelocityCmps = report.distanceTraveledCm / self.totalRuntimeSeconds

            for v in report.visits:
                if v.circleLabel == circles[0].label:
                    report.firstVisitToTarget = v.startTimeSeconds
                    break

            self.subReports.append(report)

class DynamicVelocityReport:
    def __init__(self, track: Track, bodypart = None, fps: float=30.0, cm_per_pixel: float=0.0):
        self.track = track
        self.bodypart = bodypart
        self.fps = int(fps)
        self.cm_per_pixel = cm_per_pixel
        self.id = track.id
        self.trial = track.trial
        self.dynamic_vel_dict = {}
        self.__get_vels()

    def __get_vels(self):
        self.dynamic_vel_dict["Metadata"] = {"ID": self.id, "Trial": self.trial, "Bodypart": self.bodypart}
        self.dynamic_vel_dict["vel_report_pixels"] = {}
        s = 0
        while s <= len(self.track.stops[self.bodypart])-self.fps-1:
            p1 = s
            p2 = s+1
            c_bin_dist_pixels = 0
            for i in range(self.fps-1):
                c_bin_dist_pixels += math.dist((self.track.stops[self.bodypart][p1].x, self.track.stops[self.bodypart][p1].y), (self.track.stops[self.bodypart][p2].x, self.track.stops[self.bodypart][p2].y))
                p1+=1
                p2+=1
            self.dynamic_vel_dict["vel_report_pixels"][s] = c_bin_dist_pixels * self.cm_per_pixel
            s+=self.fps
        return self.dynamic_vel_dict

# A report section for one specific bodypart.
class Subreport():
    def __init__(self, name: str='none'):
        self.name = name
        self.distanceTraveled = 0.0
        self.distanceTraveledCm = 0.0
        self.averageVelocity = 0.0
        self.averageVelocityCmps = 0.0
        self.visits: list[Visit] = []
        self.firstVisitToTarget = None

# Part of a report. Indicates when a visit to a hole started, and how long it lasted.
class Visit():
    def __init__(self, circleLabel: str="hole", start: float=0.0, duration: float=0.0):
        self.circleLabel = circleLabel
        self.startTimeSeconds = start
        self.duration = duration

def __reports_to_csv(reports: list[Report], vel_reports, path: str, rois: list[Circle], rounding_digits: int=4):

    header = f"ID,trial,bodyPart,distTraveledPixels,distTraveledCM,avgVel_PX,avgVel_CM,escLatency"
    for circle in rois:
        header += f",{circle.label}visits,{circle.label}latency,{circle.label}duration"

    with open(path, 'w') as file:
        file.write(f"{header}\n")

        for report in reports:
            for bodypart in report.subReports:

                line = f"{report.id},{report.trial},{bodypart.name},{__return_rounded_value(bodypart.distanceTraveled, rounding_digits)},{__return_rounded_value(bodypart.distanceTraveledCm, rounding_digits)},{__return_rounded_value(bodypart.averageVelocity, rounding_digits)},{__return_rounded_value(bodypart.averageVelocityCmps, rounding_digits)},{__return_rounded_value(report.trialDuration, rounding_digits)}"

                visitCounts = {}
                visitLatencies = {}
                visitDurations = {}

                for circle in rois:
                    visitCounts[circle.label] = 0
                    visitLatencies[circle.label] = 999999999.99
                    visitDurations[circle.label] = 0.0

                for visit in bodypart.visits:
                    visitCounts[visit.circleLabel] += 1
                    visitDurations[visit.circleLabel] += __return_rounded_value(visit.duration, rounding_digits)
                    if visit.startTimeSeconds < visitLatencies[visit.circleLabel]:
                        visitLatencies[visit.circleLabel] = __return_rounded_value(visit.startTimeSeconds, rounding_digits)


                for circle in rois:
                    if visitCounts[circle.label] == 0:
                        line += f",0,NA,NA"
                    else:
                        line += f",{visitCounts[circle.label]},{visitLatencies[circle.label]:.4f},{visitDurations[circle.label]:.4f}"

                file.write(f"{line}\n")

    if len(vel_reports) > 0:
        max_length = max(len(row) for row in vel_reports)
        vel_header = ["id", "trial", "bodypart"]
        for i in range(1, max_length - 2):
            vel_header.append(f"sec{i}")
        vel_filename = vel_filename = f"{path[:-4]}_dynamic_velocity.csv"

        with open(vel_filename, 'w') as vel_file:
            for item in vel_header:
                vel_file.write(f"{item},")
            vel_file.write("\n")
            for row in vel_reports:
                for item in row:
                    vel_file.write(f"{item},")
                vel_file.write(f"\n")

def __return_value_or_NA(value):
    if value is None:
        return 'NA'
    return value

def __return_rounded_value(value: float, digits: int):
    if digits < 0:
        return value
    return round(value, digits)

if __name__ == "__main__":
    print("This code is meant to be imported as a module, not ran directly")