from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.forms import LoginForm, RegisterForm, TestForm, QuestionForm
from app.models import Question, Test, User


@app.get("/")
@login_required
def root():
    match (order := request.args.get("order", "titleAZ")):
        case "dateNewFirst":
            tests = Test.get_user_tests_order_by_id_asc(current_user.id)
        case "dateOldFirst":
            tests = Test.get_user_tests_order_by_id_desc(current_user.id)
        case "titleZA":
            tests = Test.get_user_tests_order_by_title_desc(current_user.id)
        case _:
            tests = Test.get_user_tests_order_by_title_asc(current_user.id)
            order = "titleAZ"
    return render_template("home.html", user=current_user, tests=tests, order=order)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("root"))
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.get_by_username(form.data["username"].strip())
        if user and user.check_password(form.data["password"]):
            login_user(user, remember=form.data["remember"])
            return redirect(url_for("root"))
        flash("Wrong login or password", "warning")
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("root"))
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.from_form(form.data)
        login_user(user)
        flash("Successfully created new user", "success")
        return redirect(url_for("root"))
    return render_template("register.html", form=form)


@app.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/new", methods=["GET", "POST"])
@login_required
def new_test():
    form = TestForm(request.values)
    if request.method == "POST" and form.validate():
        test = Test.from_form(form.data, current_user.id)
        Question.create_from_form_many(form.data["questions"], test.id)
        flash("Successfully created new test", "success")
        return redirect(url_for("root"))
    return render_template("new_test.html", form=form, user=current_user)


@app.get("/test/<int:test_id>")
@login_required
def test_detail(test_id: int):
    if (test := Test.get_by_id(test_id)) is None:
        abort(404, "Test not found.")
    if test.owner_id != current_user.id:
        abort(403, "You are not allowed to access this test.")
    return render_template("test_detail.html", test=test, user=current_user)


@app.get("/shuffle/<int:test_id>")
@login_required
def shuffle_questions(test_id: int):
    test = Test.get_by_id(test_id)
    if test.owner_id != current_user.id:
        abort(403, "You are not allowed to access this test.")
    test.update_questions_order()
    try:
        only_marked = int(request.args.get("only_marked", 0))
        per_page = int(request.args.get("per_page", 0))
    except ValueError:
        only_marked = 0
        per_page = 3
    return redirect(
        url_for(
            "run_test",
            test_id=test_id,
            only_marked=only_marked,
            per_page=per_page
        )
    )


@app.get("/run/<int:test_id>")
@login_required
def run_test(test_id: int):
    test = Test.get_by_id(test_id)
    if test.owner_id != current_user.id:
        abort(403, "You are not allowed to access this test.")
    try:
        page = int(request.args.get("page", 1))
        only_marked = int(request.args.get("only_marked", 0))
        per_page = int(request.args.get("per_page", 3))
    except ValueError:
        abort(404, "Incorrect types of query parameters provided.")
    if only_marked not in (0, 1) or not (0 < per_page < 10):
        abort(404, "Incorrect values of query parameters provided.")
    return render_template(
        "run_test.html",
        test_id=test_id,
        only_marked=only_marked,
        user=current_user,
        questions=Question.get_paginated(
            test_id=test_id,
            page=page,
            per_page=per_page,
            only_marked=only_marked == 1
        )
    )


@app.post("/mark")
@login_required
def mark_question():
    if (question_id := request.values.get("question_id")) is not None:
        question = Question.get_by_id(question_id)
        if question.test.owner_id == current_user.id:
            question.mark()
    return "success"


@app.post("/delete_question")
@login_required
def delete_question():
    if (question_id := request.values.get("question_id")) is not None:
        question = Question.get_by_id(question_id)
        if question.test.owner_id == current_user.id:
            question.delete()
    return "success"


@app.route("/question/<int:question_id>", methods=["GET", "POST"])
@login_required
def edit_question(question_id: int):
    form = QuestionForm(request.form)
    if (question := Question.get_by_id(question_id)) is None:
        abort(404, "Question not found.")
    if question.test.owner_id != current_user.id:
        abort(403, "You are not allowed to edit this question.")
    if request.method == "POST" and form.validate():
        question.edit_from_form_data(form.data)
        return redirect(url_for("test_detail", test_id=question.test_id))
    form.fill_from_db_object(question)
    return render_template(
        "question_detail.html",
        form=form,
        question_id=question_id,
        user=current_user
    )
