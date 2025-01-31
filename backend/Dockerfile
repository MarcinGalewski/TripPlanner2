# Użyj oficjalnego obrazu Pythona
FROM python:3.11

# Ustaw katalog roboczy w kontenerze
WORKDIR /backend

# Skopiuj pliki aplikacji do kontenera
COPY . .

# Zainstaluj Pipenv
RUN pip install --no-cache-dir pipenv

# Zainstaluj zależności z Pipenv
RUN pipenv install   

# Otwórz port 8000 dla Django
EXPOSE 8000

# Uruchomienie migracji i serwera Django
CMD ["sh", "-c", "pipenv run python manage.py migrate && pipenv run python manage.py collectstatic --noinput && pipenv run python manage.py runserver 0.0.0.0:8000"]
