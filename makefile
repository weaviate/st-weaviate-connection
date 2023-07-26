format:
	black ./st_weaviate_connection && \
	 isort ./st_weaviate_connection
	
	black ./tests && \
	 isort ./tests

test:
	pytest --cov=st_weaviate_connection --cov-report term-missing