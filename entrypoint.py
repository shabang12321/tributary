# import the flask web framework
from flask import Flask, request, jsonify

# create a Flask server, and allow us to interact with it using the app variable
app = Flask(__name__)

HISTORY_LENGTH = 10
DATA_KEY = "engine_temperature"

@app.route('/record', methods=['GET'])
def get_engine_temperatures():
    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"Retrieved engine temperature values: {engine_temperature_values}")
    return jsonify({
        "engine_temperatures": engine_temperature_values,
        "count": len(engine_temperature_values)
    })

@app.route('/record', methods=['POST'])
def record_engine_temperature():
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")

    engine_temperature = payload.get("engine_temperature")
    logger.info(f"engine temperature to record is: {engine_temperature}")

    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")

    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine temperature list now contains these values: {engine_temperature_values}")

    logger.info(f"record request successful")
    return {"success": True}, 200

# practically identical to the above
@app.route('/collect', methods=['POST'])
def collect_engine_temperature():
    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    
    # Get all temperature values
    temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"Retrieved temperature values: {temperature_values}")
    
    if not temperature_values:
        return {
            "current_engine_temperature": None,
            "average_engine_temperature": None
        }, 200
    
    # Convert string values to floats
    temperature_values = [float(temp) for temp in temperature_values]
    
    # Get the most recent temperature (first in the list)
    current_temperature = temperature_values[0]
    
    # Calculate the average temperature
    average_temperature = sum(temperature_values) / len(temperature_values)
    
    logger.info(f"Current temperature: {current_temperature}, Average temperature: {average_temperature}")
    
    return {
        "current_engine_temperature": current_temperature,
        "average_engine_temperature": average_temperature
    }, 200

import json
import redis as redis
from flask import Flask, request
from loguru import logger

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

