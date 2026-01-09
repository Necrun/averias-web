# app/pdf_reader.py
import pdfplumber
import re

def leer_pdf(ruta):
    """Extrae todo el texto de un PDF"""
    texto = ""
    try:
        with pdfplumber.open(ruta) as pdf:
            for page in pdf.pages:
                texto += page.extract_text() + "\n"
        return texto
    except Exception as e:
        print(f"Error leyendo PDF {ruta}: {e}")
        return ""

def limpiar_titulo(titulo):
    """Limpia el título quitando prefijos como SCE CNF, PLAN CNF, etc."""
    if not titulo:
        return "Sin título"
    
    # Lista de prefijos a eliminar
    prefijos = [
        "SCE CNF ",
        "PLAN CNF ", 
        "SCE PNR CNF ",
        "SCE ",
        "PLAN ",
        "CNF ",
        "PNR ",
        "SCE CNF",
        "PLAN CNF",
        "SCE PNR CNF"
    ]
    
    titulo_limpio = titulo.strip()
    for prefijo in prefijos:
        if titulo_limpio.startswith(prefijo):
            titulo_limpio = titulo_limpio[len(prefijo):].strip()
    
    return titulo_limpio

def extraer_avisos_de_pdf(ruta_pdf):
    """
    Extrae avisos específicamente para PDFs de Sestap
    Versión MEJORADA con manejo de casos especiales
    """
    texto = leer_pdf(ruta_pdf)
    if not texto:
        return []
    
    avisos = []
    
    # DIVIDIR POR AVISOS (cada uno empieza con "Ub.Tec.:")
    partes = re.split(r'(?=Ub\.Tec\.:\s*)', texto)
    
    for parte in partes:
        if not parte.strip() or "Ub.Tec.:" not in parte:
            continue
            
        aviso = {}
        
        # 1. UBICACIÓN TÉCNICA
        ubic_match = re.search(r'Ub\.Tec\.:\s*([A-Za-z0-9\-]+)', parte)
        aviso['ubicacion'] = ubic_match.group(1) if ubic_match else ""
        
        # 2. DESCRIPCIÓN DE LA UBICACIÓN
        desc_match = re.search(r'Ub\.Tec\.:\s*[A-Za-z0-9\-]+\s+([^\n]+?)(?=\s+Gr\. Plan\.:|$)', parte)
        aviso['desc_ubicacion'] = desc_match.group(1).strip() if desc_match else ""
        
        # 3. NÚMERO DE AVISO
        aviso_match = re.search(r'Nº Aviso:\s*(\d+)', parte)
        aviso['num_aviso'] = aviso_match.group(1) if aviso_match else ""
        
        # 4. CLASE/TIPO DE AVISO (20, 30, 60)
        tipo_match = re.search(r'Clase Aviso:\s*(\d+)', parte)
        aviso['tipo'] = int(tipo_match.group(1)) if tipo_match else 0
        
        # 5. DESCRIPCIÓN DEL TIPO
        tipo_desc_match = re.search(r'Clase Aviso:\s*\d+\s+([^-]+-\s*[^-]+)', parte)
        aviso['tipo_desc'] = tipo_desc_match.group(1).strip() if tipo_desc_match else ""
        
        # 6. NÚMERO DE ORDEN
        orden_match = re.search(r'Nº Orden:\s*(\d+)', parte)
        aviso['num_orden'] = orden_match.group(1) if orden_match else ""
        
        # 7. ESTADO
        estado_match = re.search(r'Estado:\s*([A-Z\s]+)', parte)
        aviso['estado'] = estado_match.group(1).strip() if estado_match else ""
        
        # 8. TÍTULO REAL - ESTRATEGIA MEJORADA
        titulo_encontrado = False
        
        # Estrategia 1: Buscar después de "Clase Aviso:"
        titulo_match = re.search(r'Clase Aviso:\s*\d+\s+[^-]+-\s*[^-]+-\s*([^\n]+?)(?=\s*Nº Orden:|$)', parte)
        
        if titulo_match:
            titulo_crudo = titulo_match.group(1).strip()
            # Limpiar
            titulo_crudo = re.sub(r'^\d+\.?\s*', '', titulo_crudo)
            titulo_crudo = re.sub(r'^[^a-zA-ZÁÉÍÓÚÑ]+', '', titulo_crudo)
            if titulo_crudo.strip():
                aviso['titulo'] = titulo_crudo.strip()
                titulo_encontrado = True
        
        # Estrategia 2: Buscar después de "Estado:"
        if not titulo_encontrado:
            titulo_match = re.search(r'Estado:\s*[A-Z\s]+\s+([^\n]+?)(?=\s*\d{2}\.\d{2}\.\d{4}|$)', parte)
            if titulo_match:
                titulo_crudo = titulo_match.group(1).strip()
                # Limpiar prefijos comunes
                prefijos = ['PLAN CNF PNR', 'PLAN CNF', 'SCE CNF', 'CNF', 'PNR']
                for prefijo in prefijos:
                    if titulo_crudo.startswith(prefijo):
                        titulo_crudo = titulo_crudo[len(prefijo):].strip()
                
                if titulo_crudo.strip():
                    aviso['titulo'] = titulo_crudo.strip()
                    titulo_encontrado = True
        
        # Estrategia 3: Si no hay título, usar descripción de ubicación
        if not titulo_encontrado:
            if aviso.get('desc_ubicacion'):
                aviso['titulo'] = aviso['desc_ubicacion']
                titulo_encontrado = True
            elif aviso.get('ubicacion'):
                # Usar parte de la ubicación como título
                partes_ubic = aviso['ubicacion'].split('-')
                if len(partes_ubic) > 2:
                    aviso['titulo'] = f"{partes_ubic[-2]}-{partes_ubic[-1]}"
                else:
                    aviso['titulo'] = aviso['ubicacion'][-15:]
                titulo_encontrado = True
        
        # Estrategia 4: Si nada funciona
        if not titulo_encontrado:
            aviso['titulo'] = "Aviso técnico"
        
        # 9. FECHA Y HORA
        fecha_match = re.search(r'(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})', parte)
        aviso['fecha_completa'] = fecha_match.group(1) if fecha_match else ""
        aviso['fecha'] = fecha_match.group(1)[:16] if fecha_match else ""
        
        # 10. PERSONA
        persona_match = re.search(r'CET\s+([A-ZÑÁÉÍÓÚ\s]+)(?=\s*\(\d+\)|$)', parte)
        aviso['persona'] = persona_match.group(1).strip() if persona_match else ""
        
        # 11. EXTRAER TEXTO S/O/R/A
        texto_inicio = 0
        if fecha_match:
            fecha_pos = parte.find(fecha_match.group(1))
            if fecha_pos != -1:
                siguiente_linea = parte.find('\n', fecha_pos)
                if siguiente_linea != -1:
                    texto_inicio = siguiente_linea + 1
        
        texto_aviso = parte[texto_inicio:].strip() if texto_inicio > 0 else parte
        
        # Limpiar texto
        lineas_limpias = []
        for linea in texto_aviso.split('\n'):
            linea_limpia = linea.strip()
            if (not linea_limpia.startswith('Nº Notificación') and 
                not linea_limpia.startswith('L.Notif:') and
                not linea_limpia.startswith('Trabajo:') and
                not re.match(r'^\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}', linea_limpia)):
                lineas_limpias.append(linea_limpia)
        
        texto_limpiado = '\n'.join(lineas_limpias)
        
        # Buscar S:/O:/R:/A:
        texto_s = ""
        texto_o = ""
        texto_r = ""
        texto_a = ""
        
        s_match = re.search(r'S:\s*(.+?)(?=\s*(?:O:|R:|A:|$))', texto_limpiado, re.DOTALL | re.IGNORECASE)
        texto_s = s_match.group(1).strip() if s_match else ""
        
        o_match = re.search(r'O:\s*(.+?)(?=\s*(?:S:|R:|A:|$))', texto_limpiado, re.DOTALL | re.IGNORECASE)
        texto_o = o_match.group(1).strip() if o_match else ""
        
        r_match = re.search(r'R:\s*(.+?)(?=\s*(?:S:|O:|A:|$))', texto_limpiado, re.DOTALL | re.IGNORECASE)
        texto_r = r_match.group(1).strip() if r_match else ""
        
        a_match = re.search(r'A:\s*(.+?)(?=\s*(?:S:|O:|R:|$))', texto_limpiado, re.DOTALL | re.IGNORECASE)
        texto_a = a_match.group(1).strip() if a_match else ""
        
        # 12. GUARDAR TEXTOS
        aviso['texto_s'] = texto_s
        aviso['texto_o'] = texto_o
        aviso['texto_r'] = texto_r
        aviso['texto_a'] = texto_a
        
        # Texto completo formateado
        texto_completo = ""
        if texto_s:
            texto_completo += f"S: {texto_s}\n"
        if texto_o:
            texto_completo += f"O: {texto_o}\n"
        if texto_r:
            texto_completo += f"R: {texto_r}\n"
        if texto_a:
            texto_completo += f"A: {texto_a}\n"
        
        if not texto_completo and texto_limpiado:
            texto_completo = texto_limpiado
        
        aviso['texto_completo'] = texto_completo.strip()
        
        # Solo añadir si tiene ubicación
        if aviso['ubicacion']:
            avisos.append(aviso)
    
    return avisos