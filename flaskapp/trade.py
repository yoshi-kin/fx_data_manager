from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_paginate import Pagination, get_page_parameter
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort
from flaskapp.auth import login_required
from flaskapp.db import get_db
import datetime

bp = Blueprint('trade', __name__, url_prefix='/trade')


@bp.route('/history', methods=('GET', 'POST'))
@login_required
def history():
    db = get_db()
    trades = db.execute(
            'SELECT * FROM trade ORDER BY date DESC'
        ).fetchall()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    page_trades = trades[(page-1)*per_page: page*per_page]
    pagination = Pagination(page=page, total=len(trades), per_page=per_page, css_framework='bootstrap4')
    return render_template('trade/history.html', trades=page_trades, pagination=pagination)


@bp.route('/dashboard', methods=('GET', 'POST'))
@login_required
def dashboard():
    db = get_db()
    trades = db.execute(
            'SELECT * FROM trade ORDER BY date ASC'
        ).fetchall()
    dates = []
    results = []
    result_sum = 0
    each_result = []
    win = []
    lose = []
    win_count = 0
    lose_count = 0
    for trade in trades:
        date = datetime.datetime.strftime(trade['date'], '%Y-%m-%d')
        dates.append(date)
        result_sum = result_sum + trade['result']
        results.append(result_sum)
        each_result.append(trade['result'])
        if trade['result']> 0:
            win.append(trade['result'])
            win_count += 1
        elif trade['result'] < 0:
            lose.append(trade['result'])
            lose_count += 1
    all_sum = sum(each_result)
    win_sum = round(sum(win) / win_count, 1)
    lose_sum = round(sum(lose) / lose_count, 1)
    trade_count = len(results)
    win_ratio = round(win_count / trade_count * 100, 1)
    risk_reward = abs(round(win_sum / lose_sum, 1))



    return render_template('trade/dashboard.html', dates=dates, results=results, all_sum=all_sum, win_sum=win_sum, lose_sum=lose_sum, trade_count=trade_count, win_ratio=win_ratio,risk_reward=risk_reward)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        date = request.form['date']
        pare = request.form['pare']
        amount = request.form['amount']
        result = request.form['result']

        db = get_db()
        db.execute(
            'INSERT INTO trade (user_id, date,   pare, amount, result)'
            'VALUES (?,?,?,?,?)',(g.user['id'], date, pare, amount, result)
        )
        db.commit()
        return redirect(url_for('trade.history'))

    return render_template('trade/create.html')


def get_trade(id):
    db = get_db()
    trade = db.execute(
        'SELECT date, pare, amount, result FROM trade WHERE id = ?', (id,)
    ).fetchone()
    if trade is None:
        abort(404, 'There is not such a trade')
    return trade


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    trade = get_trade(id)
    if request.method == 'POST':       
        date = request.form['date']
        pare = request.form['pare']
        amount = request.form['amount']
        result = request.form['result']
        db = get_db()
        db.execute(
            'UPDATE trade SET date=?, pare=?, amount=?, result=? WHERE id=?', (date, pare, amount, result, id)
        )
        db.commit()
        return redirect(url_for('trade.history'))
    return render_template('trade/update.html', trade=trade)

@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM trade WHERE id = ?', (id,))
    db.commit()

    return redirect(url_for('trade.history'))

