from flask_testing import TestCase
from run import app
from backend import db
from backend.models import Event


class BaseTestCase(TestCase):
    """Base Set-Up and Tear-Down."""

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.add(Event(id=1, eb_id='5', name='Check', image='https://png.pngtree.com/svg/20161216/5935bddf9c.png',
                             desc='Check check', html='<p>Check check</p>',
                             url='https://png.pngtree.com/svg/20161216/5935bddf9c.png', address='Check city, Atlanta',
                             lat=0, lng=0))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
