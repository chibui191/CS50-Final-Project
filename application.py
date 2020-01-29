import cs50
import datetime

import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf.csrf import CSRFProtect

from helpers import usd, login_required, save_picture, percentage
from forms import (RegistrationForm, LoginForm, UpdateAccountForm, AddExpenseForm, AddIncomeForm,
                   ResetPasswordForm, SetIncomeGoalsForm, PlanBudgetsForm, ManageDebtForm, AddDebtPaymentForm)


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Secret Keys
csrf = CSRFProtect(app)
app.config["SECRET_KEYS"] = 'bc9404504f66a6823b087e442aca1201'
app.config['WTF_CSRF_SECRET_KEY'] = "bc9404504f66a6823b087e442aca1201"
csrf.init_app(app)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["percentage"] = percentage

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///moneymanager.db")


@app.route("/")
@login_required
def index():
    return redirect("/dashboard")


@app.route("/dashboard")
@login_required
def get_dashboard():
    """Show general income/expense total & budget status"""
    # get current datetime
    x = datetime.datetime.now()
    currentMonth = x.strftime("%m")
    currentYear = x.strftime("%Y")
    currentMonthShort = x.strftime("%b")
    currentMonthFull = x.strftime("%B")

    # get current user_id
    current_user_id = int(session.get("user_id"))
    # Query 'user' database for all information of current user using lookup
    user = db.execute("SELECT * FROM user WHERE user_id = :user_id",
                        user_id=current_user_id)
    image_file = url_for('static', filename='img/' + user[0]["image_file"])

    # define forms
    form_adex = AddExpenseForm()
    form_adin = AddIncomeForm()
    form_ingo = SetIncomeGoalsForm()
    form_bud = PlanBudgetsForm()
    form_made = ManageDebtForm()

    # query 'incomes' table for sum of all income amounts group by month
    totalIncomes = db.execute("SELECT IFNULL(SUM(amount), 0) AS sumIncome FROM incomes WHERE user_id = :user_id AND strftime('%m', post_date) = :currentMonth AND strftime('%Y', post_date) = :currentYear",
                                currentMonth=currentMonth, currentYear=currentYear, user_id=current_user_id)

    # query 'expenses' table for sum of all expense amounts group by month
    totalExpenses = db.execute("SELECT IFNULL(SUM(amount), 0) AS sumExpense FROM expenses WHERE user_id = :user_id AND strftime('%m', post_date) = :currentMonth AND strftime('%Y', post_date) = :currentYear",
                                currentMonth=currentMonth, currentYear=currentYear, user_id=current_user_id)

    # query 'debt' table for sum of all expense amounts with payoff_date in current month/year
    totalDebt = db.execute("SELECT IFNULL(SUM(current_amount), 0) AS sumDebt FROM debts WHERE user_id = :user_id AND strftime('%m', payoff_date) = :currentMonth AND strftime('%Y', payoff_date) = :currentYear",
                                currentMonth=currentMonth, currentYear=currentYear, user_id=current_user_id)

    # query 'debtpayments' table for sum of all payments already made in current month/year
    debtsPaid = db.execute("SELECT IFNULL(SUM(amount), 0) AS sumPaid FROM debtpayments WHERE user_id = :user_id AND strftime('%m', payment_date) = :currentMonth AND strftime('%Y', payment_date) = :currentYear",
                                currentMonth=currentMonth, currentYear=currentYear, user_id=current_user_id)

    """ INCOME GOALS display """
    # query 'incomegoals' table for list of all income goals for current month grouped by goal_type
    income_goals = db.execute("SELECT IFNULL(SUM(amount), 0) AS sumAmount, goal_type FROM incomegoals WHERE user_id = :user_id AND target_month = :currentMonth AND target_year = :currentYear GROUP BY goal_type",
                                currentMonth=currentMonth, currentYear=currentYear, user_id=current_user_id)
    goal_rows = []
    for income_goal in income_goals:
        # if income_goal is a 'Total' goal
        if income_goal['goal_type'] == 'Total':
            totalGoalDict = {'goal_type': 'Total', 'goal_amount': income_goal['sumAmount'], 'current_amount': totalIncomes[0]['sumIncome']}
            goal_rows.append(totalGoalDict)
        # categorical goals
        else:
            # query 'incomes' table for current amount for each category
            check_goal = db.execute("SELECT IFNULL(SUM(amount), 0) AS sumIncomeByCat, category FROM incomes WHERE user_id = :user_id AND strftime('%m', post_date) = :currentMonth AND strftime('%Y', post_date) = :currentYear AND category = :category",
                                        currentMonth=currentMonth, currentYear=currentYear, user_id=current_user_id, category=income_goal['goal_type'])
            # if goal_type has appeared in 'incomes' table --> get current_amount
            if check_goal:
                goalDict = {'goal_type': income_goal['goal_type'], 'goal_amount': income_goal['sumAmount'], 'current_amount': check_goal[0]['sumIncomeByCat']}
                goal_rows.append(goalDict)
            # if 'incomes' table currently doesn't have any entry for that category --> current_amount = 0
            else:
                emptyGoalDict = {'goal_type': income_goal['goal_type'], 'goal_amount': income_goal['sumAmount'], 'current_amount': 0}
                goal_rows.append(emptyGoalDict)

    """ EXPENSE BUDGETS display """
    # query 'budgets' table for list of all budgets for current month/year grouped by budget_type
    budgets = db.execute("SELECT IFNULL(SUM(amount), 0) AS sumBudgetAmount, budget_type FROM budgets WHERE user_id = :user_id AND target_month = :currentMonth AND target_year = :currentYear GROUP BY budget_type",
                                currentMonth=currentMonth, currentYear=currentYear, user_id=current_user_id)
    budget_rows = []
    for budget in budgets:
        # if budget_type is a 'Total' budget
        if budget['budget_type'] == 'Total':
            totalBudgetDict = {'budget_type': 'Total', 'budget_amount': budget['sumBudgetAmount'], 'current_expense': totalExpenses[0]['sumExpense']}
            budget_rows.append(totalBudgetDict)
        # categorical budgets
        elif budget['budget_type'] != 'Total':
            # query 'expenses' table for current status/amount for each category of 'budgets'
            check_budget = db.execute("SELECT IFNULL(SUM(amount), 0) AS sumExpenseByCat, category FROM expenses WHERE user_id = :user_id AND strftime('%m', post_date) = :currentMonth AND strftime('%Y', post_date) = :currentYear AND category = :category",
                                        currentMonth=currentMonth, currentYear=currentYear, user_id=current_user_id, category=budget['budget_type'])
            # if budget_type has appeared in current 'expenses' table for this month/year
            if check_budget:
                budgetDict = {'budget_type': budget['budget_type'], 'budget_amount': budget['sumBudgetAmount'], 'current_expense': check_budget[0]['sumExpenseByCat']}
                budget_rows.append(budgetDict)
            # if 'expenses' table doesn't have any entry for that budget_type --> current_amount = 0
            else:
                emptyBudgetDict = {'goal_type': budget['budget_type'], 'budget_amount': budget['sumBudgetAmount'], 'current_expense': 0}
                budget_rows.append(emptyBudgetDict)

    """ DEBT MANAGEMENT DISPLAY """
    debts = db.execute("SELECT CAST ((julianday(payoff_date) - julianday(post_date)) / 365 * 12 AS integer) AS monthsDiff, debt_id, initial_amount, current_amount, description, category, interest, payoff_date FROM debts WHERE user_id = :user_id",
                                    user_id=current_user_id)

    """ PAYMENTS TOWARDS DEBT """
    # query 'debts' table for category & description of all debts
    all_debts = db.execute("SELECT debt_id, (category || ' (' || description || ')') AS choice_description FROM debts WHERE user_id = :user_id",
                            user_id=session.get("user_id"))

    form_adde = AddDebtPaymentForm()
    #passing group_list to the form
    form_adde.debt.choices = [(i['debt_id'], i['choice_description']) for i in all_debts]

    return render_template("dashboard.html", currentMonthFull=currentMonthFull, currentYear=currentYear, totalIncomes=totalIncomes, totalExpenses=totalExpenses,
                            totalDebt=totalDebt, user=user, image_file=image_file, form_adex=form_adex, form_adin=form_adin, form_ingo=form_ingo,
                            goal_rows=goal_rows, form_bud=form_bud, budget_rows=budget_rows, form_made=form_made, form_adde=form_adde, debts=debts,
                            debtsPaid=debtsPaid)


