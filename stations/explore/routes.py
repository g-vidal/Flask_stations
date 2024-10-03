from flask import render_template, redirect, url_for, request, flash, session
from stations.explore import bp
from stations.auth.routes import login_required, contrib_required

import SPARQLWrapper
from SPARQLWrapper import SPARQLWrapper, JSON, POST

# exploration of data presentation page
@bp.route('/')
def index():
    return render_template('explore/index.html')

# exploration of center of interests presentation page
@bp.route('/base_ci', methods=('GET', 'POST'))
@login_required
def base_ci():
    return render_template('explore/base_ci.html')

#  center of interest ineraction page (!!to be reviewed)
@bp.route('/contrib_ci', methods=('GET', 'POST'))
@contrib_required
def contrib_ci():

    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    if request.method == 'POST':
        if "meti_form" in request.form:
            joblist = []
            proplist = []
            letters = request.form['jobs']
            session['letters'] = letters
            if len(letters) == 0:
                listmetiquery = """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX schema: <http://schema.org/>
                SELECT ?nomMetier ?Id WHERE {
                    ?Id a schema:Occupation;    
                        rdfs:label ?nomMetier .
                }
                ORDER BY REPLACE(LCASE(str(?nomMetier)),"é","e")
                """
            else:
                listmetiquery = """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX schema: <http://schema.org/>
                SELECT ?nomMetier ?Id WHERE {
                    ?Id a schema:Occupation;
                        rdfs:label ?nomMetier
                    FILTER(strStarts( ?nomMetier, '""" + letters + """' ) ) .
                }
                ORDER BY REPLACE(LCASE(str(?nomMetier)),"é","e")
                """

            remote.setQuery(listmetiquery)
            remote.setReturnFormat(JSON)
            joblist = remote.queryAndConvert()['results']['bindings']
            if len(letters) > 0:
                session['joblist'] = joblist
            if 'proplist' in session:
                proplist = session['proplist']
                return render_template('explore/contrib_ci.html', joblist=joblist,
                                       proplist=proplist)
            elif 'searchlist' in session:
                searchlist = session['searchlist']
                return render_template('explore/contrib_ci.html', joblist=joblist,
                                       searchlist=searchlist)
            else:
                return render_template('explore/contrib_ci.html', joblist=joblist)

        elif "allgrp" in request.form:
            allgrplist = []
            listallgrpquery = """
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            SELECT DISTINCT ?group ?idgrp WHERE {
                ?s a "group" ;
                    rdfs:label ?group ;
                    dcterms:identifier ?idgrp .
            }
            ORDER BY REPLACE(LCASE(str(?idgrp)),"é","e") 
            """

            remote.setQuery(listallgrpquery)
            remote.setReturnFormat(JSON)
            allgrplist = remote.queryAndConvert()['results']['bindings']
            if 'joblist' not in session:
                joblist = []
            else:
                joblist = session['joblist']

            return render_template('explore/contrib_ci.html', allgrplist=allgrplist,
                                   joblist=joblist)

        elif "allci" in request.form:
            allcilist = []
            listallciquery = """
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX dcterms: <http://purl.org/dc/terms/>
            SELECT ?ci ?id WHERE {
                ?s a "ci" ;
                    rdfs:label ?ci ;
                    dcterms:identifier ?id .
            }
            ORDER BY REPLACE(LCASE(str(?ci)),"é","e") 
            """

            remote.setQuery(listallciquery)
            remote.setReturnFormat(JSON)
            allcilist = remote.queryAndConvert()['results']['bindings']
            session['allcilist'] = allcilist
            if 'joblist' not in session:
                joblist = []
            else:
                joblist = session['joblist']

            return render_template('explore/contrib_ci.html', allcilist=allcilist,
                                   joblist=joblist)


        elif "contain" in request.form:
            searchlist = []
            searchstr = request.form['filter']
            listcontquery = '''
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            SELECT ?ci ?id WHERE {
                ?s a "ci" ;
                    rdfs:label ?ci ;
                    dcterms:identifier ?id .    
                FILTER (contains (?ci, "''' + searchstr + '''"))
            }
           '''

            remote.setQuery(listcontquery)
            remote.setReturnFormat(JSON)
            searchlist = remote.queryAndConvert()['results']['bindings']
            session['searchlist'] = searchlist
            if 'joblist' not in session:
                joblist = []
            else:
                joblist = session['joblist']

            return render_template('explore/contrib_ci.html', searchlist=searchlist,
                                   joblist=joblist)

        elif "begin" in request.form:
            searchtlist = []
            searchstr = request.form['filter']
            liststartquery = '''
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            SELECT ?ci ?id WHERE {
                ?s a "ci" ;
                    rdfs:label ?ci ;
                    dcterms:identifier ?id .
                FILTER (strstarts (?ci, "''' + searchstr + '''"))
            }
            '''

            remote.setQuery(liststartquery)
            remote.setReturnFormat(JSON)
            searchlist = remote.queryAndConvert()['results']['bindings']
            session['searchlist'] = searchlist
            if 'joblist' not in session:
                joblist = []
            else:
                joblist = session['joblist']

            return render_template('explore/contrib_ci.html', searchlist=searchlist,
                                   joblist=joblist)

        elif "edit_ci" in request.form:

            # Replace values from form

            thislabel = request.form['label']
            searchci = request.form['identifiant']
            thispublisher = request.form['publisher']
            theserelatedjobs = request.form['relatedjobs']
            thiscomment = request.form['comment']

            cireplacequery = '''
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX trmpfi:  <http://tremplin.ens-lyon.fr/rules/> 
            PREFIX dcterms: <http://purl.org/dc/terms/> 
            PREFIX dbp:     <https://dbpedia.org/ontology/> 
            DELETE {            
                ?s rdfs:label ?ci ;
                    rdfs:comment ?comment ;
                    dcterms:publisher ?pub ;
                    dcterms:isRequiredBy ?jobs . 
            }
            INSERT {                
                ?s rdfs:label "''' + thislabel + '''" ;
                    rdfs:comment "''' + thiscomment + '''" ;
                    dcterms:publisher "''' + thispublisher + '''" ;
                    dcterms:isRequiredBy "''' + theserelatedjobs + '''" .            

            }
            WHERE  {                
                    ?s a "ci" ;
                    rdfs:label ?ci ;
                    dcterms:identifier "''' + searchci + '''" .
            }
            '''

            remote.setQuery(cireplacequery)
            remote.setReturnFormat(JSON)
            remote.setMethod(POST)
            rawcireplace = remote.query()

            return render_template('explore/contrib_ci.html')



    elif request.args.get('thisci') is not None:

        proplist = []
        ci_id = request.args['thisci']

        cipropquery = """
        PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX trmpfi:  <http://tremplin.ens-lyon.fr/rules/> 
        PREFIX dcterms: <http://purl.org/dc/terms/> 
        PREFIX dbp:     <https://dbpedia.org/ontology/> 
        SELECT ?s ?ci ?id ?grp ?status ?comment ?pub ?jobs WHERE {
            ?s a "ci" ;
                rdfs:label ?ci ;
                dcterms:identifier '""" + ci_id + """' ;
                dcterms:identifier ?id ;
                dcterms:isPartOf ?grp ;
                dbp:status ?status  ;
                rdfs:comment ?comment ;
                dcterms:publisher ?pub ;
                dcterms:isRequiredBy ?jobs .
        }
        """

        remote.setQuery(cipropquery)
        remote.setReturnFormat(JSON)
        proplist = remote.queryAndConvert()['results']['bindings']

        if 'joblist' not in session:
            joblist = []
        else:
            joblist = session['joblist']
        session['proplist'] = proplist

        return render_template('explore/contrib_ci.html', proplist=proplist,
                               joblist=joblist)


    elif request.args.get('thisgrp') is not None:

        # clic on grp to add CI on this group then add ci in the database with sparql INSERT DATA

        proplist = []
        grp_id = request.args['thisgrp']

        grppropquery = """
        PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX dcterms: <http://purl.org/dc/terms/> 
        SELECT ?ci ?id WHERE {
            ?s a "ci" ;
                rdfs:label ?ci ;
                dcterms:identifier ?id .
            FILTER(strStarts( ?id, '""" + grp_id + """' ) )
        }
        ORDER BY ?id
        """

        remote.setQuery(grppropquery)
        remote.setReturnFormat(JSON)
        proplist = remote.queryAndConvert()['results']['bindings']
        maxplist = len(proplist)
        if maxplist == 0:
            order = 0
        for i in range(maxplist):
            order = int(proplist[i]['id']['value'][6:])
            if order != i + 1:
                if order < 10:
                    identifier = grp_id + '-ci' + '00' + str(order)
                elif order < 100:
                    identifier = grp_id + '-ci' + '0' + str(order)
                else:
                    identifier = grp_id + '-ci' + str(order)
                break

        if order == maxplist:
            order = order + 1
            if order < 10:
                identifier = grp_id + '-ci' + '00' + str(order)
            elif order < 100:
                identifier = grp_id + '-ci' + '0' + str(order)
            else:
                identifier = grp_id + '-ci' + str(order)

        propinsert = """
        PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX trmpfi:  <http://tremplin.ens-lyon.fr/rules/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX dbp:     <https://dbpedia.org/ontology/>
        INSERT DATA {
            trmpfi:gci""" + grp_id[1:] + identifier[3:] + """ a "ci" ;
                               dcterms:identifier   '""" + identifier + """' ;
                               rdfs:label           "Ajouter ici le libellé" ;
                               dcterms:isPartOf     trmpfi:gci""" + grp_id[1:] + """ ;
                               dbp:status           "draft" ;
                               rdfs:comment         "" ;
                               dcterms:publisher    "" ;
                               dcterms:isRequiredBy "" .
        }
        """

        remote.setQuery(propinsert)
        remote.setReturnFormat(JSON)
        remote.setMethod(POST)
        rawpropinsert = remote.query()

        # display new ci on the interface for edition

        cipropquery = """
        PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX trmpfi:  <http://tremplin.ens-lyon.fr/rules/> 
        PREFIX dcterms: <http://purl.org/dc/terms/> 
        PREFIX dbp:     <https://dbpedia.org/ontology/> 
        SELECT ?s ?ci ?id ?grp ?status ?comment ?pub ?jobs WHERE {
            ?s a "ci" ;
                rdfs:label ?ci ;
                dcterms:identifier '""" + identifier + """' ;
                dcterms:identifier ?id ;
                dcterms:isPartOf ?grp ;
                dbp:status ?status  ;
                rdfs:comment ?comment ;
                dcterms:publisher ?pub ;
                dcterms:isRequiredBy ?jobs .
        }
        """

        remote.setQuery(cipropquery)
        remote.setReturnFormat(JSON)
        proplist = remote.queryAndConvert()['results']['bindings']

        if 'joblist' not in session:
            joblist = []
        else:
            joblist = session['joblist']
        session['proplist'] = proplist

        return render_template('explore/contrib_ci.html', proplist=proplist,
                               joblist=joblist)

    return render_template('explore/contrib_ci.html')


