from random import randint
from flask_login import UserMixin
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class BaseModel:
    @classmethod
    def get_by_id(ModelClass, id: int):
        return ModelClass.query.get(id)

    @classmethod
    def get_all(ModelClass, offset: int = 0, limit: int = 10):
        return ModelClass.query.offset(offset).limit(limit).all()

    @classmethod
    def create(ModelClass, **kwargs):
        model_instance = ModelClass(**kwargs)
        model_instance.update()

    @classmethod
    def create_and_get(ModelClass, **kwargs):
        model_instance = ModelClass(**kwargs)
        model_instance.update()
        return model_instance

    def update(self):
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)

    def delete(self):
        """метод для удаления объекта из базы данных"""
        db.session.delete(self)
        db.session.commit()


class User(UserMixin, db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    tests = db.relationship('Test', backref='owner', lazy=True)

    @staticmethod
    def create_and_get(**kwargs):
        user = User(**kwargs)
        user.set_password(user.password)
        user.update()
        return user

    @staticmethod
    def from_form(form_data):
        return User.create_and_get(
            username=form_data["username"],
            password=form_data["password"]
        )

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password, password)

    @staticmethod
    def get_by_username(username: str):
        return User.query.filter(User.username == username).first()

    @staticmethod
    def is_free_username(username: str) -> bool:
        return not db.session.query(
            db.exists().where(User.username == username)
        ).scalar()


class Test(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    questions = db.relationship('Question', backref='test', lazy=True)

    @staticmethod
    def from_form(form_data: dict, owner_id: int):
        return Test.create_and_get(
            title=form_data["title"],
            description=form_data["description"],
            is_public=form_data["public"] == "Public",
            owner_id=owner_id
        )

    @staticmethod
    def get_user_tests_order_by_title_asc(user_id: int):
        return Test.query.filter(Test.owner_id == user_id).order_by(
            func.lower(Test.title)).all()

    @staticmethod
    def get_user_tests_order_by_title_desc(user_id: int):
        return Test.query.filter(Test.owner_id == user_id).order_by(
            func.lower(Test.title).desc()).all()

    @staticmethod
    def get_user_tests_order_by_id_asc(user_id: int):
        return Test.query.filter(Test.owner_id == user_id).order_by(
            Test.id).all()

    @staticmethod
    def get_user_tests_order_by_id_desc(user_id: int):
        return Test.query.filter(Test.owner_id == user_id).order_by(
            Test.id.desc()).all()

    def update_questions_order(self):
        for question in self.questions:
            question.random_order = randint(0, 1000)
        db.session.add_all(self.questions)
        db.session.commit()


class Question(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    comment = db.Column(db.String, nullable=True)
    is_marked = db.Column(db.Boolean, default=False)
    random_order = db.Column(db.Integer, nullable=False, default=0)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)

    @staticmethod
    def create_from_form_many(form_data: dict, test_id: int):
        pool = form_data.split("\r\n")
        for question in pool:
            Question.create(text=question.strip(), test_id=test_id)

    @staticmethod
    def get_paginated(test_id: int, page: int, per_page: int = 3, only_marked: bool = False):
        query = Question.query.filter(Question.test_id == test_id)
        if only_marked:
            query = query.filter(Question.is_marked == only_marked)
        return query.order_by(Question.random_order).paginate(page=page, per_page=per_page)

    def mark(self):
        self.is_marked = not self.is_marked
        self.update()

    def edit_from_form_data(self, form_data):
        self.text = form_data["text"]
        self.comment = form_data["comment"]
        self.is_marked = form_data["is_marked"]
        self.update()


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
