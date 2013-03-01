LOCAL_ROOT=..
include $(LOCAL_ROOT)/Makefile.common

PG_DB=$(shell $(GET_CONFIG_VALUE) storage.PG_DB)
PG_USER=$(shell $(GET_CONFIG_VALUE) storage.PG_USER)
PG_PASSWORD=$(shell $(GET_CONFIG_VALUE) storage.PG_PASSWORD)
PG_USER_CMD=PGPASSWORD=$(PG_PASSWORD) psql -U $(PG_USER) -h localhost
PG_ROOT_CMD=sudo -u postgres psql

DJANGO_PROJECT_NAME=dssodjango
MANAGE=PROJECT_ENV=$(PROJECT_ENV) \
  PYTHONPATH=$(PYTHON_PATH) python manage.py
# Below is also the DB's prefix

local_all: _warning

_warning:
	@echo "WARNING: All targets in this Makefile are potentially destructive."

local_install: _warning production_guard
	@if [[ ! "`echo 'SELECT 123' | $(PG_USER_CMD) 2>&1`" =~ " 123" ]]; then \
      echo "Creating UI user $(PG_USER) and database (no table)..."; \
      echo "\
CREATE ROLE $(PG_USER) \
  PASSWORD '$(PG_PASSWORD)' \
  NOSUPERUSER CREATEDB NOCREATEROLE INHERIT LOGIN; \
CREATE DATABASE $(PG_DB) OWNER = $(PG_USER);" | $(PG_ROOT_CMD); \
    fi
	@echo "Running db.syncdb and db.load_data..."
	make db.syncdb db.load_data

local_uninstall: _warning production_guard
	echo "\
DROP DATABASE IF EXISTS $(PG_DB); \
DROP ROLE IF EXISTS $(PG_USER);" | $(PG_ROOT_CMD);

# Print out DB credentials for debugging purpose. The
# values depend on PROJECT_ENV (prod, dev, ...)
info:
	@echo "DJANGO_PROJECT: $(DJANGO_PROJECT_NAME)"
	@echo "DB database: $(PG_DB)"
	@echo "DB user: $(PG_USER)"
	@echo "DB password: $(PG_PASSWORD)"
	@echo "DB user command: $(PG_USER_CMD)"
	@echo "DB root command (use with care): $(PG_ROOT_CMD)"
	@echo "Django command: $(MANAGE)"
	@echo "get_config_value = $(GET_CONFIG_VALUE)"


#############################
# DB CREATION AND MIGRATION #
#############################

# create tables like dssodjango_*, auth_*, django_*, south_migrationhistory, ...
# (this will also try to automatically load dssodjango/fixtures/initial_data.yaml
#  if it exists)
db.syncdb:
	$(MANAGE) syncdb --noinput --migrate

db.migrate:
	$(MANAGE) migrate $(DJANGO_PROJECT_NAME)

# This populates all the YAML data into the tables:
db.load_data:
	@if [[ "`echo 'SELECT 1 FROM $(DJANGO_PROJECT_NAME)_ssoauthinfo LIMIT 1' | \
	        $(PG_USER_CMD) 2>&1`" =~ "0 rows" ]]; then \
    echo "Loading data from initial fixture file (_initial_data.yaml)"; \
      make db.clobber_data; \
    else \
      echo "The database already has data ('make db.clobber_data' to clobber)."; \
    fi

# This will either append to or clobber over DB rows.
db.clobber_data:
	@echo "TODO(kevinx): add initial_data.yaml"
	$(MANAGE) loaddata fixtures/_initial_data.yaml


####################
# DEVELOPMENT ONLY #
####################

# Do this initially:
# make local_uninstall
# make local_install db.syncdb db.load_data
#
# SELECT SUM(revenue) FROM dssodjango_partnerdata WHERE fk_ad_id=3;
# SELECT fk_ad_id, SUM(revenue) FROM dssodjango_partnerdata GROUP BY fk_ad_id;
# SELECT ad.size_name, SUM(revenue) FROM dssodjango_partnerdata as partnerdata,
#  dssodjango_ad AS ad WHERE ad.pk_ad_id=partnerdata.fk_ad_id GROUP BY ad.pk_ad_id;
#

# convert_to_south should only be run once to initialize from an existing
# schema (created not using South) to South style
db.convert_to_south: db.syncdb
	$(MANAGE) convert_to_south $(DJANGO_PROJECT_NAME) && \
	$(MANAGE) migrate $(DJANGO_PROJECT_NAME) 0001 --fake

# For development purposes, here are the steps to make DB model changes:
# 0) First time only, execute the following to generate a 0001_* file:
#    make db.dev.initialize
# 1) modify models.py
# 2) $ make db.dev.update
#    (this creates migrations/0002_adding_more_shtuff.py)
# 3) if necessary, edit 0002_adding_more_shtuff.py
#
# With newly generated files, on dev and production system, do this:
# 4) $ make db.migrate
#    (if no new migrations, migrate will simply pass)
# 5) $(MANAGE) loaddata fixtures/0002_adding_more_data_in_db.yaml

db.dev.initialize:
	@echo "This should only be run the very first time."
	$(MANAGE) schemamigration $(DJANGO_PROJECT_NAME) --initial

# Run this to update with models.py subsequently, which will generate
# subsequent update files in migrations/000x_changes_in_models.py
db.dev.update:
	$(MANAGE) schemamigration $(DJANGO_PROJECT_NAME) --auto

db.dev.print_ddl:
	$(MANAGE) sqlall $(DJANGO_PROJECT_NAME)

db.dev.dump:
	$(MANAGE) dumpdata dssodjango.ldapuser --format yaml > /tmp/ldapuser.yaml


# Default user/password is admin/x, as defined in _initial_data.yaml
start.test_server:
	DJANGO_STANDALONE_SERVER=True $(MANAGE) runserver 0.0.0.0:7000

start.roulette_server:
	make -C roulette run

#PYTHONPATH=/home/kevinx/code/dsso/dsso/dssojango PROJECT_ENV=dev uwsgi \
#  --http 172.16.238.88:8080 --module dssodjango.wsgi --chdir ~/code/dsso/dsso
#PYTHONPATH=/home/kevinx/code/dsso/dsso/dssojango PROJECT_ENV=dev uwsgi \
#  --ini configs/dev/uwsgi.ini --protocol=http --log-date

# from django.contrib.auth.models import User
# u = User()
# u.set_password('whatever')
# u.password  # returns sha
shell:
	$(MANAGE) shell


#####################
# CLEAN AND CLOBBER #
#####################

local_clean:
	if [[ "`echo 'SELECT 1;\q' | $(PG_USER_CMD) 2>&1`" =~ "1 row" ]]; then \
	  echo "To drop tables, use 'make local_uninstall'"; \
	fi

local_clobber: local_clean local_uninstall

