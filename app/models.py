from datetime import datetime, date
from app import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(200), nullable=False)
    project_name = db.Column(db.String(500), nullable=False)
    matter_number = db.Column(db.String(50))
    client_number = db.Column(db.String(50))
    assigner = db.Column(db.String(200), nullable=False, default='Self')
    assigned_attorneys = db.Column(db.String(500), nullable=False)
    priority = db.Column(db.String(10), nullable=False, default='medium')
    status = db.Column(db.String(10), nullable=False, default='active', index=True)
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    milestones = db.relationship('Milestone', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    status_updates = db.relationship('StatusUpdate', backref='project', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def last_update_date(self):
        """Get the datetime of the most recent status update, or None."""
        from app.models import StatusUpdate
        update = self.status_updates.order_by(StatusUpdate.created_at.desc()).first()
        return update.created_at if update else None

    def get_status_updates_ordered(self):
        """Get all status updates ordered by created_at descending (newest first)."""
        from app.models import StatusUpdate
        return self.status_updates.order_by(StatusUpdate.created_at.desc()).all()

    @property
    def days_since_update(self):
        """Return days since last update, or days since creation if no updates."""
        reference_date = self.last_update_date or self.created_at
        return (datetime.utcnow() - reference_date).days

    @property
    def staleness_level(self):
        """Return 'critical' (14+ days), 'warning' (7-13 days), or 'ok' (< 7 days)."""
        days = self.days_since_update
        if days >= 14:
            return 'critical'
        elif days >= 7:
            return 'warning'
        return 'ok'

    def get_pending_tasks(self):
        """Get all pending tasks ordered by due_date ascending, then priority."""
        from app.models import Task
        return self.tasks.filter_by(completed=False).order_by(Task.due_date.asc()).all()

    def get_completed_tasks(self):
        """Get all completed tasks ordered by completed_at descending (newest first)."""
        from app.models import Task
        return self.tasks.filter_by(completed=True).order_by(Task.completed_at.desc()).all()

    @property
    def pending_task_count(self):
        """Return count of pending tasks."""
        return self.tasks.filter_by(completed=False).count()

    @property
    def next_task(self):
        """Return the next pending task (earliest due_date), or None."""
        from app.models import Task
        return self.tasks.filter_by(completed=False).order_by(Task.due_date.asc()).first()

    def get_pending_milestones(self):
        """Get all pending milestones ordered by date ascending."""
        from app.models import Milestone
        return self.milestones.filter_by(completed=False).order_by(Milestone.date.asc()).all()

    def get_completed_milestones(self):
        """Get all completed milestones ordered by date descending."""
        from app.models import Milestone
        return self.milestones.filter_by(completed=True).order_by(Milestone.date.desc()).all()

    @property
    def next_milestone(self):
        """Return the next pending milestone (earliest date), or None."""
        from app.models import Milestone
        return self.milestones.filter_by(completed=False).order_by(Milestone.date.asc()).first()

    @property
    def latest_status_update(self):
        """Return the most recent StatusUpdate object, or None."""
        from app.models import StatusUpdate
        return self.status_updates.order_by(StatusUpdate.created_at.desc()).first()

    def get_status_preview(self, max_lines=3):
        """Return first N lines of latest status notes with has_more flag.

        Returns dict with 'text', 'has_more', 'full_text' keys, or None if no updates.
        """
        update = self.latest_status_update
        if not update or not update.notes:
            return None
        lines = update.notes.strip().split('\n')
        preview_lines = lines[:max_lines]
        has_more = len(lines) > max_lines
        return {
            'text': '\n'.join(preview_lines),
            'has_more': has_more,
            'full_text': update.notes if has_more else None
        }

    def __repr__(self):
        return f'<Project {self.client_name}: {self.project_name}>'


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # self, associate, client, opposing_counsel, assigning_attorney
    target_name = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=False, index=True)
    description = db.Column(db.Text)
    priority = db.Column(db.String(10), nullable=False, default='medium')  # high, medium, low
    completed = db.Column(db.Boolean, nullable=False, default=False, index=True)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.target_name} by {self.due_date}>'


class Milestone(db.Model):
    __tablename__ = 'milestones'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False, index=True)
    completed = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Milestone {self.name} for project {self.project_id}>'


class StatusUpdate(db.Model):
    __tablename__ = 'status_updates'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    notes = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<StatusUpdate {self.id} for project {self.project_id}>'