@bp.route('/explore_ci', methods=('GET', 'POST'))
@login_required
def explore_ci():

    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    if request.method == 'POST':
        if "allgrp" in request.form:
            allgrplist = []
            listallgrpquery = """
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            SELECT DISTINCT ?group ?idgrp WHERE {
                ?s a "group" ;
                    rdfs:label ?group ;
                    dcterms:identifier ?idgrp .
            }
            ORDER BY REPLACE(LCASE(str(?idgrp)),"é","e")
            """

            remote.setQuery(listallgrpquery)
            remote.setReturnFormat(JSON)
            allgrplist = remote.queryAndConvert()['results']['bindings']
            if 'joblist' not in session:
                joblist = []
            else:
                joblist = session['joblist']

            return render_template('explore/explore_ci.html', allgrplist=allgrplist,
                                   joblist=joblist)

        elif "allci" in request.form:
            allcilist = []
            listallciquery = """
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            SELECT ?ci ?id WHERE {
                ?s a "ci" ;
                    rdfs:label ?ci ;
                    dcterms:identifier ?id .
            }
            ORDER BY REPLACE(LCASE(str(?ci)),"é","e")
            """

            remote.setQuery(listallciquery)
            remote.setReturnFormat(JSON)
            allcilist = remote.queryAndConvert()['results']['bindings']
            session['allcilist'] = allcilist

            return render_template('explore/explore_ci.html', allcilist=allcilist)

        elif "contain" in request.form:
            searchlist = []
            searchstr = request.form['filter']
            listcontquery = '''
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            SELECT ?ci ?id WHERE {
                ?s a "ci" ;
                    rdfs:label ?ci ;
                    dcterms:identifier ?id .
                FILTER (contains (?ci, "''' + searchstr + '''"))
            }
           '''

            remote.setQuery(listcontquery)
            remote.setReturnFormat(JSON)
            searchlist = remote.queryAndConvert()['results']['bindings']
            session['searchlist'] = searchlist
            if 'joblist' not in session:
                joblist = []
            else:
                joblist = session['joblist']

            return render_template('explore/explore_ci.html', searchlist=searchlist)

        elif "begin" in request.form:
            searchtlist = []
            searchstr = request.form['filter']
            liststartquery = '''
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            SELECT ?ci ?id WHERE {
                ?s a "ci" ;
                    rdfs:label ?ci ;
                    dcterms:identifier ?id .
                FILTER (strstarts (?ci, "''' + searchstr + '''"))
            }
            '''

            remote.setQuery(liststartquery)
            remote.setReturnFormat(JSON)
            searchlist = remote.queryAndConvert()['results']['bindings']
            session['searchlist'] = searchlist
            if 'joblist' not in session:
                joblist = []
            else:
                joblist = session['joblist']

            return render_template('explore/explore_ci.html', searchlist=searchlist,
                                   joblist=joblist)

    elif request.args.get('thisci') is not None:

        proplist = []
        ci_id = request.args['thisci']

        cipropquery = """
        PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX trmpfi:  <http://tremplin.ens-lyon.fr/rules/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX dbp:     <https://dbpedia.org/ontology/>
        SELECT ?s ?ci ?id ?grp ?status ?comment ?pub ?jobs WHERE {
            ?s a "ci" ;
                rdfs:label ?ci ;
                dcterms:identifier '""" + ci_id + """' ;
                dcterms:identifier ?id ;
                dcterms:isPartOf ?grp ;
                dbp:status ?status  ;
                rdfs:comment ?comment ;
                dcterms:publisher ?pub ;
                dcterms:isRequiredBy ?jobs .
        }
        """

        remote.setQuery(cipropquery)
        remote.setReturnFormat(JSON)
        proplist = remote.queryAndConvert()['results']['bindings']

        session['proplist'] = proplist
        if 'searchlist' in session:
            searchlist = session['searchlist']
            return render_template('explore/explore_ci.html', proplist=proplist,
                                   searchlist=searchlist)

        if 'allcilist' in session:
            allcislist = session['allcilist']
            return render_template('explore/explore_ci.html', proplist=proplist,
                                   allcislist=allcislist)

        return render_template('explore/explore_ci.html', proplist=proplist)


    elif request.args.get('thisgrp') is not None:

        # clic on grp to list CI from this group

        grpproplist = []
        grp_id = request.args['thisgrp']

        grpquery = """
        PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT ?ci ?id WHERE {
            ?s a "ci" ;
                rdfs:label ?ci ;
                dcterms:identifier ?id .
            FILTER(strStarts( ?id, '""" + grp_id + """' ) )
        }
        ORDER BY ?id
        """

        remote.setQuery(grpquery)
        remote.setReturnFormat(JSON)
        grplist = remote.queryAndConvert()['results']['bindings']
        session['grpproplist'] = grpproplist

        proplist = grpproplist

        return render_template('explore/explore_ci.html', grplist=grplist)

    return render_template('explore/explore_ci.html')


