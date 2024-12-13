from pydantic_settings import BaseSettings
from clockify_api_client.client import ClockifyAPIClient
from dotenv import load_dotenv
from typing import Any

load_dotenv()

class Config(BaseSettings):
    api_key: str
    api_url: str

config = Config()

client = ClockifyAPIClient().build(config.api_key, config.api_url)


def print_names(entries: list[dict[str, Any]]) -> None:
    print('\n'.join(f'{i+1}. {entry["name"]}' for i, entry in enumerate(entries)))


def check_input(index: int, entries: list[dict[str, Any]]) -> None:
    if len(entries) < index or index < 1:
        raise IndexError("Such id does not exist.")


def main():
    workspaces = client.workspaces.get_workspaces()
    if not workspaces:
        raise RuntimeError('There are no workspaces available.')
    print("Select from workspaces: ")
    print_names(workspaces)
    workspace = int(input())
    check_input(workspace, workspaces)
    workspace_id = workspaces[workspace-1]['id']


    projects = client.projects.get_projects(workspace_id)
    if not projects:
        raise RuntimeError('There are no projects available.')
    print("Select from projects: ")
    print_names(projects)
    project = int(input())
    check_input(project, projects)
    project_id = projects[project-1]["id"]


    tasks = client.tasks.get_tasks(workspace_id, project_id)
    if not tasks:
        raise RuntimeError('There are no projects available.')
    print("\nTasks:")
    print_names(tasks)


if __name__ == "__main__":
    main()