@app.route("/add/expense", methods=["POST"])
@login_required
def add_expense():
    # define different forms
    form_adex = AddExpenseForm()
    if form_adex.validate_on_submit():
        # Insert user_id, amount, description, category, payment_method, post_date & status into 'expenses' table
        expense = db.execute("INSERT INTO expenses (user_id, amount, description, category, payment_method, post_date, status) VALUES (:user_id, :amount, :description, :category, :payment_method, :post_date, :status)",
                                  user_id=session.get("user_id"),
                                  amount=(-1)*float(form_adex.amount.data),
                                  description=form_adex.description.data,
                                  category=form_adex.category.data,
                                  payment_method=form_adex.payment_method.data,
                                  post_date=form_adex.post_date.data,
                                  status=form_adex.status.data)
        # flash message
        flash('Expense has been added successfully!', 'success')
    else:
        # flash message
        flash('Invalid expense information. Please try to re-submit.', 'danger')

    # Redirect to transactions
    return redirect("/transactions")


@app.route("/add/income", methods=["POST"])
@login_required
def add_income():
    # define form
    form_adin = AddIncomeForm()
    if form_adin.validate_on_submit():
        # Insert user_id, amount, description, category, payment_method, post_date & status into 'incomes' table
        income = db.execute("INSERT INTO incomes (user_id, amount, description, category, payment_method, post_date, status) VALUES (:user_id, :amount, :description, :category, :payment_method, :post_date, :status)",
                                  user_id=session.get("user_id"),
                                  amount=float(form_adin.amount.data),
                                  description=form_adin.description.data,
                                  category=form_adin.category.data,
                                  payment_method=form_adin.payment_method.data,
                                  post_date=form_adin.post_date.data,
                                  status=form_adin.status.data)
        # flash message
        flash('Income has been added successfully!', 'success')
    else:
        # flash message
        flash('Invalid income information. Please try to re-submit.', 'danger')

    # Redirect to transactions
    return redirect("/transactions")


