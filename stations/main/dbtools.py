import click
from stations.extensions import db


def init_dbsql():
    db.create_all()


@click.command('init-dbsql')
def init_dbsql_command():
    """Clear the existing data and create new tables."""
    init_dbsql()
    click.echo('Initialized the sqlalchemy database.')


def construct_db(app):
    # app.teardown_appcontext(close_db)
    app.cli.add_command(init_dbsql_command)
