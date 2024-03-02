# Importar bibliotecas necessárias
import streamlit as st
from streamlit_folium import folium_static
import geopandas as gpd
import folium
from folium import plugins
from branca.element import Template, MacroElement
import shapely.geometry
import os

# Substitua impressões por comandos Streamlit (se necessário)
st.write("O diretório de trabalho atual é:", os.getcwd())

# Função para determinar a cor com base no valor de 'VLR_M2'
def get_color(value):
    if value <= 400:
        return '#2b83ba'
    elif 400 < value <= 800:
        return '#abdda4'
    elif 800 < value <= 1200:
        return '#ffffbf'
    elif 1200 < value <= 1600:
        return '#fdae61'
    else:
        return '#d7191c'

# Função para extrair a localização de um ponto (trata MultiPoint)
def extract_location(geometry):
    if isinstance(geometry, shapely.geometry.MultiPoint):
        # Iterar sobre os pontos em um MultiPoint e pegar o primeiro ponto
        for point in geometry.geoms:
            return [point.y, point.x]
    else:
        return [geometry.y, geometry.x]

# Função para gerar ícones diferenciados em círculos e triângulos conforme origem de terrenos
def add_terreno_markers(gdf, feature_group):
    for _, row in gdf.iterrows():
        point_color = get_color(row['Valor_m2'])
        popup_text = f"Origem: {row['Origem']}<br>Valor m²: {row['Valor_m2']}<br>Rua: {row['Rua']}"
        point_location = extract_location(row.geometry)

        if row['Origem'] == 'Oferta':
            # Usar um marcador triangular para 'Oferta'
            folium.RegularPolygonMarker(
                location=point_location,
                number_of_sides=3,  # Triângulo
                radius=6,
                color=point_color,
                fill=True,
                fill_color=point_color,
                popup=folium.Popup(popup_text, max_width=265)
            ).add_to(feature_group)
        else:
            # Usar um marcador circular para 'ITC'
            folium.CircleMarker(
                location=point_location,
                radius=3,
                color=point_color,
                fill=True,
                fill_color=point_color,
                popup=folium.Popup(popup_text, max_width=265)
            ).add_to(feature_group)

# Caminhos para os arquivos GeoPackage
# (ajuste os caminhos conforme necessário, dependendo de onde os arquivos estão localizados)
path_erechim_linhas = 'D:/Receita_Estadual/OSM/erechim_logradouro_wgs84.gpkg'
path_erechim_poligonos = 'D:/Receita_Estadual/OSM/erechim_bairro_wgs84.gpkg'
path_erechim_pontos = 'D:/Receita_Estadual/OSM/erechim_terreno_wgs84.gpkg'
path_venancio_linhas = 'D:/Receita_Estadual/OSM/venancio_aires_logradouro_wgs84.gpkg'
path_venancio_poligonos = 'D:/Receita_Estadual/OSM/venancio_aires_bairro_wgs84.gpkg'
path_venancio_pontos = 'D:/Receita_Estadual/OSM/venancio_aires_terreno_wgs84.gpkg'

# Carregar os arquivos GeoPackage
gdf_linhas_erechim = gpd.read_file(path_erechim_linhas)
gdf_poligonos_erechim = gpd.read_file(path_erechim_poligonos)
gdf_pontos_erechim = gpd.read_file(path_erechim_pontos)
gdf_linhas_venancio = gpd.read_file(path_venancio_linhas)
gdf_poligonos_venancio = gpd.read_file(path_venancio_poligonos)
gdf_pontos_venancio = gpd.read_file(path_venancio_pontos)

# Definir a localização central para Erechim
central_location = [-27.639172, -52.271511]  # Coordenadas de Erechim

# Criar um mapa usando Folium
m = folium.Map(location=central_location, zoom_start=13)

# Criar Feature Groups para cada camada
fg_poligonos = folium.FeatureGroup(name='Bairro')
fg_linhas = folium.FeatureGroup(name='Logradouro')
fg_pontos = folium.FeatureGroup(name='Terreno')

# Adicionar as camadas ao mapa

# Criar FeatureGroups para Erechim
fg_erechim_bairros = folium.FeatureGroup(name='Bairros de Erechim')
fg_erechim_logradouros = folium.FeatureGroup(name='Logradouros de Erechim')
fg_erechim_terrenos = folium.FeatureGroup(name='Terrenos de Erechim')

# Adicionar os multipolígonos de bairros ao Feature Group correspondente
folium.GeoJson(
    gdf_poligonos_erechim,
    style_function=lambda x: {'color': 'black', 'weight': 5, 'dashArray': '5, 5', 'fillOpacity': 0},
    name='Bairro'
).add_to(fg_erechim_bairros)

