#! /bin/bash
export SECRET_KEY="dev"
export DATABASE_URI="sqlite:///orientation.db"
# Pour une base postgresql
#export DATABASE_URI="postgresql://username:password@host:port/database_name"

export FLASK_APP=orientation
export FLASK_DEBUG=1
