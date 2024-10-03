from flask import render_template, request, flash, session, redirect, url_for
from stations.query import bp
from stations.auth.routes import login_required

import SPARQLWrapper
from SPARQLWrapper import SPARQLWrapper, JSON

# -------------------------
# Model request management
# Routes for jobs
# -------------------------
@bp.route('/modmeti', methods=('GET', 'POST'))
@login_required
def metimod():
    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    joblist = []
    if request.method == 'POST':
        letters = request.form['startjob']
        if len(letters) == 0:
            listmetiquery = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX schema: <http://schema.org/>
            SELECT ?nomMetier ?Id WHERE {
                ?Id a schema:Occupation ;
                rdfs:label ?nomMetier .
            }
            ORDER BY REPLACE(LCASE(str(?nomMetier)),"é","e")
            """
        else:
            listmetiquery = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX schema: <http://schema.org/>
            SELECT ?nomMetier ?Id WHERE {
                ?Id a schema:Occupation ;
                rdfs:label ?nomMetier .
                FILTER(strStarts( ?nomMetier, '""" + letters + """' ) ) .
            }
            ORDER BY REPLACE(LCASE(str(?nomMetier)),"é","e")
            """

        session['letters'] = letters

        remote.setQuery(listmetiquery)
        remote.setReturnFormat(JSON)
        joblist = remote.queryAndConvert()['results']['bindings']

    return render_template('query/models/metiers/modmeti.html', joblist=joblist)

# ---------------------------
# Model request management
# Routes for jobs descriptors
# ---------------------------
@bp.route('/moddescmeti', methods=('GET', 'POST'))
@login_required
def descmetimod():

    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")
    remote.setReturnFormat(JSON)

    if request.method == 'POST':
        letters = request.form['startjob']
        session['letters'] = letters
    else:
        letters = session.get('letters', 'acces')

    job = request.args['thisJob']
    jobname = request.args['thisJobName']

    if len(letters) == 0:
        listmeti = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <http://schema.org/>
        SELECT ?nomMetier ?Id WHERE {
            ?Id a schema:Occupation ;
            rdfs:label ?nomMetier .
        }
        ORDER BY REPLACE(LCASE(str(?nomMetier)),"é","e")
        """
    else:
        listmeti = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <http://schema.org/>
        SELECT ?nomMetier ?Id WHERE {
            ?Id a schema:Occupation ;
            rdfs:label ?nomMetier .
            FILTER(strStarts( ?nomMetier, '""" + letters + """' ) )
        }
        ORDER BY REPLACE(LCASE(str(?nomMetier)),"é","e")
        """

    descmeti = """
    PREFIX reegle: <http://reegle.info/schema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    PREFIX trmpfi: <http://tremplin.ens-lyon.fr/rules/>
    PREFIX trmpo: <http://www.onisep.fr/objects/>
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX doap: <http://usefulinc.com/ns/doap#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX seo: <https://w3id.org/seo#>
    PREFIX cito: <http://purl.org/spar/cito/>
    SELECT ?nomMetier ?altNames ?secteurs ?niveauAcces  ?accroche
    ?shorterDesc ?shortDesc ?metAss ?formations ?formids WHERE {
        <""" + job + """> rdfs:label ?nomMetier ;
        seo:Flyer ?accroche .
        OPTIONAL {
            SELECT (group_concat(?metAss;separator=", ") as ?metAsss) WHERE {
                <""" + job + """> cito:linksTo ?linkedJob .
                ?linkedJob trmpfi:metAssLabel ?metAss .
            }
        }
        {
            SELECT ?niveauAcces WHERE {
                <""" + job + """> rdfs:educationLevel ?niv .
                ?niv rdfs:label ?niveauAcces  .
            }
        }
        {
            SELECT ?shorterDesc WHERE {
                <""" + job + """> doap:description ?alldesc .
                ?alldesc  dcterms:identifier "FicheMetierDocumentation" ;
                dcterms:description ?shorterDesc .
            }
        }
        {
            SELECT ?shortDesc WHERE {
                <""" + job + """> doap:description ?alldesc .
                ?alldesc dcterms:identifier "DicoDesMetiers" ;
                dcterms:description ?shortDesc .
            }
        }
        {
            SELECT (group_concat(?altName;separator=", ") as ?altNames)  WHERE {
                <""" + job + """> schema:alternateName ?altName
            }
        }
        {
            SELECT (group_concat(?sectname;separator=", ") as ?secteurs)  WHERE {
                <""" + job + """> reegle:sector ?secteur .
                ?secteur rdfs:label ?sectname .
            }
        }
        {
            SELECT (GROUP_CONCAT(CONCAT(?formation, "->", ?formid); separator="$ ") as ?formations)  
            (GROUP_CONCAT(?formid; separator="$ ") AS ?formids) WHERE {
                <""" + job + """> schema:qualifications ?cursus .
                ?cursus rdfs:label ?formation ;
                dcterms:identifier ?formid .
            }
        }
    }
    """

    remote.setQuery(listmeti)
    joblist = remote.queryAndConvert()['results']['bindings']

    remote.setQuery(descmeti)
    jobdesc = remote.queryAndConvert()['results']['bindings']

    # creation de la liste des codes depuis la string contenant cette liste issue de la requête
    rawlistformcode = jobdesc[0]['formids']['value']
    listformcode = rawlistformcode.split('$ ')

    # Calcul du nombre de formations correspondant à un code -> graphe formations
    listnbform = []
    text = ""
    i = 0
    for code in listformcode:
        countform = """
        PREFIX schema: <http://schema.org/>
        SELECT (COUNT(?s) AS ?nbformations)  WHERE {
            ?s schema:relatedLink <trmpo:""" + code + """> .
        }
        """

        remote.setQuery(countform)
        listnbform.append([code, remote.queryAndConvert()['results']['bindings'][0]['nbformations']['value']])
        if i == 0:
            text += remote.queryAndConvert()['results']['bindings'][0]['nbformations']['value']
        else:
            text += ', ' + remote.queryAndConvert()['results']['bindings'][0]['nbformations']['value']
        i += 1

    jobdesc[0]['formids']['value'] = text

    return render_template('query/models/metiers/modmeti_desc.html',
                           job=job,
                           jobname=jobname,
                           joblist=joblist,
                           jobdesc=jobdesc,
                           listnbform=listnbform)

