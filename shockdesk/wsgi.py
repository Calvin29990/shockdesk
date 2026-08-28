"""Point d'entrée WSGI pour un hébergement de production.

Le serveur de développement Flask (`shockdesk.cli serve`) ne doit pas être exposé
sur Internet. Un PaaS (Render, Railway, Fly, Heroku…) pointe sur ce module :

    gunicorn shockdesk.wsgi:app --bind 0.0.0.0:$PORT

`app` est au niveau module, c'est ce que cherchent gunicorn et consorts.
"""

from .webapp import create_app

app = create_app()