@app.route("/add/debt_payment", methods=["POST"])
@login_required
def add_debt_payment():
    # query 'debts' table for category & description of all debts
    all_debts = db.execute("SELECT debt_id, (category || ' (' || description || ')') AS choice_description FROM debts WHERE user_id = :user_id",
                            user_id=session.get("user_id"))

    form_adde = AddDebtPaymentForm()
    #passing group_list to the form
    form_adde.debt.choices = [(i['debt_id'], i['choice_description']) for i in all_debts]

    if form_adde.validate_on_submit():
        # Insert user_id, debt_id, amount, payment_date into 'debtpayments' table
        debt_payment = db.execute("INSERT INTO debtpayments (user_id, amount, debt_id, payment_date) VALUES (:user_id, :amount, :debt_id, :payment_date)",
                                  user_id=session.get("user_id"),
                                  amount=float(form_adde.amount.data),
                                  debt_id=form_adde.debt.data,
                                  payment_date=form_adde.payment_date.data)
        # update current_amount in 'debts'
        update_debt = db.execute("UPDATE debts SET current_amount = current_amount - :paid WHERE debt_id = :debt_id",
                                    debt_id=form_adde.debt.data,
                                    paid=float(form_adde.amount.data))

        # flash message
        flash('Debt payment has been logged in successfully!', 'success')
    else:
        # flash message
        flash('Invalid payment information. Please try to re-submit.', 'danger')

    # Redirect to dashboard
    return redirect("/")

@app.route("/set_goals/incomes", methods=["POST"])
@login_required
def set_income_goals():
    # define different forms
    form_ingo = SetIncomeGoalsForm()
    if form_ingo.validate_on_submit():
        # Insert user_id, goal_type, amount, description, target_month, & target_year into 'incomegoals' table
        income_goal = db.execute("INSERT INTO incomegoals (user_id, goal_type, amount, target_month, target_year) VALUES (:user_id, :goal_type, :amount, :target_month, :target_year)",
                                  user_id=session.get("user_id"),
                                  goal_type=form_ingo.goal_type.data,
                                  amount=float(form_ingo.amount.data),
                                  target_month=form_ingo.target_month.data,
                                  target_year=form_ingo.target_year.data)
        # flash message
        flash('Income goal has been logged in successfully!', 'success')
    else:
        # flash message
        flash('Invalid goal information. Please try to re-submit.', 'danger')

    # Redirect to dashboard
    return redirect("/")


@app.route("/set_goals/budgets", methods=["POST"])
@login_required
def plan_budgets():
    # define different forms
    form_bud = PlanBudgetsForm()
    if form_bud.validate_on_submit():
        # Insert user_id, budget_type, amount, description, target_month, & target_year into 'budgets' table
        budget = db.execute("INSERT INTO budgets (user_id, budget_type, amount, target_month, target_year) VALUES (:user_id, :budget_type, :amount, :target_month, :target_year)",
                                  user_id=session.get("user_id"),
                                  budget_type=form_bud.budget_type.data,
                                  amount=float(form_bud.amount.data),
                                  target_month=form_bud.target_month.data,
                                  target_year=form_bud.target_year.data)
        # flash message
        flash('Planned budget has been logged in successfully!', 'success')
    else:
        # flash message
        flash('Invalid budget information. Please try to re-submit.', 'danger')
    # Redirect to dashboard
    return redirect("/")


