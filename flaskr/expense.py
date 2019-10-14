from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

from flask_table import Table, Col, LinkCol

bp = Blueprint('expense', __name__)


class ItemTable(Table):
    id = Col('Id', show=False)
    date_entered = Col('Date')
    payee = Col('Payee')
    category = Col('Category')
    sub_category = Col('Sub Category')
    owner = Col('Owner')
    amount = Col('+/-')
    RunningTotal = Col('Balance')
    edit = LinkCol('Edit', 'expense.update', url_kwargs=dict(id='id'))


class TrackerTable(Table):
    id = Col('Id', show=False)
    date_entered = Col('Date Started')
    item = Col('Item')
    category = Col('Category')
    date_ended = Col('Date Ended')



@bp.route('/tracker')
@login_required
def tracker():
    db =get_db()
    trackers = db.execute(
        'SELECT * FROM tracker'
    ).fetchall()
    trackertable = TrackerTable(trackers, border=True, html_attrs={"style": "font-size: 20px;"})
    return render_template('expense/tracker.html')

@bp.route('/')
@login_required
def index():
    db = get_db()
    expenses = db.execute(
        "SELECT id, date_entered, payee, category, sub_category, owner, amount, "
        "amount+COALESCE((SELECT SUM(amount) FROM expense b WHERE owner_id = ? AND b.id < a.id),0) AS RunningTotal "
        "FROM expense a WHERE owner_id = ? ORDER BY id", (g.user['id'], g.user['id'],)
    ).fetchall()
    table = ItemTable(expenses, border=True, html_attrs={"style": "font-size: 20px;"})
    print(table.__html__())
    return render_template('expense/index.html', table=table)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        payee = request.form['payee']
        category = request.form['category']
        sub_category = request.form['sub_category']
        owner = request.form['owner']
        debt = request.form['debt']
        credit = request.form['credit']
        error = None

        if not payee:
            error = 'Payee is required.'
        elif not category:
            error = 'Category is required.'
        elif not debt and not credit:
            error = 'Must fill in either a debt or credit.'

        if debt != '':
            temp_debt = "-" + str(debt)
            debt = float(temp_debt)
            amount = debt
        else:
            amount = credit

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO expense (payee, category, sub_category, owner, amount, owner_id) VALUES (?, ?, ?, ?, ?, ?)",
                (payee, category, sub_category, owner, amount, g.user['id']))
            db.commit()
            return redirect(url_for('expense.index'))

    return render_template('expense/create.html')


def get_expense(id):
    expense = get_db().execute(
        'SELECT id, date_entered, payee, category, sub_category, owner, amount'
        ' FROM expense'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if expense is None:
        abort(404, "Expense id {0} doesn't exist.").format(id)

    return expense


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    expense = get_expense(id)

    if request.method == 'POST':
        if 'save' in request.form:
            date = request.form['date_entered']
            payee = request.form['payee']
            category = request.form['category']
            sub_category = request.form['sub_category']
            owner = request.form['owner']
            debt = request.form['debt']
            credit = request.form['credit']
            error = None

            if not payee:
                error = 'Payee is required.'
            elif not category:
                error = 'Category is required.'
            elif not debt and not credit:
                error = 'Must have a debt or credit'

            if error is not None:
                flash(error)
            else:
                if debt != '':
                    temp_debt = "-" + str(debt)
                    debt = float(temp_debt)
                    amount = debt
                else:
                    amount = credit
                db = get_db()
                db.execute(
                    'UPDATE expense SET date_entered = ?, payee = ?, category = ?, sub_category = ?, owner = ?, amount = ?'
                    ' WHERE id = ?',
                    (date, payee, category, sub_category, owner, amount, id)
                )
                db.commit()
                return redirect(url_for('expense.index'))
        elif 'cancel' in request.form:
            return redirect(url_for('expense.index'))

    return render_template('expense/update.html', expense=expense)


@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    get_expense(id)
    db = get_db()
    db.execute('DELETE FROM expense WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('expense.index'))
