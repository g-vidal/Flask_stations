#! /bin/bash
export SECRET_KEY="dev"
export DATABASE_URI="sqlite:///stations.db"
# Pour une base postgresql
#export DATABASE_URI="postgresql://username:password@host:port/database_name"

export FLASK_APP=stations
export FLASK_DEBUG=1
