import os
from pathlib import Path

from sqlalchemy.engine import URL


BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
START_DATE = "2026-03-01 07:30"
END_DATE = "2026-11-20 07:29"
DATE_COLUMN = "e.encounter_datetime"

BASE_QUERY = """
SELECT
    v.date_started,
    v.date_stopped,
    e.encounter_id,
    e.visit_id,
    e.patient_id,
    e.program_id,
    e.encounter_datetime,
    e.encounter_type,
    et.name AS encounter_type_name,
    o.obs_id,
    o.concept_id,
    o.value_text,
    o.value_coded,
    cn.name AS concept_name,
    cnn.name AS coded_value_name
FROM encounter e
JOIN visit v ON e.visit_id = v.visit_id AND v.voided = 0
JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
LEFT JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0
LEFT JOIN concept_name cn
    ON o.concept_id = cn.concept_id
    AND cn.locale = 'en'
    AND cn.concept_name_type = 'FULLY_SPECIFIED'
    AND cn.voided = 0
LEFT JOIN concept_name cnn
    ON o.value_coded = cnn.concept_id
    AND cnn.locale = 'en'
    AND cnn.concept_name_type = 'FULLY_SPECIFIED'
    AND cnn.voided = 0
WHERE e.voided = 0
AND {date_filter}
"""

# HARMONIZED MAHIS (DB1)
SOURCE1 = {
    "URL": URL.create(
        "mysql+pymysql",
        username="",
        password="",
        host="localhost",
        port=3306,
        database="",
    ),
    "USE_SSH": False,
    "USE_KEY": False,
    "SSH_CONFIG": {
        "HOST": "",
        "PORT": 22,
        "USERNAME": "",
        "PASSWORD": "",
        "KEY_PATH": INPUT_DIR / "ssh_key",
    },
}

# QECH AETC (DB2)
SOURCE2 = {
    "URL": URL.create(
        "mysql+pymysql",
        username="",
        password="",
        host="localhost",
        port=3306,
        database="",
    ),
    "USE_SSH": False,
    "USE_KEY": False,
    "SSH_CONFIG": {
        "HOST": "",
        "PORT": 22,
        "USERNAME": "",
        "PASSWORD": "",
        "KEY_PATH": INPUT_DIR / "ssh_key",
    },
}