@app.route("/set_goals/debts", methods=["POST"])
@login_required
def manage_debt():
    form_made = ManageDebtForm()
    if form_made.validate_on_submit():
        # Insert user_id, initial_amount, current_amount, description, category, interest, & payoff_date into 'debt' table
        debt = db.execute("INSERT INTO debts (user_id, initial_amount, current_amount, description, category, interest, payoff_date) VALUES (:user_id, :amount, :amount, :description, :category, :interest, :payoff_date)",
                                  user_id=session.get("user_id"),
                                  amount=float(form_made.amount.data),
                                  description=form_made.description.data,
                                  category=form_made.category.data,
                                  interest=float(form_made.interest.data),
                                  payoff_date=form_made.payoff_date.data)
        # flash message
        flash('Debt has been logged in successfully!', 'success')
    else:
        # flash message
        flash('Invalid debt information. Please try to re-submit.', 'danger')
    # Redirect to dashboard
    return redirect("/")


@app.route("/transactions")
@login_required
def get_transactions():
    # get current user_id
    current_user_id = int(session.get("user_id"))
    # Query 'user' database for all information of current user using lookup
    user = db.execute("SELECT * FROM user WHERE user_id = :user_id",
                        user_id=current_user_id)
    image_file = url_for('static', filename='img/' + user[0]["image_file"])
    # define forms
    form_adex = AddExpenseForm()
    form_adin = AddIncomeForm()
    form_ingo = SetIncomeGoalsForm()
    form_bud = PlanBudgetsForm()
    form_made = ManageDebtForm()

    """Show history of all transactions"""
    # merge 2 tables order by post_date
    transactions = db.execute("SELECT * FROM incomes WHERE user_id = :user_id UNION ALL SELECT * FROM expenses WHERE user_id = :user_id",
                                user_id=current_user_id)

    # query 'debts' table for category & description of all debts
    all_debts = db.execute("SELECT debt_id, (category || ' (' || description || ')') AS choice_description FROM debts WHERE user_id = :user_id",
                            user_id=current_user_id)
    form_adde = AddDebtPaymentForm()
    #passing group_list to the form
    form_adde.debt.choices = [(i['debt_id'], i['choice_description']) for i in all_debts]

    return render_template("transactions.html", user=user, form_adex=form_adex, form_adin=form_adin, form_made=form_made,
                            transactions=transactions, image_file=image_file, form_ingo=form_ingo, form_bud=form_bud, form_adde=form_adde)


