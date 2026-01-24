from application.ports.command import BaseCommand


class CreateRepositoryCommand(BaseCommand):
    repoisotry_name: str
