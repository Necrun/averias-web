# analizar_pdf.py
from app.pdf_reader import analizar_estructura_pdf
import os

print("ANALIZADOR DE ESTRUCTURA DE PDFs")
print("=" * 60)

# Buscar PDFs
pdfs_folder = "pdfs"
pdf_files = [f for f in os.listdir(pdfs_folder) if f.lower().endswith('.pdf')]

if not pdf_files:
    print("No hay PDFs en la carpeta 'pdfs/'")
    print("Sube un PDF primero en http://127.0.0.1:5000/subir")
else:
    for pdf_file in pdf_files[:2]:  # Analizar solo los 2 primeros
        ruta = os.path.join(pdfs_folder, pdf_file)
        print(f"\nAnalizando: {pdf_file}")
        print("-" * 60)
        
        texto = analizar_estructura_pdf(ruta)
        
        # Contar avisos aproximados
        conteo_ubicaciones = texto.count("Ub.Tec.:")
        print(f"\nAVISOS APROXIMADOS (por 'Ub.Tec.:'): {conteo_ubicaciones}")
        
        # Mostrar ejemplo de un aviso
        if "Ub.Tec.:" in texto:
            primer_aviso = texto.split("Ub.Tec.:")[1]
            primer_aviso = primer_aviso.split("Ub.Tec.:")[0] if "Ub.Tec.:" in primer_aviso else primer_aviso[:1000]
            
            print("\nEJEMPLO DE UN AVISO COMPLETO:")
            print("-" * 40)
            print(primer_aviso[:800])
            print("-" * 40)