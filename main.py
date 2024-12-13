from pydantic_settings import BaseSettings
from clockify_api_client.client import ClockifyAPIClient
from dotenv import load_dotenv
from typing import Any
from collections import defaultdict
from datetime import datetime

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


def duration_parser(start: str, end: str) -> float:
    return (datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ") - datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")).total_seconds()


def get_time(duration: float) -> str:
    hours = duration // 3600
    minutes = (hours % 3600) // 60
    seconds = duration % 60
    return f'{int(hours)}:{int(minutes)}:{int(seconds)}'


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
    task_names = {task['id']: task['name'] for task in tasks}


    user_id = client.users.get_current_user()['id']
    user_time_entries = client.time_entries.get_time_entries(workspace_id, user_id, dict(project=project_id))
    print("\nDuration grouped by dates:")

    unique_dates = defaultdict(lambda: defaultdict(float))
    for time_entrie in user_time_entries:
        unique_dates[time_entrie['timeInterval']['start'][:10]][time_entrie['taskId']] += duration_parser(time_entrie['timeInterval']['start'], time_entrie['timeInterval']['end'])

    for key, value in unique_dates.items():
        print(key)
        for task_id, duration in value.items():
            print(f'\ttask: {task_names[task_id]}, duration: {get_time(duration)}')

    print("\nTotal duration for each task:")
    for task in tasks:
        print(f"task: {task['name']}, total duration: {task['duration']}")    

if __name__ == "__main__":
    main()