# ---------------------------
# Model request management
# Routes for activity sectors
# ---------------------------
@bp.route('/mod1meti', methods=('GET', 'POST'))
@login_required
def metimod1():

    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    sectlist = []

    if request.method == 'POST':
        sletters = request.form['startsect']

        if len(sletters) == 0:
            listsect = """
            PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX schema: <http://schema.org/>
            PREFIX reegle: <http://reegle.info/schema#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            SELECT DISTINCT ?secteur ?sectid WHERE {
                ?s rdf:type schema:Occupation ;
                reegle:sector ?datasect .
                ?datasect rdfs:label ?secteur ;
                dcterms:identifier ?sectid .
            }
            ORDER BY REPLACE(LCASE(str(?secteur)),"é","e")
            """

        else:
            listsect = """
            PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX schema: <http://schema.org/>
            PREFIX reegle: <http://reegle.info/schema#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            SELECT DISTINCT  ?secteur ?sectid WHERE {
                ?s rdf:type schema:Occupation ;
                reegle:sector ?datasect .
                ?datasect rdfs:label ?secteur ;
                dcterms:identifier ?sectid .
                FILTER(strStarts( ?secteur, '""" + sletters + """' ) )
            }
            ORDER BY REPLACE(LCASE(str(?secteur)),"é","e")
            """
        session['sletters'] = sletters

        remote.setQuery(listsect)
        remote.setReturnFormat(JSON)
        sectlist = remote.queryAndConvert()['results']['bindings']

    return render_template('query/models/metiers/mod1meti.html', sectlist=sectlist)

