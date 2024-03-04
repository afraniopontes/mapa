# Importar bibliotecas necessárias
import streamlit as st
from streamlit_folium import folium_static
import geopandas as gpd
import folium
from folium import plugins, IFrame  # Adicionado IFrame aqui
from branca.element import Template, MacroElement
from folium.map import LayerControl
import shapely.geometry
import os

# Substitua impressões por comandos Streamlit (se necessário)
# st.write("O diretório de trabalho atual é:", os.getcwd())



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
path_erechim_linhas = 'https://raw.githubusercontent.com/afraniopontes/mapa/main/erechim_logradouro_wgs84.gpkg'
path_erechim_poligonos = 'https://raw.githubusercontent.com/afraniopontes/mapa/main/erechim_bairro_wgs84.gpkg'
path_erechim_pontos = 'https://raw.githubusercontent.com/afraniopontes/mapa/main/erechim_terreno_wgs84.gpkg'
path_venancio_linhas = 'https://raw.githubusercontent.com/afraniopontes/mapa/main/venancio_aires_logradouro_wgs84.gpkg'
path_venancio_poligonos = 'https://raw.githubusercontent.com/afraniopontes/mapa/main/venancio_aires_bairro_wgs84.gpkg'
path_venancio_pontos = 'https://raw.githubusercontent.com/afraniopontes/mapa/main/venancio_aires_terreno_wgs84.gpkg'

# Carregar os arquivos GeoPackage
gdf_linhas_erechim = gpd.read_file(path_erechim_linhas)
gdf_poligonos_erechim = gpd.read_file(path_erechim_poligonos)
gdf_pontos_erechim = gpd.read_file(path_erechim_pontos)
gdf_linhas_venancio = gpd.read_file(path_venancio_linhas)
gdf_poligonos_venancio = gpd.read_file(path_venancio_poligonos)
gdf_pontos_venancio = gpd.read_file(path_venancio_pontos)

# Definir as localizações centrais para cada cidade
locations = {
    'Erechim': [-27.639172, -52.271511],  # Coordenadas de Erechim
    'Venâncio Aires': [-29.613557, -52.194308]  # Coordenadas de Venâncio Aires
}

# Criar uma caixa de seleção para escolher a cidade
selected_city = st.selectbox('Selecione uma cidade:', options=list(locations.keys()))

# Obter a localização central baseada na cidade selecionada
central_location = locations[selected_city]

# Ajustar o nível de zoom para a cidade selecionada
zoom_level = 13 # if selected_city == 'Erechim' else 12  # Ajuste conforme necessário para Venâncio Aires

# Criar um mapa usando Folium com a localização central e nível de zoom ajustados
m = folium.Map(location=central_location, zoom_start=zoom_level)

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



# Adicionar as camadas ao mapa de acordo com a cidade selecionada
if selected_city == 'Erechim':
    # Adicionar FeatureGroups de Erechim ao mapa
    fg_erechim_bairros.add_to(m)
    fg_erechim_logradouros.add_to(m)
    fg_erechim_terrenos.add_to(m)
elif selected_city == 'Venâncio Aires':
    # Adicionar FeatureGroups de Venâncio Aires ao mapa
    fg_venancio_bairros.add_to(m)
    fg_venancio_logradouros.add_to(m)
    fg_venancio_terrenos.add_to(m)

# Adicionar o plugin Geocoder
plugins.Geocoder(collapsed=True, position='topleft', add_marker=True).add_to(m)

# Cores e rótulos para a legenda
legend_colors = ['#2b83ba', '#abdda4', '#ffffbf', '#fdae61', '#d7191c']
legend_labels = ['Até 400', '401 - 800', '801 - 1200', '1201 - 1600', 'Acima de 1600']

# HTML para a legenda flutuante
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 180px; height: 130px; 
            background-color: rgba(255, 255, 255, 0.6);
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
            z-index:9999">
&emsp;<b>Legenda</b><br>
&emsp;<i style="background: {};"></i>&nbsp;{}<br>
&emsp;<i style="background: {};"></i>&nbsp;{}<br>
&emsp;<i style="background: {};"></i>&nbsp;{}<br>
&emsp;<i style="background: {};"></i>&nbsp;{}<br>
&emsp;<i style="background: {};"></i>&nbsp;{}<br>
</div>
'''.format(*[color for pair in zip(legend_colors, legend_labels) for color in pair])

# Adicionando a legenda ao mapa
macro = MacroElement()
macro._template = Template(legend_html)
m.get_root().add_child(macro)

# Adicionando o controle de camadas
folium.LayerControl().add_to(m)

# Exibindo o mapa no Streamlit
folium_static(m)