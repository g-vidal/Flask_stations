from flask import render_template, session, request
from orientation.auth.routes import login_required
from orientation.omvideos import bp
import os
from urllib.parse import urlparse


import requests, json
import SPARQLWrapper
from SPARQLWrapper import SPARQLWrapper, JSON, POST


@bp.route('/omvideos', methods=('GET', 'POST'))
@login_required
def explvideos():
    # Declare external wikidata sparql endpoint using SPARQLWrapper
    # same job can be donne with practicalSPARQL
    # remote = SPARQLWrapper("http://query.wikidata.org/sparql")

    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    titlelist = []
    subjectslist = []

    if "allcreators" in request.form:
        etabs = session['etabs']

        return render_template('explore/omvideos/index.html', etabs=etabs)

    if "alltitles" in request.form:
        titlelist = []

        listtitlesquery = """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT ?title ?id WHERE {
            ?subj dcterms:title ?title ;
                  dcterms:identifier ?id .
        }
        ORDER BY REPLACE(LCASE(str(?title)),"é","e")
        """
        remote.setQuery(listtitlesquery)
        remote.setReturnFormat(JSON)
        titlelist = remote.queryAndConvert()['results']['bindings']
        session['titlelist'] = ""

        return render_template('explore/omvideos/index.html', titlelist=titlelist)

    if "contain" in request.form:
        titlelist = []

        searchstr = request.form['filter']
        listcontquery = '''
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT ?title ?id WHERE {
            ?subj dcterms:title ?title ;
                  dcterms:identifier ?id .
            FILTER (contains (?title, "''' + searchstr + '''"))
        }
       '''

        remote.setQuery(listcontquery)
        remote.setReturnFormat(JSON)
        titlelist = remote.queryAndConvert()['results']['bindings']

        session['titlelist'] = titlelist

        return render_template('explore/omvideos/index.html', titlelist=titlelist)

    if "allsubjects" in request.form:
        subjectslist = []

        listsubjectsquery = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT DISTINCT ?subject ?label WHERE {
            ?sub dcterms:subject ?subject .
            ?subject rdfs:label ?label.
        }
        """

        remote.setQuery(listsubjectsquery)
        remote.setReturnFormat(JSON)
        subjectslist = remote.queryAndConvert()['results']['bindings']

        session['subjectslist'] = ""

        return render_template('explore/omvideos/index.html', subjectslist=subjectslist)

    if "containtopic" in request.form:
        subjectslist = []
        searchstr = request.form['filtertopic']

        listsubjectsquery = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT DISTINCT ?subject ?label WHERE {
            ?sub dcterms:subject ?subject .
            ?subject rdfs:label ?label.
                FILTER (contains (?label, '""" + searchstr + """'))
            }
           """

        remote.setQuery(listsubjectsquery)
        remote.setReturnFormat(JSON)
        subjectslist = remote.queryAndConvert()['results']['bindings']

        session['subjectslist'] = subjectslist

        return render_template('explore/omvideos/index.html', subjectslist=subjectslist)

    return render_template('explore/omvideos/index.html')


