from flask import flash, redirect, render_template, request, url_for
from flask import session as login_session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import exc
import functools

from stations.auth import bp
from stations.models.databases import User, Role, Data
from stations.extensions import db

# Standard login page


@bp.route('/login', methods=('GET', 'POST'))
def login():
    error = None

    if request.method == 'POST':
        mail = request.form['email']
        passwd = request.form['password']

        user = User.query.filter_by(email=mail).all()

        if len(user) == 0:
            error = 'Utilisateur inconnu.'
        elif not user[0].is_active:
            error = "Votre compte n'est pas encore validé"
        elif not check_password_hash(user[0].password, passwd):
            error = 'Mot de pase incorrect'

        if len(user) > 1:
            error = "Erreur dans la base : il y plus d'un seul utilisateur avec la même adresse."

        if error is None:
            user = user[0]
            login_session['userpseudo'] = user.username
            login_session['userid'] = user.id
            login_session['mail'] = user.email
            if user.data[0].longitude:
                login_session['lon'] = user.data[0].longitude
            else:
                login_session['lon'] = 4.85883
            if user.data[0].latitude:
                login_session['lat'] = user.data[0].latitude
            else:
                login_session['lat'] = 45.76046
            # modify session status
            user.connect = True
            db.session.commit()
            nbroles = len(user.roles)
            if nbroles == 1:
                login_session['role'] = user.roles[0].name
            elif 'roles' not in login_session:
                roles = ()
                for i in range(nbroles):
                    roles += (user.roles[i].name,)
                login_session['roles'] = roles
                login_session['role'] = user.roles[0].name

                return render_template('auth/login.html', roles=roles)
            else:
                login_session['role'] = request.form['role']
                return render_template('explore/index.html')

            return redirect(url_for('explore.index'))
        else:
            flash(error)

    return render_template('auth/login.html')

# registration page with inputs in database
@bp.route('/register', methods=('GET', 'POST'))
def register():
    error = None

    if request.method == 'POST':
        new_user = User(username=request.form['username'],
                        email=request.form['email'],
                        password=request.form['password'],
                        is_connected=0,
                        is_active=0)
        new_user.roles.append(Role(name='user'))
        new_user.data.append(Data(project='Mon projet'))
        if not new_user.username:
            error = "Un pseudo est obligatoire"
            flash(error)
        if not new_user.email:
            error = "Un courriel d'utilisateur est obligatoire."
            flash(error)
        if not new_user.password:
            error = 'Le mot de passe est obligatoire.'
            flash(error)

        if error is None:
            user = User.query.filter_by(email=new_user.email).all()
            firstuser = user[0]
            nameindb = firstuser.username
            new_user.password = generate_password_hash(request.form['password'])
            try:
                db.session.add(new_user)
                db.session.commit()
            except exc.IntegrityError:
                error = f"L'utilisateur {nameindb} est déjà inscrit avec l'adresse {new_user.email}."
                flash(error)
            else:
                return redirect(url_for("auth.login"))

    return render_template('auth/register.html', error=error)

# default logout
@bp.route('/logout')
def logout():
    users = User.query.filter_by(username=login_session['userpseudo']).all()
    users[0].connect = False
    db.session.commit()
    login_session.clear()

    return redirect(url_for('main.index'))

# control function for valid login
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if login_session is None:
            return redirect(url_for('main.denied'))

        return view(**kwargs)

    return wrapped_view

# control function for valid contrib role
def contrib_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):

        user = User.query.filter_by(id=login_session['userid']).all()

        if login_session is None:
            return redirect(url_for('main.denied'))
        elif login_session['role'] == 'user':
            return redirect(url_for('main.denied'))
        return view(**kwargs)

    return wrapped_view

# control function for valid admin role (not used ?)
def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):

        user = User.query.filter_by(id=login_session['userid']).all()

        if login_session is None:
            return redirect(url_for('auth.index'))
        elif Role.query.filter_by(user_id=user[0].id):
            return redirect(url_for('auth.index'))
        return view(**kwargs)

    return wrapped_view
