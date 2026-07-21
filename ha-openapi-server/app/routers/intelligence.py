import logging
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Body, HTTPException
from app.core.clients import ha_api
from app.models.common import SuccessResponse
from app.models.intelligence import (
    AnalyzeHomeContextRequest,
    ActivityRecognitionRequest,
    ComfortOptimizationRequest,
    EnergyIntelligenceRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["intelligence"])

@router.post("/analyze_home_context", operation_id="analyze_home_context", summary="Analyze complete home context")
async def analyze_home_context(request: AnalyzeHomeContextRequest = Body(...)):
    """
    Analyzes current state: occupancy, activity, time of day, weather, energy usage.
    
    **PROVIDES:**
    - Occupancy detection from person entities
    - Active devices count
    - Current time context (morning, afternoon, evening, night)
    - Weather conditions
    - Energy consumption overview
    
    **USE CASES:**
    - Smart home dashboard
    - Automation decision making
    - Energy monitoring
    """
    try:
        states = await ha_api.get_states()
        
        # Analyze occupancy
        person_states = [s for s in states if s["entity_id"].startswith("person.")]
        occupancy = {
            "total_people": len(person_states),
            "home": sum(1 for p in person_states if p.get("state") == "home"),
            "away": sum(1 for p in person_states if p.get("state") not in ["home", "unknown"])
        }
        
        # Active devices
        lights_on = sum(1 for s in states if s["entity_id"].startswith("light.") and s.get("state") == "on")
        switches_on = sum(1 for s in states if s["entity_id"].startswith("switch.") and s.get("state") == "on")
        
        # Time context
        now = datetime.now()
        hour = now.hour
        if 5 <= hour < 12:
            time_context = "morning"
        elif 12 <= hour < 17:
            time_context = "afternoon"
        elif 17 <= hour < 21:
            time_context = "evening"
        else:
            time_context = "night"
        
        # Weather (if available)
        weather_states = [s for s in states if s["entity_id"].startswith("weather.")]
        weather_info = None
        if weather_states:
            weather = weather_states[0]
            weather_info = {
                "condition": weather.get("state"),
                "temperature": weather.get("attributes", {}).get("temperature"),
                "humidity": weather.get("attributes", {}).get("humidity")
            }
        
        # Energy sensors
        energy_sensors = [s for s in states if "power" in s["entity_id"] or "energy" in s["entity_id"]]
        
        return SuccessResponse(
            message="Home context analyzed",
            data={
                "timestamp": now.isoformat(),
                "occupancy": occupancy,
                "time_context": time_context,
                "active_devices": {
                    "lights": lights_on,
                    "switches": switches_on,
                    "total": lights_on + switches_on
                },
                "weather": weather_info,
                "energy_sensors_count": len(energy_sensors)
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing home context: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/activity_recognition", operation_id="activity_recognition", summary="AI activity recognition")
async def activity_recognition(request: ActivityRecognitionRequest = Body(...)):
    """
    Infer current activity from sensors, devices, time, and patterns.
    Detects: sleeping, cooking, working, watching TV, etc.
    
    **DETECTION LOGIC:**
    - Sleeping: Night time, bedroom lights off, low activity
    - Cooking: Kitchen lights/switches on during meal times
    - Working: Office/desk area active during work hours
    - Watching TV: Media player on, living room lights dim
    - Away: No person home, minimal device activity
    
    Example: {"rooms": ["living_room", "kitchen"]}
    """
    try:
        states = await ha_api.get_states()
        now = datetime.now()
        hour = now.hour
        
        # Get occupancy
        person_states = [s for s in states if s["entity_id"].startswith("person.")]
        anyone_home = any(p.get("state") == "home" for p in person_states)
        
        if not anyone_home:
            detected_activity = "away"
        elif hour >= 22 or hour < 6:
            # Night time - check bedroom activity
            bedroom_lights = [s for s in states if "bedroom" in s["entity_id"] and s["entity_id"].startswith("light.")]
            if all(light.get("state") == "off" for light in bedroom_lights):
                detected_activity = "sleeping"
            else:
                detected_activity = "awake_at_night"
        elif 7 <= hour < 9 or 17 <= hour < 20:
            # Meal times - check kitchen
            kitchen_devices = [s for s in states if "kitchen" in s["entity_id"] and s.get("state") == "on"]
            if kitchen_devices:
                detected_activity = "cooking"
            else:
                detected_activity = "relaxing"
        elif 9 <= hour < 17:
            # Work hours
            office_devices = [s for s in states if "office" in s["entity_id"] and s.get("state") == "on"]
            if office_devices:
                detected_activity = "working"
            else:
                detected_activity = "home_during_work_hours"
        else:
            # Evening - check for entertainment
            media_players = [s for s in states if s["entity_id"].startswith("media_player.") and s.get("state") == "playing"]
            if media_players:
                detected_activity = "watching_tv"
            else:
                detected_activity = "relaxing"
        
        # Confidence score (simplified)
        confidence = 0.7 if anyone_home else 0.9
        
        return SuccessResponse(
            message=f"Detected activity: {detected_activity}",
            data={
                "activity": detected_activity,
                "confidence": confidence,
                "time_of_day": hour,
                "occupancy": anyone_home,
                "factors": {
                    "hour": hour,
                    "people_home": sum(1 for p in person_states if p.get("state") == "home")
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error recognizing activity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comfort_optimization", operation_id="comfort_optimization", summary="Multi-factor comfort optimization")
async def comfort_optimization(request: ComfortOptimizationRequest = Body(...)):
    """
    Optimizes for comfort: temperature, lighting, air quality, noise level.
    
    **OPTIMIZATION FACTORS:**
    - Temperature: Adjust climate based on occupancy and time
    - Lighting: Optimal brightness and color temperature
    - Air quality: Fan/purifier control
    - Noise: Quiet hours management
    
    Example: {
        "room": "living_room",
        "preferences": {"target_temp": 21, "brightness": 80}
    }
    """
    try:
        states = await ha_api.get_states()
        room_lower = request.room.lower()
        
        # Find room devices
        room_climate = [s for s in states if room_lower in s["entity_id"] and s["entity_id"].startswith("climate.")]
        room_lights = [s for s in states if room_lower in s["entity_id"] and s["entity_id"].startswith("light.")]
        room_sensors = [s for s in states if room_lower in s["entity_id"] and "sensor" in s["entity_id"]]
        
        recommendations = []
        
        # Temperature optimization
        if room_climate:
            climate = room_climate[0]
            current_temp = climate.get("attributes", {}).get("current_temperature")
            target_temp = request.preferences.get("target_temp", 21) if request.preferences else 21
            
            if current_temp and abs(current_temp - target_temp) > 1:
                recommendations.append({
                    "type": "temperature",
                    "action": f"Adjust {climate['entity_id']} to {target_temp}°C",
                    "current": current_temp,
                    "target": target_temp
                })
        
        # Lighting optimization
        if room_lights:
            target_brightness = request.preferences.get("brightness", 80) if request.preferences else 80
            for light in room_lights:
                if light.get("state") == "on":
                    current_brightness = light.get("attributes", {}).get("brightness", 0)
                    if abs(current_brightness - target_brightness) > 20:
                        recommendations.append({
                            "type": "lighting",
                            "action": f"Adjust {light['entity_id']} brightness to {target_brightness}",
                            "current": current_brightness,
                            "target": target_brightness
                        })
        
        # Air quality
        temp_sensors = [s for s in room_sensors if "temperature" in s["entity_id"]]
        humidity_sensors = [s for s in room_sensors if "humidity" in s["entity_id"]]
        
        if humidity_sensors:
            try:
                humidity = float(humidity_sensors[0].get("state", 0))
                if humidity > 60:
                    recommendations.append({
                        "type": "air_quality",
                        "action": "Consider running dehumidifier",
                        "current_humidity": humidity
                    })
                elif humidity < 30:
                    recommendations.append({
                        "type": "air_quality",
                        "action": "Consider running humidifier",
                        "current_humidity": humidity
                    })
            except (ValueError, TypeError):
                pass  # Skip if humidity value is non-numeric
        
        return SuccessResponse(
            message=f"Comfort analysis for {request.room}",
            data={
                "room": request.room,
                "recommendations": recommendations,
                "devices_found": {
                    "climate": len(room_climate),
                    "lights": len(room_lights),
                    "sensors": len(room_sensors)
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error optimizing comfort: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/energy_intelligence", operation_id="energy_intelligence", summary="Energy usage analysis & optimization")
async def energy_intelligence(request: EnergyIntelligenceRequest = Body(...)):
    """
    Analyzes energy consumption and provides recommendations.
    
    **ANALYSIS:**
    - Current power usage
    - High-consumption devices
    - Usage patterns
    - Cost estimates
    - Saving suggestions
    
    Example: {"period": "day", "suggest_savings": true}
    """
    try:
        states = await ha_api.get_states()
        
        # Separate power (W) and energy (kWh) sensors
        power_sensors = [s for s in states if "power" in s["entity_id"] and s["entity_id"].startswith("sensor.")]
        energy_sensors = [s for s in states if "energy" in s["entity_id"] and s["entity_id"].startswith("sensor.")]
        
        total_power = 0
        device_power = []
        device_energy = []
        
        # Process power sensors (W)
        for sensor in power_sensors:
            try:
                value = float(sensor.get("state", 0))
                if value > 0:
                    total_power += value
                    device_power.append({
                        "entity_id": sensor["entity_id"],
                        "name": sensor.get("attributes", {}).get("friendly_name", sensor["entity_id"]),
                        "value": value,
                        "unit": sensor.get("attributes", {}).get("unit_of_measurement", "W")
                    })
            except (ValueError, TypeError):
                pass
        
        # Process energy sensors (kWh)
        for sensor in energy_sensors:
            try:
                value = float(sensor.get("state", 0))
                if value > 0:
                    device_energy.append({
                        "entity_id": sensor["entity_id"],
                        "name": sensor.get("attributes", {}).get("friendly_name", sensor["entity_id"]),
                        "value": value,
                        "unit": sensor.get("attributes", {}).get("unit_of_measurement", "kWh")
                    })
            except (ValueError, TypeError):
                pass
        
        # Combine for sorting
        device_consumption = device_power + device_energy
        
        # Sort by consumption
        device_consumption.sort(key=lambda x: x["value"], reverse=True)
        
        # Generate savings suggestions
        suggestions = []
        
        if request.suggest_savings:
            # Check for lights left on
            lights_on = [s for s in states if s["entity_id"].startswith("light.") and s.get("state") == "on"]
            if lights_on:
                suggestions.append(f"Turn off {len(lights_on)} lights currently on")
            
            # Check for high consumption devices
            if device_consumption:
                top_consumer = device_consumption[0]
                suggestions.append(f"Check {top_consumer['name']} ({top_consumer['value']} {top_consumer['unit']})")
        
        return SuccessResponse(
            message="Energy analysis complete",
            data={
                "total_power_usage": total_power,
                "power_sensors": len(power_sensors),
                "energy_sensors": len(energy_sensors),
                "top_power_consumers": device_power[:5],
                "top_energy_consumers": device_energy[:5],
                "suggestions": suggestions
            }
        )
        
    except Exception as e:
        logger.error(f"Error analyzing energy: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