# ---------------------------------------
# Model request management
# Routes for activity sectors descritions
# ---------------------------------------
@bp.route('/mod1descmeti', methods=('GET', 'POST'))
@login_required
def descmetimod1():
    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    if request.method == 'POST':
        sletters = request.form['startsect']
        session['sletters'] = sletters
    else:
        sletters = session.get('sletters')

    sect = request.args['thisSect']
    sectid = request.args['thisSectId']

    if len(sletters) == 0:
        listsect = """
        PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <http://schema.org/>
        PREFIX reegle: <http://reegle.info/schema#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT DISTINCT  ?secteur ?sectid WHERE {
            ?s rdf:type schema:Occupation ;
                reegle:sector ?datasect .
            ?datasect rdfs:label ?secteur ;
                    dcterms:identifier ?sectid .
        }
        ORDER BY REPLACE(LCASE(str(?secteur)),"é","e")
        """
    else:
        listsect = """
        PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <http://schema.org/>
        PREFIX reegle: <http://reegle.info/schema#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT DISTINCT  ?secteur ?sectid WHERE {
            ?s rdf:type schema:Occupation ;
                reegle:sector ?datasect .
            ?datasect rdfs:label ?secteur ;
                dcterms:identifier ?sectid .
        FILTER(strStarts( ?secteur, '""" + sletters + """' ) ) .
        }
        ORDER BY REPLACE(LCASE(str(?secteur)),"é","e")
        """

    descsectmeti = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX reegle: <http://reegle.info/schema#>
    PREFIX doap: <http://usefulinc.com/ns/doap#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    PREFIX trmpfi: <http://tremplin.ens-lyon.fr/rules/>
    PREFIX seo: <https://w3id.org/seo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT ?Id ?nomMetier ?niveauAcces  ?accroche ?shorterDesc WHERE {
        ?Id rdf:type schema:Occupation ;
            rdfs:label ?nomMetier ;
            seo:Flyer ?accroche ;
            dcterms:identifier ?idMetier .
        {
            SELECT ?Id ?datasect WHERE {
                    ?Id reegle:sector ?datasect .
                    ?datasect dcterms:identifier '""" + sectid + """' .
            }
        }
        {
            SELECT ?Id ?shorterDesc WHERE {
                ?Id doap:description ?description .
                ?description dcterms:identifier "FicheMetierDocumentation" ;
                dcterms:description ?shorterDesc .
            }
            }
        {
            SELECT ?Id ?niveauAcces WHERE {
                ?Id schema:educationalLevel ?niv .
                ?niv rdfs:label ?niveauAcces  .
            }
        }
    }
    ORDER BY REPLACE(LCASE(str(?niveauAcces)),"é","e")
    """

    remote.setQuery(listsect)
    remote.setReturnFormat(JSON)
    sectlist = remote.queryAndConvert()['results']['bindings']

    remote.setQuery(descsectmeti)
    remote.setReturnFormat(JSON)
    sectmetidesc = remote.queryAndConvert()['results']['bindings']

    return render_template('query/models/metiers/mod1meti_desc.html', sect=sect, sectmetidesc=sectmetidesc,
                           sectlist=sectlist)

# ------------------------------
# Model request management
# Routes for centers of interest
# ------------------------------
@bp.route('/mod2meti', methods=('GET', 'POST'))
@login_required
def metimod2():
    listchoices = []
    listlabels = []
    selectjobs = []

    if request.method == 'POST':
        listchoices = request.form.getlist('c_int')

        if not listchoices:
            return render_template('common/emptyRequest.html')
        else:
            llist = len(listchoices)
            choices = " '" + listchoices[0] + "'"

            for i in range(1, llist):
                choices += ", '" + listchoices[i] + "'"

            session['choices'] = choices

            return redirect(url_for('query.descmetimod2'))

    return render_template('query/models/metiers/mod2meti.html', listchoices=listchoices)

# ------------------------------------------
# Model request management
# Routes for centers of interest description
# ------------------------------------------
@bp.route('/mod2descmeti', methods=('GET', 'POST'))
@login_required
def descmetimod2():
    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    choices = session['choices']

    qlabelscint = """
    PREFIX being: <http://contextus.net/ontology/ontomedia/ext/common/being#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?cilabel WHERE {
        ?s being:will-do ?ci .
        ?ci dcterms:identifier ?value ;
            rdfs:label ?cilabel .
        FILTER (?value IN (""" + choices + """)) .
    }
    """
    #
    qselectjobs = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX being: <http://contextus.net/ontology/ontomedia/ext/common/being#>
    PREFIX schema: <http://schema.org/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT DISTINCT ?Metier ?Id ?cinterets ?nbCinterets WHERE {
        ?Id rdf:type schema:Occupation ;
            rdfs:label ?Metier .
        {
            SELECT ?Id (group_concat(?cinteret; separator = ", ") as ?cinterets)
            (COUNT(?cinteret) AS ?nbCinterets)  WHERE {
                ?Id being:will-do ?ci .
                ?ci dcterms:identifier ?value ;
                    rdfs:label ?cinteret .
                FILTER (?value IN (""" + choices + """))
            }
            GROUP BY ?Id
        }
        #FILTER(?nbCinterets >= 2)
    }
    ORDER BY DESC(?nbCinterets)
    """

    remote.setQuery(qlabelscint)
    remote.setReturnFormat(JSON)
    listlabels = remote.queryAndConvert()['results']['bindings']

    remote.setQuery(qselectjobs)
    remote.setReturnFormat(JSON)
    selectjobs = remote.queryAndConvert()['results']['bindings']

    return render_template('query/models/metiers/mod2meti+desc.html', listlabels=listlabels,
                           selectjobs=selectjobs)

