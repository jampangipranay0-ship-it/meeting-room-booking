import urllib.request
urls=['http://127.0.0.1:5000/','http://127.0.0.1:5000/static/images/multirecruit.png','http://127.0.0.1:5000/static/images/vachihr.png']
for u in urls:
    try:
        with urllib.request.urlopen(u, timeout=5) as r:
            info=r.info()
            data=r.read()
            print(f'URL: {u}\nSTATUS: {getattr(r,"status", "200?")}, LEN: {len(data)}, TYPE: {info.get_content_type()}\n')
    except Exception as e:
        print(f'URL: {u}\nERROR: {e}\n')
