from flask import render_template, session, request, flash
from stations.profile import bp
from stations.auth.routes import login_required
from stations.extensions import db
from stations.models.databases import User, Role, Data
@bp.route('/')
def index():

    user = User.query.filter_by(email=session.get('mail')).all()

    if user[0].data[0].longitude:
        session['lon'] = user[0].data[0].longitude
    if user[0].data[0].latitude:
        session['lat'] = user[0].data[0].latitude
    if user[0].data[0].project:
        session['projet'] = user[0].data[0].project
    if user[0].data[0].projectpro:
        session['projetpro'] = user[0].data[0].projectpro
    if user[0].data[0].cint:
        session['cint'] = user[0].data[0].cint
    if user[0].data[0].comp:
        session['comp'] = user[0].data[0].comp

    userdata = [session.get('userpseudo'), session.get('userid'), session.get('mail'), session.get('roles'), session.get('lon'), session.get('lat'), session.get('projet'), session.get('projetpro'), session.get('cint'), session.get('comp')]
    session['userdata'] = userdata

    return render_template('profile/index.html', userdata=userdata)

@bp.route('/modif', methods=('GET', 'POST'))
@login_required
def modif_param():

    userdata = session.get('userdata')
    user = User.query.filter_by(email=userdata[2]).all()

    if request.method == 'POST':
        if request.form['lon']:
            user[0].data[0].longitude = request.form['lon']
            session['lon'] = user[0].data[0].longitude
        if request.form['lat']:
            user[0].data[0].latitude = request.form['lat']
            session['lat'] = user[0].data[0].latitude
        if request.form['formation']:
            user[0].data[0].project = request.form['formation']
            session['projet'] = user[0].data[0].project
        if request.form['profession']:
            user[0].data[0].projectpro = request.form['profession']
            session['projetpro'] = user[0].data[0].projectpro
        if request.form['competences']:
            user[0].data[0].comp = request.form['competences']
            session['comp'] = user[0].data[0].comp

        db.session.commit()

    userdata = [session.get('userpseudo'), session.get('userid'), session.get('mail'), session.get('roles'), session.get('lon'), session.get('lat'), session.get('projet'), session.get('projetpro'), session.get('cint'), session.get('comp')]
    session['userdata'] = userdata


    return render_template('profile/modif.html', userdata=userdata)