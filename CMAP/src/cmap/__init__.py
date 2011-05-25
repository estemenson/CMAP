from os import path
from cmap.view.stories.storyViews import MinStoryView, StoryView
from cmap.model.storyModel import StoryModel
from cmap.controller.storyController import StoryController
from cmap.view.projects.projectViews import ProjectView, ProjectMinView
from cmap.model.projectModel import ProjectModel
from cmap.controller.projectController import ProjectController
from cmap.view.releases.releaseViews import ReleaseView, ReleaseMinView
from cmap.model.releaseModel import ReleaseModel
from cmap.controller.releaseController import ReleaseController
from cmap.view.sprints.sprintViews import SprintMinView, SprintView
from cmap.model.sprintModel import SprintModel
from cmap.controller.sprintController import SprintController
from cmap.view.tasks.taskViews import TaskMinView, TaskView
from cmap.model.taskModel import TaskModel
from cmap.controller.taskController import TaskController

#AGILE_ICONS = path.join(path.abspath(path.dirname(__file__)), 'icons')
BACKLOG,PROJECTS,RELEASES,SPRINTS,STORIES,TASKS = 'backlog','projects',\
                                        'releases','sprints','stories','tasks'
artefact_types = {
    BACKLOG:
        {'type':BACKLOG,'view_type':StoryView, 'mini_view_type':MinStoryView, 
         'get_artefact':'newBacklog', 'model': StoryModel,
         'container':['backlog_list_layout', 'backlog_flow'], 
         'callback':'flow_backlog_select',
         'viewCurrent':'viewCurrentBacklog', 'controller':StoryController, 
         'current':'current_backlog'},
    PROJECTS:
        {'type':PROJECTS,'view_type':ProjectView, 
         'mini_view_type':ProjectMinView, 'get_artefact':'newProject',
         'model': ProjectModel,'container':['projects_flow'], 
         'viewCurrent':'viewCurrentProject','callback':'flow_projects_select', 
         'controller':ProjectController, 'current':'current_project'},
    RELEASES:
        {'type':RELEASES,'view_type':ReleaseView, 
         'mini_view_type':ReleaseMinView, 'get_artefact':'newRelease',
         'model': ReleaseModel,'container':['release_flow'], 
         'viewCurrent':'viewCurrentRelease','callback':'flow_release_select', 
         'controller':ReleaseController, 'current':'current_release'},
    SPRINTS:
        {'type':SPRINTS,'view_type':SprintView, 'mini_view_type':SprintMinView,
         'get_artefact':'newSprint', 'model': SprintModel,
         'container':['sprint_flow'],'viewCurrent':'viewCurrentSprint',
         'callback':'flow_sprint_select','controller':SprintController, 
         'current':'current_sprint'},
    STORIES:
        {'type':STORIES,'view_type':StoryView, 'mini_view_type':MinStoryView, 
         'get_artefact':'newStory', 'model': StoryModel,
         'container':['story_flow'], 'callback':'flow_story_select', 
        'viewCurrent':'viewCurrentStory', 'controller':StoryController, 
        'current':'current_story'},
    TASKS:
        {'type':TASKS,'view_type':TaskView, 'mini_view_type':TaskMinView, 
         'get_artefact':'newTask', 'model': TaskModel,'container':['task_flow'], 
         'viewCurrent':'viewCurrentTask','callback':'flow_task_select',
         'controller':TaskController, 'current':'current_task'}
    }
