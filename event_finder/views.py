import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
import pytz


class NearbyEventsView(APIView):
    def get(self, request):
        lat = request.query_params.get("lat")
        lon = request.query_params.get("lon")
        start = request.GET.get("start")
        end = request.GET.get("end")

        if not lat or not lon:
            return Response({"error": "Missing lat/lon"}, status=400)

        def to_utc_z_format(date_str):
            try:
                dt = datetime.fromisoformat(date_str)
                return dt.astimezone(pytz.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
            except Exception:
                return None

        start_utc = to_utc_z_format(start)
        end_utc = to_utc_z_format(end)

        if not start_utc or not end_utc:
            return Response({"error": "Invalid start/end format"}, status=400)

        url = f"https://app.ticketmaster.com/discovery/v2/events.json"
        params = {
            "apikey": "Gmo8nEHt14mosxzDXnenMBpxKdF5fAB4",
            "latlong": f"{lat},{lon}",
            "radius": "100",
            "unit": "km",
            "classificationName": "music",
            "startDateTime": start_utc,
            "endDateTime": end_utc,
        }

        res = requests.get(url, params=params)
        data = res.json()
        events = data.get('_embedded', {}).get('events', [])
        return Response(events)
