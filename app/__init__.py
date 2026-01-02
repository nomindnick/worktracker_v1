from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    # Register blueprints
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.projects import bp as projects_bp
    from app.routes.tasks import bp as tasks_bp
    from app.routes.milestones import bp as milestones_bp
    from app.routes.updates import bp as updates_bp
    from app.routes.export import bp as export_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(milestones_bp, url_prefix='/milestones')
    app.register_blueprint(updates_bp, url_prefix='/updates')
    app.register_blueprint(export_bp, url_prefix='/export')

    # CLI command to initialize database
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database."""
        db.create_all()
        print('Database initialized.')

    return app
