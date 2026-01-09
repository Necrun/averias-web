# test_titulo_especifico.py
from app.pdf_reader import extraer_avisos_de_pdf
import os

print("🔍 TEST ESPECÍFICO DE EXTRACCIÓN DE TÍTULOS")
print("="*70)

pdfs = [f for f in os.listdir('pdfs') if f.endswith('.pdf')]

if not pdfs:
    print("No hay PDFs en 'pdfs/'")
    exit()

pdf_path = os.path.join('pdfs', pdfs[0])
print(f"Analizando: {pdfs[0]}\n")

avisos = extraer_avisos_de_pdf(pdf_path)

print(f"📊 Total avisos: {len(avisos)}\n")

# Mostrar solo los primeros 10 para no saturar
for i, aviso in enumerate(avisos[:10]):
    print(f"📄 AVISO {i+1}:")
    print(f"   Título: {aviso.get('titulo', 'NO EXTRAÍDO')}")
    print(f"   Tipo: {aviso.get('tipo', '')}")
    print(f"   Ubicación: {aviso.get('ubicacion', '')}")
    print(f"   Descripción ubicación: {aviso.get('desc_ubicacion', '')}")
    print(f"   Fecha: {aviso.get('fecha', '')}")
    
    # Mostrar un poco del texto S si existe
    if aviso.get('texto_s'):
        print(f"   S: {aviso.get('texto_s', '')[:60]}...")
    
    print("-"*50)

print("\n🎯 RESUMEN DE TÍTULOS EXTRAÍDOS:")
print("="*50)
for i, aviso in enumerate(avisos[:10]):
    print(f"{i+1:2}. {aviso.get('titulo', 'SIN TÍTULO')}")