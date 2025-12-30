from datetime import datetime, date
from app import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(200), nullable=False)
    project_name = db.Column(db.String(500), nullable=False)
    matter_number = db.Column(db.String(50))
    hard_deadline = db.Column(db.Date)
    internal_deadline = db.Column(db.Date, nullable=False, index=True)
    assigner = db.Column(db.String(200), nullable=False, default='Self')
    assigned_attorneys = db.Column(db.String(500), nullable=False)
    priority = db.Column(db.String(10), nullable=False, default='medium')
    status = db.Column(db.String(10), nullable=False, default='active', index=True)
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    followups = db.relationship('FollowUp', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    status_updates = db.relationship('StatusUpdate', backref='project', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Project {self.client_name}: {self.project_name}>'


class FollowUp(db.Model):
    __tablename__ = 'followups'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # associate, client, opposing_counsel, other
    target_name = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=False, index=True)
    notes = db.Column(db.Text)
    completed = db.Column(db.Boolean, nullable=False, default=False, index=True)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FollowUp {self.target_name} by {self.due_date}>'


class StatusUpdate(db.Model):
    __tablename__ = 'status_updates'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    notes = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<StatusUpdate {self.id} for project {self.project_id}>'