@bp.route('/descvideo', methods=('GET', 'POST'))
@login_required
def moddescvideos():

    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    if 'titlelist' in session:
        titlelist = session['titlelist']
    else:
        titlelist = ""

    if 'subjectslist' in session:
        subjectslist = session['subjectslist']
    else:
        subjectslist = ""

    videodesc = []

    if "allcreators" in request.form:
        etabs = session['etabs']

        return render_template('explore/omvideos/index.html', etabs=etabs)

    if "alltitles" in request.form:
        listtitlesquery = """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT ?title ?id WHERE {
            ?subj dcterms:title ?title ;
                  dcterms:identifier ?id .
        }
        ORDER BY REPLACE(LCASE(str(?title)),"é","e")
        """
        remote.setQuery(listtitlesquery)
        remote.setReturnFormat(JSON)
        titlelist = remote.queryAndConvert()['results']['bindings']
        # la liste ne contient pas dans le tampon on le vide passer à redis pour lever cette limitation
        session['titlelist'] = ""

        return render_template('explore/omvideos/index.html', titlelist=titlelist)

    if "contain" in request.form:
        searchstr = request.form['filter']
        listcontquery = '''
        PREFIX dcterms: <http://purl.org/dc/terms/>
       SELECT ?title ?id WHERE {
            ?subj dcterms:title ?title ;
                  dcterms:identifier ?id .
            FILTER (contains (?title, "''' + searchstr + '''"))
        }
       '''

        remote.setQuery(listcontquery)
        remote.setReturnFormat(JSON)
        titlelist = remote.queryAndConvert()['results']['bindings']
        session['titlelist'] = titlelist

        return render_template('explore/omvideos/index.html', titlelist=titlelist)

    if "allsubjects" in request.form:
        subjectslist = []

        listsubjectsquery = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT DISTINCT ?subject ?label WHERE {
            ?sub dcterms:subject ?subject .
            ?subject rdfs:label ?label.
        }
        """

        remote.setQuery(listsubjectsquery)
        remote.setReturnFormat(JSON)
        subjectslist = remote.queryAndConvert()['results']['bindings']
        session['subjectslist'] = ""

        return render_template('explore/omvideos/index.html', subjectslist=subjectslist)

    if "containtopic" in request.form:
        subjectslist = []
        searchstr = request.form['filtertopic']

        listsubjectsquery = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT DISTINCT ?subject ?label WHERE {
            ?sub dcterms:subject ?subject .
            ?subject rdfs:label ?label.
                FILTER (contains (?label, '""" + searchstr + """'))
            }
           """

        remote.setQuery(listsubjectsquery)
        remote.setReturnFormat(JSON)
        subjectslist = remote.queryAndConvert()['results']['bindings']

        session['subjectslist'] = subjectslist

        return render_template('explore/omvideos/index.html', subjectslist=subjectslist)

    if 'thistitle' in request.args:
        title = request.args['thistitle']
        identifier = request.args['thisid']

        desconevideo = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
    
        SELECT DISTINCT ?vid ?title ?creator ?labell ?date ?type ?dur (group_concat(?labels;separator=", ") as ?subjs)?desc WHERE {
            ?vid dcterms:identifier <""" + identifier + """> ;
                 dcterms:title ?title ;
                 dcterms:creator ?creator;
                 dcterms:date ?date ;
                 dcterms:type ?type ;
                 dcterms:duration ?dur ;
                 dcterms:description ?desc ;
                 dcterms:language ?lang .
            OPTIONAL {?vid dcterms:subject ?subj .{
                ?subj rdfs:label ?labels . }}
            ?lang rdfs:label ?labell .
        }
        GROUP BY ?vid ?title ?creator ?labell ?date ?type ?dur ?desc
        """

        remote.setQuery(desconevideo)
        remote.setReturnFormat(JSON)
        videodesc = remote.queryAndConvert()['results']['bindings']

        qvalue = os.path.basename(urlparse(videodesc[0]['creator']['value']).path)
        uri = ('https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&ids=' +
               qvalue + '&languages=fr&format=json')
        creator = json.loads(requests.get(uri).text)['entities'][qvalue]['labels']['fr']['value']

        return render_template('explore/omvideos/fullview.html', title=title,
                               creator=creator,
                               videodesc=videodesc,
                               titlelist=titlelist)

    elif 'thiscreatid' in request.args:

        identifier = request.args['thiscreatid']
        creator = request.args['thiscreator']
        etabs = session['etabs']

        descmanyvideos = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dcterms: <http://purl.org/dc/terms/>

        SELECT DISTINCT ?vid ?title ?labell ?date ?type ?dur (group_concat(?labels;separator=", ") as ?subjs) ?desc WHERE {
            ?vid dcterms:identifier ?id;
                 dcterms:title ?title ;
                 dcterms:creator <""" + identifier + """> ;
                 dcterms:date ?date ;
                 dcterms:type ?type ;
                 dcterms:duration ?dur ;
                 dcterms:description ?desc ;
                 dcterms:language ?lang .
            OPTIONAL {?vid dcterms:subject ?subj .{
                ?subj rdfs:label ?labels .}}
            ?lang rdfs:label ?labell .
        }
        GROUP BY ?vid ?title ?creator ?labell ?date ?type ?dur ?desc
        """

        remote.setQuery(descmanyvideos)
        remote.setReturnFormat(JSON)
        videodesc = remote.queryAndConvert()['results']['bindings']

        return render_template('explore/omvideos/fullview.html', videodesc=videodesc,
                               creator=creator,
                               etabs=etabs)

    elif 'thissubjid' in request.args:

        identifier = request.args['thissubjid']
        subject = request.args['thissubject']

        descmanyvideos = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dcterms: <http://purl.org/dc/terms/>

        SELECT DISTINCT ?vid ?id ?title ?creator ?date ?type ?dur ?desc ?subjs ?labell WHERE {
            ?vid dcterms:identifier ?id;
            dcterms:title ?title ;
            dcterms:creator ?creator ;
            dcterms:date ?date ;
            dcterms:type ?type ;
            dcterms:duration ?dur ;
            dcterms:description ?desc ;
            dcterms:language ?lang ;
            dcterms:subject <""" + identifier + """> .
            {
                SELECT ?vid (group_concat(?labels;separator=", ") as ?subjs) WHERE {
                    ?vid  dcterms:subject ?subj .
                    ?subj rdfs:label ?labels .
                }GROUP BY ?vid
            }
            ?lang rdfs:label ?labell .
        }
        """

        remote.setQuery(descmanyvideos)
        remote.setReturnFormat(JSON)
        videodesc = remote.queryAndConvert()['results']['bindings']

        for i in range(len(videodesc)):
            qvalue = os.path.basename(urlparse(videodesc[i]['creator']['value']).path)
            uri = ('https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&ids=' +
                   qvalue + '&languages=fr&format=json')
            videodesc[i]['creator'] = json.loads(requests.get(uri).text)['entities'][qvalue]['labels']['fr']['value']

        return render_template('explore/omvideos/fullview.html', videodesc=videodesc,
                               subjectslist=subjectslist)
