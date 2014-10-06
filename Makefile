default: test

testdb:
	pg_ctl init -D /tmp/pgsql -w
	pg_ctl start -D /tmp/pgsql -w
	createdb backslash

testserver:
	.env/bin/python manage.py testserver

clean:
	rm -rf .env
	find . -name "*.pyc" -delete

test:
	python manage.py unittest
