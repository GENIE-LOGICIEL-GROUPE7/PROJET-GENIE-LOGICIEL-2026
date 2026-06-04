import urllib.request, os
BASE = os.path.dirname(os.path.abspath(__file__))
CSS  = os.path.join(BASE,"restaurant","static","css")
JS   = os.path.join(BASE,"restaurant","static","js")
os.makedirs(CSS,exist_ok=True); os.makedirs(JS,exist_ok=True)
os.makedirs(os.path.join(CSS,"fonts"),exist_ok=True)
files=[
  ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",os.path.join(CSS,"bootstrap.min.css")),
  ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js",os.path.join(JS,"bootstrap.bundle.min.js")),
  ("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css",os.path.join(CSS,"bootstrap-icons.css")),
  ("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff2",os.path.join(CSS,"fonts","bootstrap-icons.woff2")),
  ("https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js",os.path.join(JS,"chart.umd.min.js")),
]
print("Telechargement Bootstrap en local...")
for url,dest in files:
  name=os.path.basename(dest)
  try:
    print(f"  {name}...",end=" ",flush=True)
    urllib.request.urlretrieve(url,dest)
    print(f"OK ({os.path.getsize(dest)//1024}KB)")
  except Exception as e:
    print(f"ERREUR: {e}")
print("TERMINE ! Rechargez la page dans le navigateur.")
