from flask import render_template, session
from stations.main import bp
import os
from urllib.parse import urlparse

import SPARQLWrapper
from SPARQLWrapper import SPARQLWrapper, JSON


@bp.route('/')
def index():
    remote_w = SPARQLWrapper("http://query.wikidata.org/sparql")
    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    if 'etabs' in session:
        etabs = session['etabs']
    else:
        etabs = []
        listcreatorsquery = """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT DISTINCT ?creator WHERE {
            ?sub dcterms:creator ?creator .
        }
        """

        remote.setQuery(listcreatorsquery)
        remote.setReturnFormat(JSON)
        templist = remote.queryAndConvert()['results']['bindings']

        for result in templist:
            data = result['creator']['value']

            if urlparse(data).netloc == 'www.wikidata.org':
                value = os.path.basename(urlparse(data).path)

                creatquery = """
                    PREFIX wd: <http://www.wikidata.org/entity/>
                    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                    SELECT ?label WHERE {
                        wd:""" + value + """ rdfs:label ?label .
                        FILTER (lang(?label) = 'fr') .
                        }
                """

                remote_w.setQuery(creatquery)
                remote_w.setReturnFormat(JSON)
                label = remote_w.queryAndConvert()
                etabs.append([label['results']['bindings'][0]['label']['value'], data])
        session['etabs'] = etabs
    return render_template('/index.html')


@bp.route('/denied')
def denied():
    return render_template('/denied.html')
