import pandas as pd
import configparser, os
from sqlalchemy import create_engine

def load_user_data():
    return pd.DataFrame({"Name": ["Alice", "Bob"], "Age": [25, 30]})

def fetch_data(conn_str, query):
    engine = create_engine(conn_str)
    raw_conn = engine.raw_connection()
    try:
        return pd.read_sql(query, raw_conn)
    finally:
        raw_conn.close()

def connection_str(dbname:str):
    config_path = "./config.ini"
    print(os.path.abspath(config_path))
    print(os.path.exists(config_path))

    # ตรวจสอบว่าไฟล์ config มีอยู่หรือไม่
    if not os.path.exists(config_path):
        return {
            "data": "",
            "status": "false",
            "message": f"Config file not found at path: {config_path}"
        }

    config = configparser.ConfigParser()
    config.read(config_path)

    if "database" not in config:
        return {
            "data" : "",
            "status": "false",
            "message": "Missing [database] section in config file"
        }

    db_config = config["database"]
    required_keys = ["user", "password", "host", "port"]

    try:
        for key in required_keys:
            if key not in db_config or db_config[key].strip() == "":
                return {
                    "data" : "",
                    "status": "false",
                    "message": f"Missing or empty config key: '{key}'"
                }

        connection_url = (
            f"postgresql://{db_config['user']}:"
            f"{db_config['password']}@"
            f"{db_config['host']}:"
            f"{db_config['port']}/"
            f"{dbname}"
        )
    except KeyError as e:
        return {
            "data" : "",
            "status": "false",
            "message": f"Missing required config key: {e}"
        }

    print(f"Connected to {db_config['host']}")

    return {
        "data": connection_url,
        "status": "ok",
        "message":"success"
    }

def get_chart_location_label(region, state, city):
    if city != "ทั้งหมด" and city != "โปรดเลือกจังหวัดก่อน":
        return f"{state} : {city}"
    elif state != "ทั้งหมด" and state != "โปรดเลือกภูมิภาคก่อน":
        return state
    elif region != "ทั้งหมด":
        return f"ภูมิภาค {region}"
    else:
        return "ทั้งประเทศ"