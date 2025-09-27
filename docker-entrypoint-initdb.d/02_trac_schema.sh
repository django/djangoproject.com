#!/bin/sh

PGPASSWORD=secret psql --username=code.djangoproject --dbname=code.djangoproject < /trac.sql