# ---------------------------------
# Model request management OBSOLETE
# kept for further developments
# Routes for formations
# ---------------------------------
@bp.route('/modform', methods=('GET', 'POST'))
@login_required
def formmod():
    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    error = None

    if request.method == 'POST':
        first_param = request.form['param1']
        second_param = request.form['param2']

        if error is None:
            twoparlist = 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \n' + \
                         'PREFIX trmpfi: <http://tremplin.ens-lyon.fr/rules/> \n' + \
                         'SELECT ?' + first_param + ' ?' + second_param + ' WHERE { \n' + \
                         '?' + first_param + ' rdfs:label ?' + second_param + ' . \n' + \
                         '?' + first_param + ' a trmpfi:info . \n' + \
                         '} \n'

            # results = forrdfdb.query(first_query)
            # return render_template('query/idlabel_request.html', results=results)

            remote.setQuery(twoparlist)
            remote.setReturnFormat(JSON)
            parlist = remote.queryAndConvert()['results']['bindings']
    else:
        flash('error')

    return render_template('query/models/formations/modform.html')


# ---------------------------------
# Model request management OBSOLETE
# kept for further developments
# Routes for formations descriptions
# ---------------------------------
@bp.route('/moddescform', methods=('GET', 'POST'))
@login_required
def descformmod():

    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")
    remote.setReturnFormat(JSON)

    formlink = request.args['formlink']

    lon = str(session.get('lon'))
    lat = str(session.get('lat'))
    alldist = []

    descform = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX schema: <http://schema.org/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
    PREFIX trmpo: <http://www.onisep.fr/http/redirection/metier/slug/>
    PREFIX uom: <http://www.opengis.net/def/uom/OGC/1.0/>
    SELECT ?desc ?educationalLevel ?region ?ville ?etablissement ?duree ?scolmod ?enseign ?heberg ?statut ?cout ?siteweb ?pageweb ?dist WHERE { 
        ?s schema:relatedLink <trmpo:""" + formlink + """> ;
        rdfs:label ?desc ;
        schema:educationalLevel ?educationalLevel ;
        schema:AdministrativeArea ?region ;
        schema:City ?ville ;
        schema:provider ?etablissement ;
        schema:timeToComplete ?duree ;
        schema:eventAttendanceMode ?scolmod ;
        schema:teaches ?enseign ;
        schema:Accommodation ?heberg ;
        schema:funder ?statut ;
        schema:estimatedCost ?cout ;
        schema:WebSite ?siteweb ;
        schema:WebPage ?pageweb ;
        geo:hasGeometry ?geom .
        ?geom  geo:asWKT ?pWKT .
        BIND (geof:distance("<http://www.opengis.net/def/crs/EPSG//1.3/CRS84> POINT(""" + lon + " " + lat + """)", ?pWKT, uom:metre) as ?dist) .
    }
    ORDER BY ?region 
    """

    remote.setQuery(descform)
    formdesc = remote.queryAndConvert()['results']['bindings']

    if not formdesc:
        return render_template('common/emptyRequest.html')
    else:
        formname = formdesc[0]['desc']['value']
        educlevel = formdesc[0]['educationalLevel']['value']
        duration = formdesc[0]['duree']['value']

        for i in range(len(formdesc)):
            distance = int(float(formdesc[i]['dist']['value']) / 1000)
            formdesc[i]['dist']['value'] = distance

        return render_template('query/models/formations/modform_desc.html', formdesc=formdesc,
                               formname=formname,
                               educlevel=educlevel,
                               duration=duration)


# ---------------------------------
# Model request management OBSOLETE
# kept for further developments
# Routes for institutions
# ----------------------------------
@bp.route('/modetab', methods=('GET', 'POST'))
@login_required
def etabmod():
    return render_template('query/models/etablissements/modetab.html')


# ------------------------------------
# Model request management OBSOLETE
# kept for further developments
# Routes for institutions descriptions
# ------------------------------------
@bp.route('/auto_modelrq', methods=('GET', 'POST'))
@login_required
def auto_modelrq():
    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    first_query = 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \n' + \
                  'PREFIX trmpfi: <http://tremplin.ens-lyon.fr/rules/> \n' + \
                  'SELECT ?predicate ?label WHERE { \n' + \
                  '?predicate rdfs:label ?label ; \n' + \
                  '           a trmpfi:info .  \n' + \
                  '} \n'

    remote.setQuery(first_query)
    remote.setReturnFormat(JSON)
    results = remote.queryAndConvert()['results']['bindings']
    # results = prerdfdb.query(first_query)

    return render_template('query/idlabel_request.html', results=results)

