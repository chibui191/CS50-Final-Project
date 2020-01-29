from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from cs50 import SQL
from flask import session
from flask_session import Session

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///moneymanager.db")

class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=1, max=25)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register Account')

    def validate_email(self, email):
        # Query 'user' database for email address using lookup
        user = db.execute("SELECT * FROM user WHERE email = :email",
                            email=email.data)
        if len(user) > 0:
            raise ValidationError('Email address already exists.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class UpdateAccountForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=1, max=25)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        # Query 'user' database for current info of this user
        user = db.execute("SELECT * FROM user WHERE user_id = :user_id",
                            user_id=int(session.get("user_id")))
        # if input email is different from current email address on database:
        if email.data != user[0]["email"]:
            # Query 'user' database to see if input email already exists
            input_email = db.execute("SELECT * FROM user WHERE email = :email", email=email.data)
            # if yes
            if len(input_email) != 0:
                raise ValidationError('This email address is taken. Please choose a different one.')


class AddExpenseForm(FlaskForm):
    amount = DecimalField('Amount US$', validators=[DataRequired()], places=2)
    description = StringField('Description', validators=[DataRequired(), Length(min=1, max=100)])
    category = SelectField('Category', choices=[('Clothing', 'Clothing'), ('Education', 'Education'), ('Entertainment', 'Entertainment'), ('Food & Drink', 'Food & Drink'),
                                                ('Health & Beauty', 'Health & Beauty'), ('Home', 'Home'), ('Investment', 'Investment'), ('Payments', 'Payments'),
                                                ('Subscriptions', 'Subscriptions'), ('Auto & Transportations', 'Auto & Transportations'), ('Others', 'Others')], validators=[DataRequired()])
    status = BooleanField('Paid?')
    payment_method = SelectField('Payment Method', choices=[('Cash','Cash'), ('Credit','Credit'), ('Debit','Debit'), ('Wire Transfer','Wire Transfer'),
                                                ('Digital Wallet','Digital Wallet'), ('Money Order','Money Order'), ('Check','Check'), ('Others','Others')])
    post_date = DateField('Payment Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Add')

    def validate_amount(self, amount):
        try:
            float(amount.data)
        except ValueError:
            raise ValidationError('Please enter valid numeric value.')


class AddIncomeForm(FlaskForm):
    amount = DecimalField('Amount US$', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), Length(min=1, max=100)])
    category = SelectField('Category', choices=[('Award', 'Award'), ('Gift', 'Gift'), ('Investment', 'Investment'), ('Salary', 'Salary'),
                                                ('Refund/Reimbursement', 'Refund/Reimbursement'), ('Others', 'Others')], validators=[DataRequired()])
    status = BooleanField('Received?')
    payment_method = SelectField('Payment Method', choices=[('Cash','Cash'), ('Wire Transfer','Wire Transfer'),
                                                            ('Digital Wallet','Digital Wallet'), ('Check','Check'), ('Others','Others')])
    post_date = DateField('Receive Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Add')

    def validate_amount(self, amount):
        try:
            float(amount.data)
        except ValueError:
            raise ValidationError('Please enter valid numeric value.')


class ResetPasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Reset Password')


class SetIncomeGoalsForm(FlaskForm):
    goal_type = SelectField('Set Goal By Category/Total', choices=[('Award', 'Award'), ('Gift', 'Gift'), ('Investment', 'Investment'), ('Salary', 'Salary'),
                                                                    ('Refund/Reimbursement', 'Refund/Reimbursement'), ('Others', 'Others'),
                                                                    ('Total', 'Total')], validators=[DataRequired()])
    amount = DecimalField('Amount US$', validators=[DataRequired()], places=2)
    target_month = SelectField('Target Month', choices=[('01', 'January'), ('02', 'February'), ('03', 'March'),  ('04', 'April'),
                                                         ('05', 'May'), ('06', 'June'),  ('07', 'July'), ('08', 'August'),  ('09', 'September'),
                                                           ('10', 'October'), ('11', 'November'),  ('12', 'December')], validators=[DataRequired()])
    target_year = SelectField('Target Year', choices=[('2020', '2020'), ('2021', '2021'), ('2022', '2022'),  ('2023', '2023'),
                                                         ('2024', '2024'), ('2025', '2025'),  ('2026', '2026'), ('2027', '2027'),  ('2028', '2028'),
                                                           ('2029', '2029'), ('2030', '2030')], validators=[DataRequired()])

    submit = SubmitField('Set')

    def validate_amount(self, amount):
        try:
            float(amount.data)
        except ValueError:
            raise ValidationError('Please enter valid numeric value.')


class PlanBudgetsForm(FlaskForm):
    budget_type = SelectField('Plan Budget By Category/Total', choices=[('Clothing', 'Clothing'), ('Education', 'Education'), ('Entertainment', 'Entertainment'), ('Food & Drink', 'Food & Drink'),
                                                                        ('Health & Beauty', 'Health & Beauty'), ('Home', 'Home'), ('Investment', 'Investment'), ('Payments', 'Payments'),
                                                                        ('Subscriptions', 'Subscriptions'), ('Auto & Transportations', 'Auto & Transportations'), ('Others', 'Others'), ('Total', 'Total')], validators=[DataRequired()])
    amount = DecimalField('Amount US$', validators=[DataRequired()], places=2)
    target_month = SelectField('Target Month', choices=[('01', 'January'), ('02', 'February'), ('03', 'March'),  ('04', 'April'),
                                                         ('05', 'May'), ('06', 'June'),  ('07', 'July'), ('08', 'August'),  ('09', 'September'),
                                                           ('10', 'October'), ('11', 'November'),  ('12', 'December')], validators=[DataRequired()])
    target_year = SelectField('Target Year', choices=[('2020', '2020'), ('2021', '2021'), ('2022', '2022'),  ('2023', '2023'),
                                                         ('2024', '2024'), ('2025', '2025'),  ('2026', '2026'), ('2027', '2027'),  ('2028', '2028'),
                                                           ('2029', '2029'), ('2030', '2030')], validators=[DataRequired()])

    submit = SubmitField('Set')

    def validate_amount(self, amount):
        try:
            float(amount.data)
        except ValueError:
            raise ValidationError('Please enter valid numeric value.')


class ManageDebtForm(FlaskForm):
    amount = DecimalField('Balance Owed - US$', validators=[DataRequired(), NumberRange(min=0)])
    description = StringField('Description', validators=[DataRequired(), Length(min=1, max=30)])
    category = SelectField('Category', choices=[('Auto Loans', 'Auto Loans'), ('Credit Cards', 'Credit Cards'), ('Mortgages', 'Mortgages'), ('Student Loans', 'Student Loans'),
                                                ('Others', 'Others')], validators=[DataRequired()])
    interest = DecimalField('Annual Interest Rate %')
    payoff_date = DateField('Target Payoff Date', format='%Y-%m-%d')
    submit = SubmitField('Manage Debt Payoff')

    def validate_amount(self, amount):
        try:
            float(amount.data)
        except ValueError:
            raise ValidationError('Please enter valid numeric value.')
    def validate_interest(self, interest):
        try:
            float(interest.data)
        except ValueError:
            raise ValidationError('Please enter valid numeric value.')

class AddDebtPaymentForm(FlaskForm):
    amount = DecimalField('Amount US$', validators=[DataRequired()])
    payment_date = DateField('Payment Date', format='%Y-%m-%d', validators=[DataRequired()])
    debt = SelectField('Towards', choices=[], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Payment')
    def validate_amount(self, amount):
        try:
            float(amount.data)
        except ValueError:
            raise ValidationError('Please enter valid numeric value.')