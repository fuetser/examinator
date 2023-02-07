from wtforms import Form, BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from wtforms.widgets import TextArea
from app.models import User, Question


class RegisterForm(Form):
    username = StringField('Username', [DataRequired(), Length(min=3, max=25)])
    password = PasswordField('Password', [DataRequired(), Length(min=8, max=32)])
    confirm_password = PasswordField('Confirm Password', [EqualTo('password')])
    submit = SubmitField("Register")

    def validate_username(self, username):
        if not User.is_free_username(username.data):
            raise ValidationError(f"Username {username.data} is already taken")


class LoginForm(Form):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


class TestForm(Form):
    title = StringField("Title", validators=[DataRequired(), Length(min=1, max=50)])
    description = StringField("Description")
    questions = StringField("Questions (each on a new line)", validators=[DataRequired()], widget=TextArea())
    public = SelectField("Access", choices=["Private", "Public"], default="Public")
    submit = SubmitField("Create")


class QuestionForm(Form):
    text = StringField("Text", validators=[DataRequired()])
    comment = StringField("Details", widget=TextArea())
    is_marked = BooleanField("Is Marked")
    submit = SubmitField("Save changes")

    def fill_from_db_object(self, question: Question):
        self.text.data = question.text
        self.comment.data = question.comment
        self.is_marked.data = question.is_marked
