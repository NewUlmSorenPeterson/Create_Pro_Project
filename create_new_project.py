import datetime
import os
import arcpy
import shutil

class new_project:

    template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Template")
    base_directory = r"\\nu-sto-03\Departments\Engineering_CAD\Engineering-City\Data\GIS\_ESRI\A_Pro\_Figures"
    current_year = datetime.date.today().strftime("%Y")

    def __init__(self, project_name):
        self.name = project_name
        self.location = os.path.join(new_project.base_directory, new_project.current_year, project_name)
        self.output_aprx = ""
        self.output_gdb = ""
        print("Job Created")

    def create_project_folder(self):
        if not os.path.exists(self.location):
            os.makedirs(self.location)
            print("Folder Created")

    def create_geodatabase(self):
        arcpy.management.CreateFileGDB(
        out_folder_path= self.location,
        out_name="Data",
        out_version="CURRENT"
        )
        self.output_gdb = os.path.join(self.location, "data.gdb")
        print("Geodatabase Created {}".format(self.output_gdb))

    def update_folder_connections(self):
        proj_aprx = arcpy.mp.ArcGISProject(self.output_aprx)
        folders = proj_aprx.folderConnections
        new_folder = {'connectionString': self.location, 'alias':self.name, 'isHomeFolder':True}
        folders.append(new_folder)
        for d in folders:
            print(d)
            if d["connectionString"] != self.location:
                folders.remove(d)
            if d["connectionString"] == self.location:
                d['isHomeFolder'] = True
        print(folders)
        proj_aprx.updateFolderConnections(folders, True)
        proj_aprx.save()

    def update_database_connections(self):
        proj_aprx = arcpy.mp.ArcGISProject(self.output_aprx)
        db = proj_aprx.databases
        for d in db:
            print(d["databasePath"])
            if d["databasePath"] != self.output_gdb:
                db.remove(d)
        print(db)
        proj_aprx.updateDatabases(db, True)
        proj_aprx.save()

    def update_toolbox_connections(self):
        proj_aprx = arcpy.mp.ArcGISProject(self.output_aprx)
        new_toolbox_name = self.name + ".atbx"
        new_toolbox = {'toolboxPath': os.path.join(self.location, new_toolbox_name), 'isDefaultToolbox': True}
        toolboxes = proj_aprx.toolboxes
        toolboxes.append(new_toolbox)
        shutil.copyfile(os.path.join(new_project.template_dir, "Default.atbx"), os.path.join(self.location, new_toolbox_name))
        print (toolboxes)
        for d in toolboxes:
            if d["toolboxPath"] != os.path.join(self.location, new_toolbox_name):
                toolboxes.remove(d)
        proj_aprx.updateToolboxes(toolboxes, True)
        proj_aprx.save()

    def create_project_aprx(self):
        aprx_file_name = str(self.name).replace(" ", "_") + ".aprx"
        self.output_aprx = os.path.join(self.location, aprx_file_name)
        proj_aprx = arcpy.mp.ArcGISProject(os.path.join(new_project.template_dir, "template.aprx"))
        db = proj_aprx.databases
        print(db)
        db.append({'databasePath' : self.output_gdb,
           'isDefaultDatabase': False})
        print(db)
        proj_aprx.updateDatabases(db, True)
        proj_aprx.defaultGeodatabase = self.output_gdb
        proj_aprx.saveACopy(self.output_aprx)
        self.update_database_connections()
        self.update_folder_connections()
        self.update_toolbox_connections()
        print("Aprx Configured {}".format(self.output_aprx))
        print("Aprx Created")

    def exec_create_project(self):
        self.create_project_folder()
        self.create_geodatabase()
        self.create_project_aprx()

if __name__ == '__main__':
    project_name = input("Enter Project Name: ").replace(" ", "_")
    create_project = new_project(project_name)
    create_project.exec_create_project()
