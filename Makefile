book :
	jupyter-book build .
	ghp-import -n -p -f _build/html
