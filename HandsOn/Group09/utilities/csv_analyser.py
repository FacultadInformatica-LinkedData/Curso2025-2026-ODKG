import pandas as pd
import sys
import numpy as np
import re

def analizar_dataset_definitivo(archivo_csv):
    """
    Analiza un archivo CSV mostrando un resumen completo, detectando tipos de
    datos, fechas, coordenadas y valores categóricos.
    """
    print(f"\n===================================================================")
    print(f"  Analizando el archivo: {archivo_csv}")
    print(f"===================================================================")

    try:
        df = pd.read_csv(archivo_csv, encoding='utf-8', low_memory=False)
    except FileNotFoundError:
        print(f"--- ERROR: No se pudo encontrar el archivo. ---")
        return
    except Exception as e:
        print(f"--- ERROR al leer el archivo: {e} ---")
        return

    # --- Información General ---
    total_rows, total_cols = df.shape
    print("\n--- INFO GENERAL ---")
    print(f"Total de Filas: {total_rows}")
    print(f"Total de Columnas: {total_cols}\n")

    # --- Resumen por Columna ---
    print("--- DETALLES POR COLUMNA ---")
    # Expresión regular para detectar tuplas de coordenadas, ej: (12.34, -56.78)
    coord_pattern = re.compile(r'^\s*\(\s*[-+]?\d*\.?\d+\s*,\s*[-+]?\d*\.?\d+\s*\)\s*$')

    for col in df.columns:
        print(f"\n-> Columna: '{col}'")
        col_data = df[col].dropna() # Trabajar sin nulos para el análisis
        
        # Información básica
        dtype = str(df[col].dtype)
        missing_values = df[col].isnull().sum()
        unique_values = col_data.nunique()
        
        print(f"   - Tipo de Dato Original: {dtype}")
        print(f"   - Valores Ausentes: {missing_values}")
        print(f"   - Valores Únicos: {unique_values}")

        # Lógica para determinar el tipo de dato y el rango
        detected_type = "Desconocido"
        range_info = "No aplicable"
        
        # 1. Si es numérico
        if np.issubdtype(df[col].dtype, np.number):
            detected_type = "Numérico"
            if not col_data.empty:
                min_val, max_val = col_data.min(), col_data.max()
                range_info = f"{min_val} — {max_val}"
        
        # 2. Si es tipo 'object', puede ser fecha, coordenada o categoría
        elif dtype == 'object':
            if col_data.empty:
                detected_type = "Categórico (vacío)"
                range_info = "Sin datos para analizar"
            else:
                # Intentar convertir a fecha
                temp_dates = pd.to_datetime(col_data, errors='coerce')
                
                # Intentar detectar coordenadas
                is_coord = col_data.astype(str).str.match(coord_pattern).sum()

                # Decidir el tipo basado en la detección
                if (temp_dates.notna().sum() / len(col_data) > 0.75):
                    detected_type = "Fecha"
                    min_date = temp_dates.min().strftime('%Y-%m-%d')
                    max_date = temp_dates.max().strftime('%Y-%m-%d')
                    range_info = f"{min_date} — {max_date}"
                elif (is_coord / len(col_data) > 0.75):
                    detected_type = "Coordenada"
                    uniques = col_data.unique()
                    range_info = ", ".join(uniques[:3]) + ", ..." # Mostrar 3 ejemplos
                else:
                    detected_type = "Categórico"
                    uniques = col_data.unique()
                    if unique_values <= 6:
                        range_info = ", ".join(map(str, uniques))
                    else:
                        range_info = ", ".join(map(str, uniques[:5])) + ", ..."
        
        print(f"   - Tipo de Dato Detectado: {detected_type}")
        print(f"   - Rango / Valores Principales: {range_info}")

    print(f"\n===================================================================")
    print(f"  Fin del análisis para: {archivo_csv}")
    print(f"===================================================================\n\n")


import os

if __name__ == "__main__":

    folder_path = "git_folder/Curso2025-2026-ODKG/HandsOn/Group09/csv"

    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} no es una carpeta válida.")
    else:
        csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]

        if not csv_files:
            print("No se encontraron archivos CSV en la carpeta.")
        else:
            for csv_file in csv_files:
                file_path = os.path.join(folder_path, csv_file)
                print(f"\n📂 Procesando: {file_path}")
                analizar_dataset_definitivo(file_path)
