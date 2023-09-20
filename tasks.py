from celery import Celery

from config import Config


celery = Celery('app',broker=Config.CELERY_BROKER_URL)

@celery.task()
def process_diary(id):
    pprocess_diary(id)

from app import app, db
from diary.models import Diary

def pprocess_diary(id):
    with app.app_context():
        diary = Diary.query.filter_by(id=id).first()
        diary.result = text_processor(diary.text)
        diary.in_progress = False

        db.session.add(diary)
        db.session.commit()

def text_processor(text):
    return 'a'
