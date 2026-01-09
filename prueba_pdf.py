# prueba_pdf.py
from app.pdf_reader import leer_pdf, extraer_avisos_de_pdf
import os

# Buscar PDFs en la carpeta pdfs/
pdfs_folder = "pdfs"
pdf_files = [f for f in os.listdir(pdfs_folder) if f.lower().endswith('.pdf')]

if pdf_files:
    print(f"Encontrados {len(pdf_files)} PDFs:")
    
    for pdf_file in pdf_files:
        ruta = os.path.join(pdfs_folder, pdf_file)
        print(f"\n{'='*60}")
        print(f"ARCHIVO: {pdf_file}")
        print(f"{'='*60}")
        
        # Leer el texto completo
        texto = leer_pdf(ruta)
        
        print("\nPRIMEROS 2000 CARACTERES DEL PDF:")
        print("-" * 40)
        print(texto[:2000])
        print("-" * 40)
        
        # Probar extracción de avisos
        avisos = extraer_avisos_de_pdf(ruta)
        print(f"\nAVISOS DETECTADOS: {len(avisos)}")
        
        if avisos:
            print("\nPRIMER AVISO DETECTADO:")
            print(f"Ubicación: {avisos[0].get('ubicacion', 'No detectada')}")
            print(f"Fecha: {avisos[0].get('fecha', 'No detectada')}")
            print(f"Título: {avisos[0].get('titulo', 'No detectado')}")
            print(f"Texto (primeros 300 chars): {avisos[0].get('texto', '')[:300]}")
else:
    print("No se encontraron PDFs en la carpeta 'pdfs/'")