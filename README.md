======================
Project: MoneyManager
======================
This is a personal finance web application that allows users to track their income streams and expenses on a monthly basis,
as well as to manage any outstanding debts they might have.


=============
Requirements
=============
1. cs50
2. Flask
3. Flask-Session
4. requests
5. flask-wtf


===========
Built With
===========
1. Flask
2. Bootstrap theme - SB Admin 2 (https://startbootstrap.com/themes/sb-admin-2/)
3. SQLite


=======
Author
=======
- Chi Phuong Bui


===============
Program Design
===============

1. REGISTER page
---------
Features:
---------
This page allows user to create an account with MoneyManager. They're asked to provide First Name, Last Name, Email Address, and
set a Password for their account. Email address used to register must not yet exist on our database. Upon finishing the Registration,
user will be directed to their personal Dashboard page without having to log in again.

1. LOG IN page
---------
Features:
---------
This page allows user to log in their account. User are asked to provide email address and password. If they don't have an account
yet and would like to have one, they can click on 'Create an Account!,' which would direct them to the Register page.
------------
Limitations:
------------
Users are not able to access their accounts if they forgot their passwords yet. To reduce the chance of people losing their accounts,
I have designed this program so that users need to use a valid email address to log in (instead of a username) because people are
less likely to forget their emails.


1. DASHBOARD page
---------
Features:
---------
This is where the current statuses of user's income(s) and expense(s), goals, budgets, as well as debt management information
are displayed.
- On the top are "Total Incomes," "Total Expenses," "Total Debts (due in this month)," and "Current Balance."
Total Incomes is the sum of all income amounts that the user has logged in for the current month. Similarly, Total Expenses sum
of all expenses. Total Debts (due this month) is the sum of all the debt(s) that user has logged in with Target Payoff Date in current
month. Finally, Current Balance is what is left from all incomes after expenses and debt payments that was made in that month.
- Then a bit further down, we have 3 collapsable bars, each, upon expanding, would display information in regards to Income Goals,
Planned Budgets and Debt Management, respectively.
- On the navigation bar on the left hand side, user can find "Add" and "Set Goals" buttons which allows them to log in their income and
expenses, as well as setting income goals and planning their budgets for the month. Every time they log in a transaction, all the
numbers displayed on Dashboard page would be adjusted accordingly. If the income or expense logged in is part of their goals/budgets
for the month, percentage on progress bar would also be updated to make it visually easier for users to see where they stand in terms
of their goals. Users can easily access 'Add' and 'Set Goals' buttons from other pages like 'Transactions' and 'Account Settings.'
- At the very bottom is Debt Management, specifically designed for people who want to set goals to pay off their debts before a certain
date. Once user enter Balance Owed amount, Category, Description, Annual Interest Rate, Target Payoff Date, the app will automatically
provide estimated amount of money to be paid each month for users to reach their goals. Every time a 'Payment towards Debt'
is added in, the progress percentage of that debt will also be updated automatically to give user an idea of how much they've paid
and how much they have left. Once the debt is paid off 100%, it would be removed out of the table. User can only log in payments towards
debts that they have added into the Debt Management section previously.
------------
Limitations:
------------
- Users are not yet able to edit their goals/budgets individually from Dashboard page. For now, the only way for to update the
money amount for a goal/budget is by setting another goal/budget for an amount of the difference. For example,
if I currently have an Income Goal of $2,000 from Investment, and I would like to change it to $1,500 only, I would then need to go
into 'Set Goals,' and set another Income Goal for Investment of -$500 for the same month/year. And if I want to delete this goal
altogether, I would need to do the same, but with an amount of -$2,000. This is not really a very convenient way to edit goals
and budgets.
- In addition, Dashboard only displays the information for the current month and year. Users are not yet able to see the summaries
for other months.
=> The goal is to have these features ready by the next update of the program.


2. TRANSACTIONS page
---------
Features:
---------
This is a list of all the income(s) and expense(s) that user have logged in. There're a total of 6 columns - Category, Description,
Amount, Payment Method, Status, and Date. In addition, a search bar is provided for user to look for specific transactions if they
want. User can also choose to see 10-25-50-100 entries per page.
------------
Limitations:
------------
- There is no record of Payments towards Debts yet.
- Similar to Dashboard's Income Goals & Planned Budgets, users are not yet able to individually edit/delete their transactions if
the information was entered incorrectly.
=> The goal is to have this feature ready by the next update of the program.
- Ideally, users can also upload and store their receipts or any other photos/images related to their transactions if they'd like to.
- Users should also be able to duplicate/clone transactions that are supposed to repeat in the future months so that they don't
have to log those in multiple times.


3. ACCOUNT SETTINGS page
---------
Features:
---------
This page displays user's current personal information (First Name, Last Name, Email Address, and Preferred Currency). They can also
choose to reset their password, edit their information (names), change email address, and/or upload a new profile picture.
------------
Limitations:
------------
In the future updates of this program, users should be able to set their location, preferred currency, and to have the option to have
transaction entries in other currencies converted to their preferred one as well.


-------
OVERALL
-------
Currently the program is still in its very early stages. There're many more features that could have been added to make the logging
and tracking easier for its user. For example, I would like to add another page called Charts or Reports, which is
going to display the percent composition of a user's actual expenses by categories, as well as income/expense changes over time.
Another page would be Personal Finance Advice/Guide, which provides guidance for users that need a bit more assistance (e.g. roughly
how many percent of their incomes should go into each category ideally). Reminders when an user is getting close to their budgets
or debt payment reminders can also be very useful. Savings tracking would be another great feature to have as well.


================
Acknowledgments
================
1. Corey Schafer's Flask Tutorials series (https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH)
2. Mobills - an expense tracker app (https://www.mobillsapp.com/)
3. Mint - Budget Trackers & Planners (https://www.mint.com/)
