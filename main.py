from fastapi import FastAPI, HTTPException
from opensky_api import OpenSkyApi
import time
from typing import Optional

app = FastAPI(title="OpenSky Aviation API", version="1.0.0")

# Inicializar API de OpenSky
api = OpenSkyApi()


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
            "/opensky/flights/{aircraft_id} - Obtener vuelos de una aeronave"
        ]
    }


@app.get("/opensky/states")
def get_all_states():
    """
    Obtener todos los estados de aeronaves actuales
    Basado en prueba.py
    """
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
    """
    Obtener la trayectoria de una aeronave específica
    Basado en prueba3.py
    
    Args:
        aircraft_id: ID ICAO24 de la aeronave (en minúsculas)
        timestamp: Timestamp opcional (por defecto usa tiempo actual)
    """
    try:
        # Convertir a minúsculas para asegurar formato correcto
        aircraft_id = aircraft_id.lower()
        
        # Usar timestamp proporcionado o tiempo actual
        current_time = timestamp if timestamp else int(time.time())
        
        # Obtener trayectoria
        track = api.get_track_by_aircraft(aircraft_id, t=current_time)
        
        if track is None:
            raise HTTPException(
                status_code=404, 
                detail=f"No se pudo obtener la trayectoria para la aeronave {aircraft_id}"
            )
        
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
    """
    Obtener el estado actual de una aeronave específica
    Basado en prueba4.py
    
    Args:
        aircraft_id: ID ICAO24 de la aeronave
    """
    try:
        # Convertir a minúsculas
        aircraft_id = aircraft_id.lower()
        
        # Obtener estado
        state = api.get_states(time_secs=0, icao24=aircraft_id, bbox=())
        
        if state is None:
            raise HTTPException(
                status_code=404, 
                detail=f"No se pudieron obtener datos para la aeronave {aircraft_id}"
            )
        
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
    """
    Obtener los vuelos de una aeronave específica
    Basado en prueba5.py
    
    Args:
        aircraft_id: ID ICAO24 de la aeronave
        begin_timestamp: Timestamp de inicio (por defecto tiempo actual)
        end_timestamp: Timestamp de fin (por defecto tiempo actual)
    """
    try:
        # Convertir a minúsculas
        aircraft_id = aircraft_id.lower()
        
        # Usar timestamps proporcionados o tiempo actual
        current_time = int(time.time())
        begin = begin_timestamp if begin_timestamp else current_time
        end = end_timestamp if end_timestamp else current_time
        
        # Obtener vuelos
        flights = api.get_flights_by_aircraft(aircraft_id, begin, end)
        
        if flights is None:
            raise HTTPException(
                status_code=404, 
                detail=f"No se pudieron obtener vuelos para la aeronave {aircraft_id}"
            )
        
        return {
            "success": True,
            "aircraft_id": aircraft_id,
            "data": flights,
            "begin_timestamp": begin,
            "end_timestamp": end
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Error de validación: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener vuelos: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
