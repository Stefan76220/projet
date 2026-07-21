from src.core.project import Project


class ProjectManager:

    def __init__(self):

        self.current_project = None

    def new_project(self, folder: str, name: str):

        project = Project()

        project.create(folder, name)

        self.current_project = project

        return project

    def open_project(self, folder: str):

        project = Project()

        project.load(folder)

        self.current_project = project

        return project

    def has_project(self):

        return self.current_project is not None

    def get_project_name(self):

        if self.current_project is None:
            return ""

        return self.current_project.name

    def get_project(self):

        return self.current_project