@bp.route('/formations', methods=('GET', 'POST'))
@login_required
def search_formindex():

    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")
    remote.setReturnFormat(JSON)
    param = []
    error = None

    formsdurquery = """
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX schema: <http://schema.org/>
    SELECT DISTINCT ?educationalLevel WHERE {
        ?formation a schema:EducationalOccupationalProgram ;
                   schema:educationalLevel ?educationalLevel.
    }
    ORDER BY ?educationalLevel
    """

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

    listdept = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    PREFIX reegle: <http://reegle.info/schema#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX schema1: <http://schema.org/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    SELECT DISTINCT ?dept WHERE {
        ?s rdf:type schema:EducationalOccupationalProgram ;
        wd:Q6465 ?dept .
    }
    ORDER BY REPLACE(LCASE(str(?dept)),"é","e")
    """
    remote.setQuery(formsdurquery)
    formsdurlist = remote.queryAndConvert()['results']['bindings']

    remote.setQuery(listsect)
    sectlist = remote.queryAndConvert()['results']['bindings']

    remote.setQuery(listdept)
    deptlist = remote.queryAndConvert()['results']['bindings']


    if request.method == 'POST':
        nbchoix = 0
        if request.form['niveau']:
            niv = request.form['niveau']
        if request.form.getlist('status'):
            status = request.form.getlist('status')
            if len(status) == 3:
                filtstatus = ""
            elif len(status) == 2:
                if status[0] == 'public':
                    if status[1] == 'privectrt' :
                        filtstatus = "FILTER (strstarts (?statut, 'public') || strstarts (?statut, 'privé sous contrat'))"
                        filtstring = "Établissements publics ou privés sous contrat"
                    else:
                        filtstatus = "FILTER (strstarts (?statut, 'public') && !strstarts (?statut, 'privé sous contrat'))"
                        filtstring = "Établissements publics ou privés autres que sous contrat"
                else:
                    filtstatus = "FILTER (!strstarts (?statut, 'public'))"
                    filtstring = "Tous établissements privés"
            else:
                if status[0] == 'public':
                    filtstatus = "FILTER (strstarts (?statut, 'public'))"
                    filtstring = "Tous établissements publics"
                elif status[0] == 'privectrt' :
                    filtstatus = "FILTER (strstarts (?statut, 'privé sous contrat'))"
                    filtstring = "Établissements privés sous contrat"
                else:
                    filtstatus = "FILTER (!strstarts (?statut, 'public') && !strstarts (?statut, 'privé sous contrat'))"
                    filtstring = "Établissements privés autres que sous contrat"
        else:
            error = "Vous devez obligatoirement choisir au moins un type d'établissement"
            flash(error)
            return redirect(url_for('explore.search_formindex'))
        if request.form['secteur']:
            sector = sectlist[int(request.form['secteur'])]['secteur']['value']
            sectorid = sectlist[int(request.form['secteur'])]['sectid']['value']
        if request.form['departement'] != "-- Choisir dans cette liste --":
            dept = deptlist[int(request.form['departement'])]['dept']['value']
            dist= ""
            nbchoix = nbchoix + 1
        if request.form['distance']:
            dist = str(int(request.form['distance']) * 1000)
            dept=""
            nbchoix = nbchoix + 1

        if nbchoix == 0 or nbchoix == 2:
            error = "Vous devez obligatoirement choisir un et un seul paramètre géographique"
            flash(error)
            return redirect(url_for('explore.search_formindex'))
        else:
            if dist :
                return redirect(url_for('explore.search_form1', niv=niv, status=filtstatus,
                                        filtstring=filtstring, dist=dist, sector=sector, sectorid=sectorid))
            if dept:
                return redirect(url_for('explore.search_form2', niv=niv, status=filtstatus,
                                        filtstring=filtstring, dept=dept, sector=sector,  sectorid=sectorid))

    return render_template('explore/open/index.html', formsdurlist=formsdurlist, sectlist=sectlist, deptlist=deptlist)

@bp.route('/search_form1', methods=('GET', 'POST'))
@login_required
def search_form1():

    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")
    remote.setReturnFormat(JSON)

    param = [request.args['niv'],  request.args['status'], request.args['sector'], request.args['sectorid'],
             request.args['dist'], request.args['filtstring']]

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
        PREFIX reegle: <http://reegle.info/schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX poder: <http://dev.poderopedia.com/vocab/>

        SELECT  ?typform ?nomForm ?dist  ?duree ?statut ?cost ?pageweb ?siteweb ?formtype ?scolmod ?enseign
        (GROUP_CONCAT(DISTINCT ?acad; separator=', ') as ?acads)  
        (GROUP_CONCAT(DISTINCT ?heberg; separator=', ') as ?hebergs) 
        (GROUP_CONCAT(DISTINCT ?ville ; separator=', ') as ?villes)
        (GROUP_CONCAT(DISTINCT ?dept; separator=', ') as ?depts) 
        (GROUP_CONCAT(DISTINCT ?etab; separator=', ') as ?etabs) 
        (GROUP_CONCAT(DISTINCT ?nomMetier; separator=', ') as ?jobs) WHERE {
            ?job reegle:sector <trmpo:""" + param[3] + """> ;
                 rdfs:label ?nomMetier ;
                 dcterms:identifier ?idMetier ;
                 schema:qualifications ?form ;
                 rdfs:educationLevel ?inlevel .
            ?form dcterms:identifier ?formid .
            ?inlevel rdfs:label '""" + param[0] + """' .
            ?typform a schema:EducationalOccupationalProgram ;
               schema:relatedLink ?link ;
               rdfs:label ?nomForm ;
               poder:AcademicOrganization ?acad ;
               schema:Accommodation ?heberg ;
               schema:City ?ville ;
               wd:Q6465 ?dept ;
               schema:provider ?etab ;
               schema:timeToComplete ?duree ;
               schema:eventAttendanceMode ?scolmod ;
               schema:teaches ?enseign ;
               schema:WebPage ?pageweb ;
               schema:WebSite ?siteweb ;
               schema:funder ?statut ;
               schema:accessibilitySummary ?access ;
               schema:address ?adress ;
               schema:telephone ?tel ;
               schema:estimatedCost ?cost ;
               schema:occupationalCredentialAwarded ?certif ;
               schema:programType ?formtype ;               
               geo:hasGeometry ?geom .
               ?geom  geo:asWKT ?pWKT .
               """ + param[1] + """
            BIND (geof:distance("<http://www.opengis.net/def/crs/EPSG//1.3/CRS84> POINT(""" + lon + " " + lat + """)", ?pWKT, uom:metre) as ?dist) .
            FILTER ( ?dist < 100000)
                ?link dcterms:identifier ?formid .
        }
        GROUP By ?typform ?nomForm  ?dist ?duree ?statut ?cost ?pageweb ?siteweb ?formtype ?scolmod ?enseign        
        ORDER BY ?depts ?villes
        """

    remote.setQuery(descform)
    formdesc = remote.queryAndConvert()['results']['bindings']


    return render_template('explore/open/formdesc1.html', param=param, formdesc=formdesc)

