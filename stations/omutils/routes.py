from flask import render_template
from stations.omutils import bp
from stations.auth.routes import login_required

import SPARQLWrapper
from SPARQLWrapper import SPARQLWrapper, JSON


@bp.route('/utilmeti', methods=('GET', 'POST'))
@login_required
def metiutil():
    return render_template('omutils/metiers/utilmeti.html')


@bp.route('/utildescmeti', methods=('GET', 'POST'))
@login_required
def descmetiutil():
    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    countjobsquery = """
    PREFIX schema: <http://schema.org/>
    SELECT (COUNT(?s) AS ?metier) WHERE {
        ?s a schema:Occupation .
    }
    """

    jobskeycodequery = """
    PREFIX schema: <http://schema.org/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dcterms: <http://purl.org/dc/terms/> 
    SELECT ?Id ?metier ?code WHERE {
        ?Id a schema:Occupation ;
        rdfs:label ?metier ;
        dcterms:identifier ?code .
    }
    ORDER BY REPLACE(LCASE(str(?metier)),"é","e")
    """

    remote.setQuery(countjobsquery)
    remote.setReturnFormat(JSON)
    countjobs = remote.queryAndConvert()['results']['bindings'][0]['metier']['value']

    remote.setQuery(jobskeycodequery)
    remote.setReturnFormat(JSON)
    jobskeycode = remote.queryAndConvert()['results']['bindings']

    return render_template('omutils/metiers/utilmeti_desc.html',
                           countjobs=countjobs,
                           jobskeycode=jobskeycode)


@bp.route('/utildurmeti', methods=('GET', 'POST'))
@login_required
def durmetiutil():
    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    countjobsquery = """
    PREFIX schema: <http://schema.org/>
    SELECT (COUNT(?s) AS ?metier) WHERE {
        ?s a schema:Occupation .
    }
    """

    jobsdursalquery = """
    PREFIX schema: <http://schema.org/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dcterms: <http://purl.org/dc/terms/> 
    SELECT DISTINCT ?Id ?metier ?niveauAcces ?sal WHERE {
        ?Id a schema:Occupation ;
              rdfs:label ?metier ;
              schema:estimatedSalary ?sal ;
              rdfs:educationLevel ?niv .
              ?niv rdfs:label ?niveauAcces  .
    }
    ORDER BY REPLACE(LCASE(str(?metier)),"é","e")
    """

    remote.setQuery(countjobsquery)
    remote.setReturnFormat(JSON)
    countjobs = remote.queryAndConvert()['results']['bindings'][0]['metier']['value']

    remote.setQuery(jobsdursalquery)
    remote.setReturnFormat(JSON)
    jobsdursal = remote.queryAndConvert()['results']['bindings']

    return render_template('omutils/metiers/utilmeti_dur.html',
                           countjobs=countjobs,
                           jobsdursal=jobsdursal)


@bp.route('/utilpredmeti', methods=('GET', 'POST'))
@login_required
def predmetiutil():

    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    countpredsquery = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sd: <http://www.w3.org/ns/sparql-service-description#>
    SELECT (COUNT(?clefDeFiltrage) AS ?nbclefs) WHERE {
        ?s sd:Graph "Métiers" ;
        rdfs:label ?clefDeFiltrage .
    }
    """

    predsquery = """
    PREFIX sd: <http://www.w3.org/ns/sparql-service-description#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?informationsDisponibles ?clefDeFiltrage WHERE {
         ?clefDeFiltrage sd:Graph "Métiers" ;
            rdfs:label ?informationsDisponibles .
    }
    ORDER BY REPLACE(LCASE(str(?informationsDisponibles)),"é","e")
    """

    remote.setQuery(countpredsquery)
    remote.setReturnFormat(JSON)
    countpreds = remote.queryAndConvert()['results']['bindings'][0]['nbclefs']['value']

    remote.setQuery(predsquery)
    remote.setReturnFormat(JSON)
    preds = remote.queryAndConvert()['results']['bindings']

    return render_template('omutils/metiers/utilmeti_preds.html',
                           countpreds=countpreds,
                           preds=preds)


@bp.route('/utilform', methods=('GET', 'POST'))
@login_required
def formutil():
    return render_template('omutils/formations/utilform.html')


@bp.route('/utildescform', methods=('GET', 'POST'))
@login_required
def descformutil():
    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    countformsquery = """
    PREFIX schema: <http://schema.org/>
    SELECT (COUNT(DISTINCT ?typeDeFormation) AS ?count) WHERE {
        ?formation schema:programType ?typeDeFormation .
    }
    """

    formskeydurquery = """
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX schema: <http://schema.org/>
    SELECT DISTINCT ?typeDeFormation ?educationalLevel WHERE {
        ?formation schema:programType ?typeDeFormation ;
                   schema:educationalLevel ?educationalLevel.
    }
    ORDER BY ?educationalLevel
    """

    remote.setQuery(countformsquery)
    remote.setReturnFormat(JSON)
    countforms = remote.queryAndConvert()['results']['bindings'][0]['count']['value']

    remote.setQuery(formskeydurquery)
    remote.setReturnFormat(JSON)
    formskeydur = remote.queryAndConvert()['results']['bindings']

    return render_template('omutils/formations/utilform_desc.html',
                           countforms=countforms,
                           formskeydur=formskeydur)


@bp.route('/utilpredform', methods=('GET', 'POST'))
@login_required
def predformutil():
    remote = SPARQLWrapper("http://localhost:7200/repositories/ONISEP")

    countformspredsquery = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sd: <http://www.w3.org/ns/sparql-service-description#>
    SELECT (COUNT(?clefDeFiltrage) AS ?nbclefs) WHERE {
        ?s sd:Graph "Formations" ;
            rdfs:label ?clefDeFiltrage .
    }
    """

    formspredsquery = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sd: <http://www.w3.org/ns/sparql-service-description#>
    SELECT ?informationsDisponibles ?clefDeFiltrage WHERE {
        ?clefDeFiltrage sd:Graph "Formations" ;
            rdfs:label ?informationsDisponibles .
    }
    ORDER BY REPLACE(LCASE(str(?informationsDisponibles)),"é","e")
    """

    remote.setQuery(countformspredsquery)
    remote.setReturnFormat(JSON)
    countformspreds = remote.queryAndConvert()['results']['bindings'][0]['nbclefs']['value']

    remote.setQuery(formspredsquery)
    remote.setReturnFormat(JSON)
    formspreds = remote.queryAndConvert()['results']['bindings']

    return render_template('omutils/formations/utilform_preds.html',
                           countpreds=countformspreds,
                           formspreds=formspreds)


@bp.route('/utilcint', methods=('GET', 'POST'))
@login_required
def cintutil():
    return render_template('omutils/cint/cintutil.html')


@bp.route('/utiletab', methods=('GET', 'POST'))
@login_required
def etabutil():
    return render_template('omutils/etablissements/etabutil.html')
