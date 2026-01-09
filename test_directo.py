# test_directo.py
import re

# Texto de ejemplo de tu PDF
texto_ejemplo = """
Ub.Tec.: SE-ST-EAF1-02-ED-EA-01-03 CELDA DE SALIDA Gr. Plan.: AE2
Nº Aviso: 1209696498 Clase Aviso: 30 MttoCorr - Avería Urgente / Inmediato Seccionador HEA2 no entra
Nº Orden: 119818332 Estado: PLAN CNF PNR Seccionador HEA2 no entra
27.12.2025 13:25:50 CET LEONTI ALEXANDRU MATEAS (893618)
S:Nos dicen que tienen time out
"""

print("🔍 TEST DIRECTO DE EXTRACCIÓN")
print("="*70)

# Probamos diferentes patrones
patrones = [
    r'Clase Aviso:\s*\d+\s+[^-]+-\s*[^-]+-\s*([^\n]+?)(?=\s*Nº Orden:|$)',
    r'Clase Aviso:\s*\d+\s+[^-]+-\s*[^-]+-\s*([^\n]+)',
    r'Clase Aviso:\s*\d+\s+[^-\n]+-\s*[^-\n]+-\s*([^\n]+)',
    r'Estado:\s*[A-Z\s]+\s+([^\n]+?)(?=\s*\d{2}\.\d{2}\.\d{4}|$)',
    r'Estado:\s*[A-Z\s]+\s+([^\n]+)'
]

for i, patron in enumerate(patrones):
    print(f"\n🔍 Patrón {i+1}: {patron}")
    match = re.search(patron, texto_ejemplo)
    if match:
        print(f"   ✅ Encontrado: {match.group(1).strip()}")
    else:
        print("   ❌ No encontrado")

# También probar buscar el título específicamente
print("\n🎯 BUSCANDO TÍTULO ESPECÍFICO:")
# Buscar lo que viene después del tipo de aviso
titulo_match = re.search(r'Clase Aviso:\s*\d+\s+[^-\n]+-\s*[^-\n]+-\s*([^\n]+?)(?=\s*Nº Orden:|$)', texto_ejemplo)
if titulo_match:
    titulo = titulo_match.group(1).strip()
    print(f"Título extraído: '{titulo}'")
    
    # Limpiar si tiene números raros al inicio
    titulo_limpio = re.sub(r'^\d+\.?\s*', '', titulo)
    titulo_limpio = re.sub(r'^[^a-zA-ZÁÉÍÓÚÑ]+', '', titulo_limpio)
    print(f"Título limpio: '{titulo_limpio.strip()}'")