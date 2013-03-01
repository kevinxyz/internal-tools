BOGUS_TRIGGER=1
LOCAL_ROOT=.
include $(LOCAL_ROOT)/Makefile.common

local_all:

local_install:
	mkdir -p data/google data/rubicon data/appnexus data/floor_reports
	make -C dssodjango/ local_install

local_uninstall:
	make -C dssodjango/ local_uninstall

# Note that the nginx argument requires an absolute path.
_start_servers:
	sudo nginx -c $(CONFIG_PATH)/nginx.conf
	cd $(ROOT)/ && \
	  sudo PROJECT_ENV=$(PROJECT_ENV) PYTHONPATH=$(PYTHON_PATH) \
	     uwsgi --ini $(CONFIG_PATH)/uwsgi.ini
	sleep 1 && make check.servers

_stop.servers:
ifneq ($(wildcard $(PID_PATH)/uwsgi.pid),)
	sudo uwsgi --stop $(PID_PATH)/uwsgi.pid
endif
ifneq ($(wildcard $(PID_PATH)/nginx.pid),)
	sudo kill `cat $(PID_PATH)/nginx.pid`
endif
	sleep 1 && make check.servers

check.servers:
	- ps auxfwww | egrep -i 'uwsgi|nginx' | grep -v grep

start.servers:
	CONFIG_PATH=$(ROOT)/configs/dev make _start_servers

stop.servers:
	PID_PATH=/tmp make _stop.servers


######################################################################
#  Test targets                                                      #
######################################################################
test: production_guard
	@if [[ -n "$(TEST_ALL)" && "$(TEST_ALL)" != "0" ]]; then \
	  echo "Running 'make alltests'"; \
	  $(MAKE) alltests; \
	else \
	  echo "Running 'make smoketests'"; \
	  $(MAKE) smoketests; \
	fi

PYTHON_PROJECT_PATHS=\
translation \
dcommon

# Nosetests need explicit paths or else it will traverse through all the
# Python codes (including auto).
# TODO(kevinx): uncomment when component specific tests are written
#test_paths=$(addsuffix /tests,$(addprefix ./,$(PYTHON_PROJECT_PATHS)))
test_paths=.
nosetest_cover_packages=$(addprefix --cover-package=,$(PYTHON_PROJECT_PATHS))
smoketests: production_guard all
	@echo "Starting smoke tests (fast)"
	TEST_ALL=0 $(TEST_SETTINGS) PYTHONPATH=$(PYTHON_PATH) \
time $(NOSETESTS_CMD_SMOKE) $(nosetest_cover_packages) $(test_paths)
	@echo "PASSED all smoke (light) tests. For a more comprehensive test, run: make alltests"

alltests: production_guard all
	@echo "Starting all tests (slow)"
	TEST_ALL=1 $(TEST_SETTINGS) PYTHONPATH=$(PYTHON_PATH) \
time $(NOSETESTS_CMD) $(nosetest_cover_packages) $(test_paths)
	$(CHECK_PEP8_CMD)

# Jenkins is run on an external (non-VM) machine. Therefore, skip the guard
jenkins_test: all
	TEST_ALL=1 $(TEST_SETTINGS) \
    PYTHONPATH=$(PYTHON_PATH) \
    time $(JENKINS_NOSETESTS_CMD) $(nosetest_cover_packages) $(test_paths)
	$(CHECK_PEP8_CMD)
	$(CHECK_MISC_CMD)


basename=$(shell basename $(PWD))
timestamp=$(shell echo `date +"%F_%H%M"`)
backup:
	echo "Creating a backup..." && \
	cd .. && rm -f $(basename).tar* && tar cvfj "$(basename).$(timestamp).tar.bz2" \
  --exclude=".git*" --exclude=".svn" \
  --exclude="*.jar" --exclude="*.class" --exclude="*.pyc" \
  --exclude="auto" --exclude="data" $(basename)/

local_clean:
	rm -rf auto/nose*

# Remove downloaded 3rd party dependencies
local_clobber: local_clean
	rm -rf auto/nose*
	rm -rf $(AUTO_PATHS)