@app.route("/register", methods=["GET", "POST"])
def register():
    # get current datetime
    x = datetime.datetime.now()
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash password
        hashed_pw = generate_password_hash(form.password.data)

        # Insert firstName, lastName, email, & hashed_pw into users
        this_user = db.execute("INSERT INTO user (firstName, lastName, email, hashed_pw) VALUES (:firstname, :lastname, :email, :hashed_pw)",
                                  firstname=form.firstname.data,
                                  lastname=form.lastname.data,
                                  email=form.email.data,
                                  hashed_pw=hashed_pw)

        # Remember which user has logged in
        session["user_id"] = this_user

        # Flash success message when redirecting to Dashboard
        flash(f'Account created successfully!', 'success')
        return redirect("/")
    return render_template("register.html", title='Register', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """
    # Forget any user_id
    session.clear()

    form = LoginForm()
    if form.validate_on_submit():
        # Query 'user' database for email address using lookup
        user = db.execute("SELECT * FROM user WHERE email = :email",
                            email=form.email.data)

        # Ensure email exists and password is correct
        if len(user) == 1 and check_password_hash(user[0]["hashed_pw"], form.password.data):
            # Remember which user has logged in
            session["user_id"] = user[0]["user_id"]
            user_firstname = user[0]["firstName"]
            # flash message
            flash(f'Welcome back, {user_firstname}!', 'success')
            # redirect back to the page the user initially tried to access before logging in, if not go to dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect("/")
        else:
            flash('Incorrect Email or Password', 'danger')

    return render_template("login.html", title='Login', form=form)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/account_settings", methods=["GET"])
@login_required
def get_account():
    # get current user_id
    current_user_id = int(session.get("user_id"))
    # Query 'user' database for all information of current user using lookup
    user = db.execute("SELECT * FROM user WHERE user_id = :user_id",
                        user_id=current_user_id)
    image_file = url_for('static', filename='img/' + user[0]["image_file"])
    # define form
    form_adex = AddExpenseForm()
    form_adin = AddIncomeForm()
    form_ingo = SetIncomeGoalsForm()
    form_bud = PlanBudgetsForm()
    form_pw = ResetPasswordForm()
    form_made = ManageDebtForm()

    form = UpdateAccountForm()
    form.firstname.data = user[0]["firstName"]
    form.lastname.data = user[0]["lastName"]
    form.email.data = user[0]["email"]

    """ PAYMENTS TOWARDS DEBT """
    # query 'debts' table for category & description of all debts
    all_debts = db.execute("SELECT debt_id, (category || ' (' || description || ')') AS choice_description FROM debts WHERE user_id = :user_id",
                            user_id=current_user_id)
    form_adde = AddDebtPaymentForm()
    #passing group_list to the form
    form_adde.debt.choices = [(i['debt_id'], i['choice_description']) for i in all_debts]

    return render_template("account_settings.html", title='Account Settings', user=user, image_file=image_file, form=form,
                            form_adex=form_adex, form_adin=form_adin, form_pw=form_pw, form_ingo=form_ingo,
                            form_bud=form_bud, form_made=form_made, form_adde=form_adde)


@app.route("/account_settings/update", methods=["POST"])
@login_required
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            update_picture = db.execute("UPDATE user SET image_file = :image_file WHERE user_id = :user_id",
                                            user_id=int(session.get("user_id")),
                                            image_file=picture_file)
        # Update information in "user" table
        update_user = db.execute("UPDATE user SET firstName = :firstname, lastName = :lastname, email = :email WHERE user_id = :user_id",
                                    user_id=int(session.get("user_id")),
                                    firstname=form.firstname.data,
                                    lastname=form.lastname.data,
                                    email=form.email.data)
        # flash message
        flash('Account info updated successfully!', 'success')
    else:
        flash("Sorry, we're unable to update your information.", 'danger')
    return redirect("/account_settings")


@app.route("/account_settings/reset_password", methods=["GET", "POST"])
@login_required
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Query "users" database for hash using lookup
        user = db.execute("SELECT * FROM user WHERE user_id = :user_id",
                              user_id=session.get("user_id"))

        # Ensure current password is entered correctly
        if not check_password_hash(user[0]["hashed_pw"], form.current_password.data):
            flash('Current Password is invalid. Please re-enter', 'danger')
            return redirect("/account_settings")
        else:
            # Hash new password
            hashed_pw = generate_password_hash(form.new_password.data)
            # Update password in "user" table
            update_hash = db.execute("UPDATE user SET hashed_pw = :hashed_pw WHERE user_id = :user_id",
                                    user_id=int(session.get("user_id")),
                                    hashed_pw=hashed_pw)
        # flash message
        flash('Password has been updated successfully!', 'success')
    else:
        flash("Sorry, we're unable to reset your password.", 'danger')

    return redirect("/account_settings")


@login_required
def apology(message, code=400):
    # get current user_id
    current_user_id = int(session.get("user_id"))
    # Query 'user' database for all information of current user using lookup
    user = db.execute("SELECT * FROM user WHERE user_id = :user_id",
                        user_id=current_user_id)
    image_file = url_for('static', filename='img/' + user[0]["image_file"])
    # define form
    form_adex = AddExpenseForm()
    form_adin = AddIncomeForm()
    form_ingo = SetIncomeGoalsForm()
    form_bud = PlanBudgetsForm()
    form_pw = ResetPasswordForm()
    form_made = ManageDebtForm()
    # query 'debts' table for category & description of all debts
    all_debts = db.execute("SELECT debt_id, (category || ' (' || description || ')') AS choice_description FROM debts WHERE user_id = :user_id",
                            user_id=session.get("user_id"))
    form_adde = AddDebtPaymentForm()
    #passing group_list to the form
    form_adde.debt.choices = [(i['debt_id'], i['choice_description']) for i in all_debts]
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message), user=user, form_adex=form_adex, form_adin=form_adin, form_made=form_made,
                            image_file=image_file, form_ingo=form_ingo, form_bud=form_bud, form_adde=form_adde), code


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
