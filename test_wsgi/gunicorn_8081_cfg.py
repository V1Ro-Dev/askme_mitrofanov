import multiprocessing

bind = "127.0.0.1:8081"
workers = 2
wsgi_app = "test_wsgi.test_wsgi:simple_app"