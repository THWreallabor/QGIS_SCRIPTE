import geopandas as gpd
import pandas as pd
import os
from pathlib import Path

"""
Summary: 

Script, which takes .geojson and generates .shp layers for every FGr.

Known Bugs: 

All Units from Wuppertal (last OV in list) are duplicated
Trupp TS gets duplicated due to kommata in name    
"""
# Pfad zur GeoJSON-Datei
geojson_path = Path('pfadzumgeojson') # Eigenen Pfad eintragen
output_directory = './shapefiles/'  # Verzeichnis, wo die Shapefiles gespeichert werden


# GeoDataFrame aus GeoJSON-Datei 
gdf = gpd.read_file(geojson_path)

columns_to_keep = ['name','Einheiten', 'geometry'] 
gdf = gdf[columns_to_keep]


# Überprüfe, ob das Ausgabeverzeichnis existiert, und erstelle, falls nicht
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Funktion, um Spaltennamen eindeutig zu kürzen
def truncate_column_names(gdf):
    truncated = {}
    for col in gdf.columns:
        new_col = col[:10]
        # Verhindere Duplikate durch Hinzufügen von Suffixen, falls erforderlich
        suffix = 1
        while new_col in truncated.values():
            new_col = f"{col[:9]}{suffix}"
            suffix += 1
        truncated[col] = new_col
    gdf.rename(columns=truncated, inplace=True)

# Vorbereitung: Kürze die Spaltennamen im Haupt-GeoDataFrame
truncate_column_names(gdf)

# Funktion zum Aktualisieren oder Erstellen eines Shapefiles für eine Einheit
def update_or_create_shape(unit_name, feature):
    shapefile_path = os.path.join(output_directory, f'{unit_name}.shp')
    
    # Prüfe, ob Shapefile bereits existiert
    if os.path.exists(shapefile_path):
        # Lade bestehendes Shapefile
        existing_gdf = gpd.read_file(shapefile_path)
        # Füge das neue Feature zum bestehenden GeoDataFrame hinzu
        updated_gdf = pd.concat([existing_gdf, gpd.GeoDataFrame([feature], crs=existing_gdf.crs)], ignore_index=True)
    else:
        # Erstelle ein neues GeoDataFrame für das Feature
        updated_gdf = gpd.GeoDataFrame([feature], crs=gdf.crs)
    
    # Speichere GeoDataFrame als Shapefile
    # Hier ist das größte Optimierungspotential
    updated_gdf = updated_gdf.drop_duplicates()
    updated_gdf.to_file(shapefile_path, driver='ESRI Shapefile')

for idx, row in gdf.iterrows():
    # Teile die 'Einheiten' in einzelne Einheiten
    if row['Einheiten'] == None:
        pass
    else:
        units = row['Einheiten'].split(',')
    for unit in units:
        unit = unit.strip()  # Entferne Leerzeichen
        unit = unit.replace('/','')
        if unit:  # Überprüfe, ob die Einheit nicht leer ist
            # Aktualisiere oder erstelle Shapefile für die Einheit
            update_or_create_shape(unit, row)
    
print("Verarbeitung abgeschlossen. Shapefiles wurden aktualisiert oder erstellt. \n Done")