# Adicionar as linhas de logradouros ao Feature Group correspondente
for _, row in gdf_linhas_erechim.iterrows():
    color = get_color(row['VLR_M2'])
    popup_text = f"Logradouro: {row['LOGRADOURO']}<br>" + \
                 f"Bairro: {row['TXT_BAIRRO']}<br>" + \
                 f"Valor m²: {row['VLR_M2']}<br>" + \
                 f"Nro Inicial: {row['NRO_INICIA']}<br>" + \
                 f"Nro Final: {row['NRO_FINAL']}"
    folium.GeoJson(
        row['geometry'],
        style_function=lambda x, color=color: {'color': color, 'opacity': 0.7, 'weight': 2},
        highlight_function=lambda x: {'weight': 5, 'color': 'green'}
    ).add_child(folium.Popup(popup_text, max_width=265)).add_to(fg_erechim_logradouros)

# Adicionar os pontos de terrenos de Erechim
add_terreno_markers(gdf_pontos_erechim, fg_erechim_terrenos)

# Adicionar FeatureGroups de Erechim ao mapa
fg_erechim_bairros.add_to(m)
fg_erechim_logradouros.add_to(m)
fg_erechim_terrenos.add_to(m)

# Criar FeatureGroups para Venâncio Aires
fg_venancio_bairros = folium.FeatureGroup(name='Bairros de Venâncio Aires')
fg_venancio_logradouros = folium.FeatureGroup(name='Logradouros de Venâncio Aires')
fg_venancio_terrenos = folium.FeatureGroup(name='Terrenos de Venâncio Aires')

# Adicionar os multipolígonos de bairros ao Feature Group correspondente
folium.GeoJson(
    gdf_poligonos_venancio,
    style_function=lambda x: {'color': 'black', 'weight': 5, 'dashArray': '5, 5', 'fillOpacity': 0},
    name='Bairro'
).add_to(fg_venancio_bairros)

# Adicionar as linhas de logradouros ao Feature Group correspondente
for _, row in gdf_linhas_venancio.iterrows():
    color = get_color(row['VLR_M2'])
    popup_text = f"Logradouro: {row['LOGRADOURO']}<br>" + \
                 f"Bairro: {row['TXT_BAIRRO']}<br>" + \
                 f"Valor m²: {row['VLR_M2']}<br>" + \
                 f"Nro Inicial: {row['NRO_INICIA']}<br>" + \
                 f"Nro Final: {row['NRO_FINAL']}"
    folium.GeoJson(
        row['geometry'],
        style_function=lambda x, color=color: {'color': color, 'opacity': 0.7, 'weight': 2},
        highlight_function=lambda x: {'weight': 5, 'color': 'green'}
    ).add_child(folium.Popup(popup_text, max_width=265)).add_to(fg_venancio_logradouros)

# Adicionar os pontos de terrenos de Venâncio Aires
add_terreno_markers(gdf_pontos_venancio, fg_venancio_terrenos)

# Adicionar FeatureGroups de Venâncio Aires ao mapa
fg_venancio_bairros.add_to(m)
fg_venancio_logradouros.add_to(m)
fg_venancio_terrenos.add_to(m)

# Adicionar o plugin Geocoder
plugins.Geocoder(collapsed=True, position='topleft', add_marker=True).add_to(m)

# Adicionar a legenda
template = """
{% macro html(this, kwargs) %}
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 180px; height: 130px; 
            background: white; border:2px solid grey; z-index:9999; font-size:14px; 
            padding: 5px; border-radius: 5px;">
  &nbsp; Valores de VLR_M2 <br>
  &nbsp; Até 400 &nbsp; <i style="background:#2b83ba; width: 20px; height: 10px; display: inline-block;"></i><br>
  &nbsp; 401 - 800 &nbsp; <i style="background:#abdda4; width: 20px; height: 10px; display: inline-block;"></i><br>
  &nbsp; 801 - 1200 &nbsp; <i style="background:#ffffbf; width: 20px; height: 10px; display: inline-block;"></i><br>
  &nbsp; 1201 - 1600 &nbsp; <i style="background:#fdae61; width: 20px; height: 10px; display: inline-block;"></i><br>
  &nbsp; Acima de 1600 &nbsp; <i style="background:#d7191c; width: 20px; height: 10px; display: inline-block;"></i>
</div>
{% endmacro %}
"""

macro = MacroElement()
macro._template = Template(template)

m.get_root().add_child(macro)

# Adicionar o controle de camadas
folium.LayerControl().add_to(m)

# Exibir o mapa no Streamlit em vez de salvar em um arquivo HTML
folium_static(m)
