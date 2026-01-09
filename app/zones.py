# app/zones.py
def detectar_zona_general(ubicacion):
    """
    Convierte ubicación técnica a zona general
    Ejemplo: SE-ST-EAF1-01-... -> HEA1
    """
    if not ubicacion:
        return "OTROS"
    
    ubicacion = ubicacion.upper()
    
    # Reglas para zonas generales (AJUSTA ESTO SEGÚN TUS UBICACIONES REALES)
    if ubicacion.startswith("SE-ST-EAF1-01"):
        return "HEA1"
    elif ubicacion.startswith("SE-ST-EAF1-02"):
        return "HEA2"
    elif "SLM1-61" in ubicacion:
        return "HORNO CUCHARA HC1"
    elif "SLM1-62" in ubicacion:
        return "HORNO CUCHARA HC2"
    elif "CCS1" in ubicacion or "CCS2" in ubicacion:
        return "COLADA CONTINUA"
    elif "PCC1" in ubicacion or "PCC2" in ubicacion:
        return "PARQUE CHATARRA"
    elif "SE-SP-" in ubicacion:
        return "SUBESTACIÓN"
    elif "EAF1" in ubicacion:
        return "HORNOS ELÉCTRICOS"
    elif "ACERIA" in ubicacion.upper():
        return "ACERÍA"
    else:
        return "OTROS"

# Diccionario de zonas para mostrar en la web
ZONAS_DISPONIBLES = [
    "HEA1",
    "HEA2", 
    "HORNO CUCHARA HC1",
    "HORNO CUCHARA HC2",
    "COLADA CONTINUA",
    "PARQUE CHATARRA",
    "SUBESTACIÓN",
    "HORNOS ELÉCTRICOS",
    "ACERÍA",
    "OTROS"
]