from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from .models import Trip, Attraction
import json
import requests
from datetime import datetime
from reportlab.pdfgen import canvas
from io import BytesIO
import os

# Pobieranie pogody z OpenWeather API
def get_weather(city):
    API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "weather": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }
    return {"error": "Nie udało się pobrać danych pogodowych"}

# Pobieranie gotowych planów wycieczek
@csrf_exempt
def ready_plans(request):
    if request.method == 'GET':
        plans = list(Trip.objects.values())
        return JsonResponse(plans, safe=False)

# Generowanie PDF dla planu wycieczki
def generate_trip_pdf(trip, attractions):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.drawString(100, 800, f"Plan wycieczki: {trip.title}")
    pdf.drawString(100, 780, f"Czas trwania: {trip.duration_days} dni")
    pdf.drawString(100, 760, "Atrakcje:")

    y_position = 740
    for attr in attractions:
        pdf.drawString(120, y_position, f"- {attr.name} ({attr.location})")
        y_position -= 20

    pdf.save()
    buffer.seek(0)
    return buffer

# Wysyłanie gotowego planu na e-mail
@csrf_exempt
def send_ready_plan(request, plan_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        email_address = data.get("email")

        if not email_address:
            return JsonResponse({"error": "Brak adresu e-mail"}, status=400)

        try:
            trip = Trip.objects.get(id=plan_id)
            attractions = trip.attractions.all()

            pdf_buffer = generate_trip_pdf(trip, attractions)

            email = EmailMessage(
                subject=f"Plan wycieczki: {trip.title}",
                body="Załączamy Twój plan wycieczki.",
                from_email="noreply@wycieczkomat.pl",
                to=[email_address]
            )
            email.attach('plan.pdf', pdf_buffer.getvalue(), 'application/pdf')
            email.send()

            return JsonResponse({"message": f"Plan wysłany na {email_address}"})
        except Trip.DoesNotExist:
            return JsonResponse({"error": "Plan nie istnieje"}, status=404)

# Generowanie indywidualnego planu wycieczki
@csrf_exempt
def individual_plan(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        city = data.get("city")
        email_address = data.get("email")
        start_date = data.get("startDate")
        end_date = data.get("endDate")
        preferences = data.get("preferences", "Brak preferencji")

        if not city or not email_address or not start_date or not end_date:
            return JsonResponse({"error": "Brak wymaganych danych"}, status=400)

        weather = get_weather(city)

        pdf_buffer = generate_individual_pdf(data, weather)

        email = EmailMessage(
            subject=f"Twój indywidualny plan wycieczki do {city}",
            body=f"Plan dla {city} ({start_date} - {end_date})",
            from_email="noreply@wycieczkomat.pl",
            to=[email_address]
        )
        email.attach('plan.pdf', pdf_buffer.getvalue(), 'application/pdf')
        email.send()

        return JsonResponse({
            "message": f"Plan wysłany na {email_address}",
            "planSummary": f"Wycieczka do {city} ({preferences})",
            "weather": weather,
            "days": generate_daily_plan(data, weather)
        })

# Generowanie PDF dla indywidualnego planu
def generate_individual_pdf(data, weather):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.drawString(100, 800, f"Indywidualny plan dla {data['city']}")
    pdf.drawString(100, 780, f"Data: {data['startDate']} - {data['endDate']}")
    pdf.drawString(100, 760, f"Preferencje: {data['preferences']}")

    pdf.drawString(100, 740, "Pogoda w dniu przyjazdu:")
    pdf.drawString(120, 720, f"- Temperatura: {weather.get('temperature', 'Brak danych')}°C")
    pdf.drawString(120, 700, f"- Warunki: {weather.get('weather', 'Brak danych')}")
    pdf.drawString(120, 680, f"- Wiatr: {weather.get('wind_speed', 'Brak danych')} m/s")

    pdf.save()
    buffer.seek(0)
    return buffer

# Generowanie przykładowego planu dziennego
def generate_daily_plan(data, weather):
    return [
        f"Dzień {i+1}: Zwiedzanie atrakcji w {data['city']}"
        for i in range(int(data.get("duration_days", 3)))
    ]
