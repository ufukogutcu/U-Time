import datetime

from app import app, db, bcrypt

class Diary(db.Model):
    __tablename__ = 'diaries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, nullable=False)
    in_progress = db.Column(db.Boolean, nullable=False, default=False)
    result = db.Column(db.String(255), nullable=True)
    created_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, text, user_id, in_progress, result=None):
        self.text = text
        self.user_id = user_id
        self.in_progress = in_progress
        self.result = result
        self.created_on = datetime.datetime.now()

    def myjson(self):
        return {
            'id':self.id,
            'text':self.text,
            'user_id':self.user_id,
            'in_progress':self.in_progress,
            'result':self.result,
            'created_on':self.created_on
        }
