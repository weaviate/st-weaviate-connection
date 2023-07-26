format:
	black ./st_weaviate_connection && \
	 isort ./st_weaviate_connection

test:
	pytest --cov=st_weaviate_connection --cov-report term-missing