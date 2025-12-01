from fastapi import FastAPI, HTTPException
from opensky_api import OpenSkyApi
import time
from typing import Optional
# from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OpenSky Aviation API", version="1.0.0")

# Inicializar API de OpenSky
api = OpenSkyApi()

# Configurar CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get("/")
def read_root():
    """Endpoint raíz de la API"""
    return {
        "message": "OpenSky Aviation API",
        "version": "1.0.0",
        "endpoints": [
            "/opensky/states - Obtener todos los estados de aeronaves",
            "/opensky/track/{aircraft_id} - Obtener trayectoria de una aeronave",
            "/opensky/state/{aircraft_id} - Obtener estado de una aeronave específica",
            "/opensky/flights - Obtener vuelos en un intervalo de tiempo",
            "/opensky/flights/{aircraft_id} - Obtener vuelos de una aeronave",
            "/opensky/arrivals/{airport} - Obtener llegadas a un aeropuerto",
            "/opensky/departures/{airport} - Obtener salidas de un aeropuerto"
        ]
    }


@app.get("/opensky/states")
def get_all_states():
    """Obtener todos los estados de aeronaves actuales"""
    try:
        states = api.get_states()
        if states is None:
            raise HTTPException(status_code=404, detail="No se pudieron obtener los estados")
        
        return {
            "success": True,
            "data": states,
            "timestamp": int(time.time())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estados: {str(e)}")


@app.get("/opensky/track/{aircraft_id}")
def get_aircraft_track(aircraft_id: str, timestamp: Optional[int] = None):
    """Obtener la trayectoria de una aeronave específica"""
    try:
        aircraft_id = aircraft_id.lower()
        current_time = timestamp if timestamp else int(time.time())
        track = api.get_track_by_aircraft(aircraft_id, t=current_time)
        
        if track is None:
            raise HTTPException(status_code=404, detail=f"No se pudo obtener la trayectoria para la aeronave {aircraft_id}")
        
        return {
            "success": True,
            "aircraft_id": aircraft_id,
            "data": track,
            "timestamp": current_time
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Error de validación: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener trayectoria: {str(e)}")


@app.get("/opensky/state/{aircraft_id}")
def get_aircraft_state(aircraft_id: str):
    """Obtener el estado actual de una aeronave específica"""
    try:
        aircraft_id = aircraft_id.lower()
        state = api.get_states(time_secs=0, icao24=aircraft_id, bbox=())
        
        if state is None:
            raise HTTPException(status_code=404, detail=f"No se pudieron obtener datos para la aeronave {aircraft_id}")
        
        return {
            "success": True,
            "aircraft_id": aircraft_id,
            "data": state,
            "timestamp": int(time.time())
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Error de validación: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estado: {str(e)}")


@app.get("/opensky/flights/{aircraft_id}")
def get_aircraft_flights(
    aircraft_id: str, 
    begin_timestamp: Optional[int] = None,
    end_timestamp: Optional[int] = None
):
    """Obtener los vuelos de una aeronave específica"""
    try:
        aircraft_id = aircraft_id.lower()
        current_time = int(time.time())

        # Cambiando a un rango de tiempo más próximo si no se proporcionan timestamps
        begin = begin_timestamp if begin_timestamp else current_time - (7 * 24 * 60 * 60)  # 7 dias antes
        end = end_timestamp if end_timestamp else current_time 

        print(f"Requesting flights for aircraft_id: {aircraft_id}, from {begin} to {end}")
        
        flights = api.get_flights_by_aircraft(aircraft_id, begin, end)
        
        print(f"Flights data fetched: {flights}")

        # Comprobación en la respuesta
        if flights is None or len(flights) == 0:
            raise HTTPException(status_code=404, detail=f"No se pudieron obtener vuelos para la aeronave {aircraft_id} en el rango de tiempo especificado.")
        
        # Mostrar los datos de los vuelos encontrados
        flights_data = [{"callsign": flight.callsign, "estDepartureAirport": flight.estDepartureAirport, "firstSeen": flight.firstSeen, "lastSeen": flight.lastSeen} for flight in flights]
        return {
            "success": True,
            "aircraft_id": aircraft_id,
            "data": flights_data,
            "begin_timestamp": begin,
            "end_timestamp": end
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Error de validación: {str(ve)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener vuelos: {str(e)}")

@app.get("/opensky/flights/")
def get_flights(
    begin_timestamp: Optional[int] = None,
    end_timestamp: Optional[int] = None
):
    """Obtener vuelos durante un intervalo de tiempo específico"""
    try:
        current_time = int(time.time())

        # Calcular los timestamps por defecto
        begin = begin_timestamp if begin_timestamp else current_time - (7200)  # 2 horas atrás
        end = end_timestamp if end_timestamp else current_time  # Hasta ahora

        print(f"Requesting flights from {begin} to {end}")
        
        flights = api.get_flights_from_interval(begin, end)

        # Comprobación en la respuesta
        if not flights:  # Verifica si la lista está vacía o es None
            raise HTTPException(status_code=404, detail="No se pudieron obtener vuelos en el rango de tiempo especificado.")

        # Preparar los datos de vuelos encontrados
        flights_data = [{
            "icao24": flight.icao24,
            "firstSeen": flight.firstSeen,
            "estDepartureAirport": flight.estDepartureAirport,
            "lastSeen": flight.lastSeen,
            "estArrivalAirport": flight.estArrivalAirport,
            "callsign": flight.callsign,
            "estDepartureAirportHorizDistance": flight.estDepartureAirportHorizDistance,
            "estDepartureAirportVertDistance": flight.estDepartureAirportVertDistance,
            "estArrivalAirportHorizDistance": flight.estArrivalAirportHorizDistance,
            "estArrivalAirportVertDistance": flight.estArrivalAirportVertDistance,
            "departureAirportCandidatesCount": flight.departureAirportCandidatesCount,
            "arrivalAirportCandidatesCount": flight.arrivalAirportCandidatesCount,
        } for flight in flights]

        return {
            "success": True,
            "data": flights_data,
            "begin_timestamp": begin,
            "end_timestamp": end
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Error de validación: {str(ve)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener vuelos: {str(e)}")


@app.get("/opensky/arrivals/{airport}")
def get_arrivals(airport: str, begin_timestamp: Optional[int] = None, end_timestamp: Optional[int] = None):
    """Obtener llegadas a un aeropuerto dentro de un intervalo de tiempo específico"""
    try:
        current_time = int(time.time())
        begin = begin_timestamp if begin_timestamp else current_time - 3600  # 1 hora antes por defecto
        end = end_timestamp if end_timestamp else current_time
        
        arrivals = api.get_arrivals_by_airport(airport, begin, end)
        
        if arrivals is None:
            raise HTTPException(status_code=404, detail=f"No se pudieron obtener llegadas para el aeropuerto {airport}")
        
        return {
            "success": True,
            "airport": airport,
            "data": arrivals,
            "begin_timestamp": begin,
            "end_timestamp": end
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Error de validación: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener llegadas: {str(e)}")


@app.get("/opensky/departures/{airport}")
def get_departures(airport: str, begin_timestamp: Optional[int] = None, end_timestamp: Optional[int] = None):
    """Obtener salidas desde un aeropuerto dentro de un intervalo de tiempo específico"""
    try:
        current_time = int(time.time())
        begin = begin_timestamp if begin_timestamp else current_time - 3600  # 1 hora antes por defecto
        end = end_timestamp if end_timestamp else current_time
        
        departures = api.get_departures_by_airport(airport, begin, end)
        
        if departures is None:
            raise HTTPException(status_code=404, detail=f"No se pudieron obtener salidas para el aeropuerto {airport}")
        
        return {
            "success": True,
            "airport": airport,
            "data": departures,
            "begin_timestamp": begin,
            "end_timestamp": end
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Error de validación: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener salidas: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)