@bp.route('/search_form2', methods=('GET', 'POST'))
@login_required
def search_form2():

    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")
    remote.setReturnFormat(JSON)

    param = [request.args['niv'],  request.args['status'], request.args['sector'], request.args['sectorid'],
             request.args['dept'], request.args['filtstring']]

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
        PREFIX reegle: <http://reegle.info/schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX poder: <http://dev.poderopedia.com/vocab/>
        SELECT  ?typform ?nomForm ?dist  ?duree ?statut ?cost ?pageweb ?siteweb ?formtype ?scolmod ?enseign
        (GROUP_CONCAT(DISTINCT ?acad; separator=', ') as ?acads)  
        (GROUP_CONCAT(DISTINCT ?heberg; separator=', ') as ?hebergs) 
        (GROUP_CONCAT(DISTINCT ?ville ; separator=', ') as ?villes)
        (GROUP_CONCAT(DISTINCT ?dept; separator=', ') as ?depts) 
        (GROUP_CONCAT(DISTINCT ?etab; separator=', ') as ?etabs) 
        (GROUP_CONCAT(DISTINCT ?nomMetier; separator=', ') as ?jobs) WHERE {
            ?job reegle:sector <trmpo:""" + param[3] + """> ;
                 rdfs:label ?nomMetier ;
                 dcterms:identifier ?idMetier ;
                 schema:qualifications ?form ;
                 rdfs:educationLevel ?inlevel .
            ?form dcterms:identifier ?formid .
            ?inlevel rdfs:label '""" + param[0] + """' .
            ?typform a schema:EducationalOccupationalProgram ;
               schema:relatedLink ?link ;
               rdfs:label ?nomForm ;
               poder:AcademicOrganization ?acad ;
               schema:Accommodation ?heberg ;
               schema:City ?ville ;
               wd:Q6465 '""" + param[4] + """';
               schema:provider ?etab ;
               schema:timeToComplete ?duree ;
               schema:eventAttendanceMode ?scolmod ;
               schema:teaches ?enseign ;
               schema:WebPage ?pageweb ;
               schema:WebSite ?siteweb ;
               schema:funder ?statut ;
               schema:accessibilitySummary ?access ;
               schema:address ?adress ;
               schema:telephone ?tel ;
               schema:estimatedCost ?cost ;
               schema:occupationalCredentialAwarded ?certif ;
               schema:programType ?formtype ;               
               geo:hasGeometry ?geom .
               ?geom  geo:asWKT ?pWKT .
               """ + param[1] + """
            BIND (geof:distance("<http://www.opengis.net/def/crs/EPSG//1.3/CRS84> POINT(""" + lon + " " + lat + """)", ?pWKT, uom:metre) as ?dist) .
                ?link dcterms:identifier ?formid .
        }
        GROUP By ?typform ?nomForm  ?dist ?duree ?statut ?cost ?pageweb ?siteweb ?formtype ?scolmod ?enseign        
        ORDER BY ?depts ?villes
    """

    remote.setQuery(descform)
    formdesc = remote.queryAndConvert()['results']['bindings']

    return render_template('explore/open/formdesc2.html', param=param, formdesc=formdesc)
