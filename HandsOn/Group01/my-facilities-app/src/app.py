import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import altair as alt

from queries import (
    get_facilities_by_type,
    get_neighbourhoods,
    get_facilities_in_neighbourhood,
    get_districts,
    get_neighbourhoods_in_district,
    get_facilities_by_type_and_neighbourhood,
    get_facilities_by_types,
    get_nearby_transport,
    get_linked_wiki_info,
    FACILITY_CLASS_MAP,
    FACILITY_MAIN_TYPES,
    FACILITY_SUBTYPES_BY_MAIN,
    ALL_FACILITY_TYPES,
)




st.set_page_config(page_title="Smart City Facilities", page_icon="../logo.png",layout="wide")

# ✅ Cabecera con logo + título
col1, col2 = st.columns([0.2, 0.8])
with col1:
    st.image("../logo.png", use_container_width=True)  
with col2:
    st.markdown("""
        <div style='padding-top:10px;'>
            <h1 style='color:#003366; font-size:42px; margin-bottom:0;'>Bienvenido a Madrid: Explora sus instalaciones inteligentes</h1>
            <h3 style='color:#551; font-size:25px; margin-bottom:0;'>Aquí podrás descubrir toda la información sobre los espacios y servicios de la ciudad. ¿Qué quieres explorar hoy? 🔍</h3>
        </div>
    """, unsafe_allow_html=True)



# --- FILTRADO COMBINADO POR DEFECTO (SIN SIDEBAR, MULTI-FACILITY) ---

df = pd.DataFrame()

# Layout central dividido
col1, col2 = st.columns(2)

# --------- COLUMNA IZQUIERDA: FACILITIES 🏗️ ---------
with col1:
    st.markdown("### 🏗️ Filtros por Facility")

    # Tipo principal
    main_choice = st.selectbox(
        "Tipo principal de facility",
        ["Ninguno"] + FACILITY_MAIN_TYPES,
        index=0,
    )

    # Subtipos disponibles
    type_options = ALL_FACILITY_TYPES if main_choice == "Ninguno" else FACILITY_SUBTYPES_BY_MAIN.get(main_choice, [])

    if not type_options:
        st.warning("No hay subtipos configurados para este tipo de facility.")
        st.stop()

    # MULTISELECCIÓN DE FACILITIES
    selected_types = st.multiselect(
        "Subtipos de facility (puedes elegir varios)",
        type_options,
        default=[]
    )

    # --- NUEVA LÓGICA: si hay tipo principal y no se selecciona subclase, usar todas ---
    if main_choice != "Ninguno" and not selected_types:
        selected_types = type_options  # selecciona automáticamente todas las subclases






# --------- COLUMNA DERECHA: BARRIOS 🏙️ ---------
with col2:
    st.markdown("### 🏙️ Filtros por Barrio")

    nh_list = get_neighbourhoods()
    neighbourhood_names = [n[1] for n in nh_list]

    selected_neighbourhood = st.selectbox(
        "Selecciona barrio",
        ["Todos"] + neighbourhood_names,
        index=0
    )


# --------- LÓGICA DE FILTRADO (MULTI-FACILITY) ---------

use_facility = len(selected_types) > 0
use_neighbourhood = selected_neighbourhood != "Todos"

nh_uri = None
if use_neighbourhood:
    nh_uri = [uri for uri, name in nh_list if name == selected_neighbourhood][0]

frames = []

# Caso 1: facilities seleccionadas
if use_facility:

    for t in selected_types:

        if use_neighbourhood:
            # facility + barrio
            partial = pd.DataFrame(get_facilities_by_type_and_neighbourhood(t, nh_uri))
        else:
            # solo facilities
            partial = pd.DataFrame(get_facilities_by_type(t))

        if not partial.empty:
            frames.append(partial)

    if frames:
        df = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["uri"]).reset_index(drop=True)
    else:
        df = pd.DataFrame()



# Caso 2: solo barrio
# elif use_neighbourhood:

#     df = pd.DataFrame(get_facilities_in_neighbourhood(nh_uri))

# elif use_neighbourhood:

#     df = pd.DataFrame(get_facilities_in_neighbourhood(nh_uri))
    
#     # 🆕 FIX: Añadir la columna 'neighbourhood' que falta en esta función
#     if not df.empty:
#         df['neighbourhood'] = selected_neighbourhood


# Caso 2: solo barrio
elif use_neighbourhood:

    df_raw = pd.DataFrame(get_facilities_in_neighbourhood(nh_uri))
    
    if not df_raw.empty:
        # 🆕 PASO 1: Eliminar duplicados por URI. Usamos keep='last'
        # Esto intenta mantener la clase más específica si la consulta la devuelve al final.
        df = df_raw.drop_duplicates(subset=['uri'], keep='last').reset_index(drop=True)

        # 🆕 PASO 2: Añadir la columna 'neighbourhood' (el fix obligatorio)
        df['neighbourhood'] = selected_neighbourhood
        
    else:
        df = pd.DataFrame() # Vacío si no hay resultados



# Caso 3: ningún filtro → TODO (sin get_all_facilities)
else:

    frames = []
    for t in ALL_FACILITY_TYPES:
        try:
            part = pd.DataFrame(get_facilities_by_type(t))
            if not part.empty:
                frames.append(part)
        except:
            continue

    if frames:
        df = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["uri"]).reset_index(drop=True)
    else:
        df = pd.DataFrame()

# --------- TÍTULO DEL RESULTADO ---------

fac_str = ", ".join(selected_types) if selected_types else "todas las facilities"
zone_str = selected_neighbourhood if use_neighbourhood else "todas las zonas"

st.subheader(f"Resultados – {fac_str} en {zone_str}")







col1, col2 = st.columns(2)

with col1:

    # --- Mostrar resultados si hay dataframe ---
    if not df.empty:
        st.caption(f"{len(df)} resultados")
        
        # 🆕 AÑADIR SELECTOR DE VISTA
        view_mode = st.radio(
            "Seleccionar vista",
            ["Tabla de Datos", "Resumen por Tipo"],
            horizontal=True,
            index=0,
        )

        if view_mode == "Tabla de Datos":
            # ➡️ VISTA DE TABLA ORIGINAL
            st.dataframe(
                df[["name","class","neighbourhood","district","municipality","telephone","email","uri"]],
                use_container_width=True,
                hide_index=True
            )
        
        elif view_mode == "Resumen por Tipo":
            # ➡️ VISTA DE RESUMEN
            st.subheader("📊 Resumen de Facilities por Tipo")

            # Contar el número de facilities por su 'class'
            class_counts = df["class"].value_counts().reset_index()
            class_counts.columns = ["Tipo de Facility", "Nº de Resultados"]
            
            # Mostrar tabla de resumen
            st.dataframe(class_counts, use_container_width=True, hide_index=True)
            
            # Opcional: Mostrar un gráfico de barras (usando el gráfico nativo de Streamlit)
            # st.bar_chart(class_counts.set_index("Tipo de Facility"), color="#C8DFF6")
            
            chart = alt.Chart(class_counts).mark_bar().encode(   
            x=alt.X('Tipo de Facility', axis=alt.Axis(labelAngle=0,title='Tipo de Facility')),y=alt.Y('Nº de Resultados', title='Nº de Resultados'),color=alt.value("#C8DFF6")).properties(title="Distribución de Facilities por Tipo" ).interactive()
            st.altair_chart(chart, use_container_width=True)
            
    else:
        st.info("No se han encontrado instalaciones que coincidan con los filtros seleccionados. Intenta cambiar los criterios de búsqueda.")


with col2:
    # --- Mapa ---
        if df.empty:
            st.warning("No existen instalaciones que coincidan con los filtros seleccionados.")
            st.stop()

        if not {"lat", "long"}.issubset(df.columns):
            st.warning("Los datos filtrados no contienen coordenadas para mostrar en el mapa.")
            st.stop()

        # Si pasa las validaciones, ahora sí podemos hacer dropna
        map_df = df.dropna(subset=["lat","long"]).copy()

        map_df = df.dropna(subset=["lat","long"]).copy()
        if not map_df.empty:
            m = folium.Map(location=[40.4168, -3.7038], zoom_start=11, tiles="cartodbpositron")
            for _, row in map_df.iterrows():
                html = f"""
                <b>{row['name']}</b><br/>
                <i>{row['class']}</i><br/>
                Barrio: {row.get('neighbourhood','-')}<br/>
                Distrito: {row.get('district','-')}<br/>
                Municipio: {row.get('municipality','-')}<br/>
                Tel: {row.get('telephone','-')}<br/>
                Email: {row.get('email','-')}<br/>
                <small>{row['uri']}</small>
                """
                folium.Marker(
                    [row["lat"], row["long"]],
                    popup=folium.Popup(html, max_width=300),
                    tooltip=row["name"],
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)
            st_folium(m, height=600, width=None)










# -------------------------------------------------
# --- Detalle + de la facility, nuestros + wikidata
# -------------------------------------------------

st.divider()
st.subheader("Detalle y transporte cercano")
# 💡 FIX: Usamos una key única para evitar el error StreamlitDuplicateElementId
pick = st.selectbox("Selecciona una facility", df["name"].tolist(), key="facility_selector")

col1, col2 = st.columns(2)

with col1:
    
    if pick:
        sel = df[df["name"] == pick].iloc[0]
        
        # 1. OBTENER WIKIDATA DE INMEDIATO (para usarlo más tarde)
        wiki = get_linked_wiki_info(sel["uri"], lang="es")
        fac = wiki.get("facility", {}) or {} # Datos enriquecidos de la Facility
        
        # --- FUNCIÓN AUXILIAR DE POBLACIÓN (Se mantiene) ---
        def format_population(info: dict) -> str:
            pop = info.get("population")
            if not pop:
                return "—"
            val = pop.get("value")
            if val is None:
                return "—"
            try:
                val_int = int(val)
                val_str = f"{val_int:,}".replace(",", ".")
            except Exception:
                val_str = str(val)
            year = pop.get("year")
            if year:
                return f"{val_str} (año {year})"
            return val_str
        # --------------------------------------------------

        # 🆕 BLOQUE 1: INFORMACIÓN BÁSICA (LOCAL)
        st.markdown("#### 📝 Información Básica de Contacto y Ubicación")
        st.markdown(
            f"""
            <div style='background-color: #f0f2f6; border-left: 5px solid #003366; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
                <h4 style='color:#003366; margin-top:0;'>{sel['name']}</h4>
                <p style='margin:0;'><strong>Tipo:</strong> {sel['class']}</p>
                <p style='margin:0;'><strong>Barrio:</strong> {sel.get('neighbourhood','—')} | <strong>Distrito:</strong> {sel.get('district','—')}</p>
                <p style='margin:0;'><strong>Teléfono:</strong> {sel.get('telephone','—')} | <strong>Email:</strong> {sel.get('email','—')}</p>
                <p style='margin:0;'><small><strong>URI Local:</strong> {sel['uri']}</small></p>
            </div>
            """, unsafe_allow_html=True
        )
    

with col2:


    with st.expander("🌐 Información Enriquecida de Wikidata (Detalle y Contexto)", expanded=True):
        
        # --- SUB-BLOQUE A: DATOS ESPECÍFICOS DE LA FACILITY (WD) ---
        # if fac.get("uri"):
        #     st.markdown("#### ℹ️ Datos Adicionales de la Instalación")
            
        #     website = fac.get("website")
            
        #     st.markdown(
        #         f"""
        #         <div style='border: 1px dashed #ced4da; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
        #             <p style='margin: 0;'><strong>Etiqueta Wikidata:</strong> {fac.get('label') or '—'}</p>
        #             <p style='margin: 0;'><strong>Dirección (WD):</strong> {fac.get('street_address') or '—'}</p>
        #             <p style='margin: 0;'><strong>Código Postal (WD):</strong> {fac.get('postal_code') or '—'}</p>
        #             <p style='margin: 0;'><strong>Web Oficial (WD):</strong> {f"<a href='{website}' target='_blank'>{website}</a>" if website else '—'}</p>
        #             <p style='margin: 0;'><small><strong>URI Wikidata:</strong> [{fac['uri']}]({fac['uri']})</small></p>
        #         </div>
        #         """, unsafe_allow_html=True
        #     )
        # else:
        #     st.info("No se encontró información enlazada de Wikidata para esta Facility.")


        # --- SUB-BLOQUE A: DATOS ESPECÍFICOS DE LA FACILITY (WD) ---
        if fac.get("uri"):
            st.markdown("#### ℹ Datos Adicionales de la Instalación")
        
            website = fac.get("website")
            img = fac.get("image")
            inception = fac.get("inception") or "—"
            part_of = fac.get("part_of") or []
        
            # Construimos el HTML
            html = f"""
            <div style='border: 1px dashed #ced4da; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
                <p style='margin: 0;'><strong>Etiqueta Wikidata:</strong> {fac.get('label') or '—'}</p>
                <p style='margin: 0;'><strong>Dirección (WD):</strong> {fac.get('street_address') or '—'}</p>
                <p style='margin: 0;'><strong>Código Postal (WD):</strong> {fac.get('postal_code') or '—'}</p>
                <p style='margin: 0;'><strong>Web Oficial (WD):</strong> {f"<a href='{website}' target='_blank'>{website}</a>" if website else '—'}</p>
                <p style='margin: 0;'><strong>Año de creación:</strong> {inception}</p>
                <p style='margin: 0;'><strong>Pertenece a:</strong> {", ".join(part_of) if part_of else '—'}</p>
                <p style='margin: 0;'><small><strong>URI Wikidata:</strong> <a href='{fac["uri"]}' target='_blank'>{fac["uri"]}</a></small></p>
            </div>
            """
        
            st.markdown(html, unsafe_allow_html=True)
        
            # Imagen separada, fuera del bloque HTML
            if img:
                st.markdown("*Imagen (Wikidata):*")
                st.image(img, width=250)
        
        else:
            st.info("No se encontró información enlazada de Wikidata para esta Facility.")








# -------------------------------------------------
# BLOQUE 2: TRANSPORTE CERCANO (Se mantiene el formato card)
# -------------------------------------------------
st.divider()


col1, col2 = st.columns(2)

with col1:

    tr = get_nearby_transport(sel["uri"])
    st.markdown("#### 🔗 Conexiones de Transporte")

    # NOTE: Definición de format_transport_info (asegúrate de que esté en el ámbito)
    def format_transport_info(icon, title, data):
        html = f"<div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px; height: 100%;'>"
        html += f"<h4 style='margin-top:0; color:#003366;'>{icon} {title}</h4>"
        
        if data:
            for name, d in data.items():
                lines = ", ".join(d["lines"]) if d["lines"] else "—"
                stations = ", ".join(d["stations"]) if d["stations"] else "—"
                # html += f"<p style='margin: 0; padding-bottom: 5px;'>**{name}**</p>"
                html += f"<p style='margin: 0 0 5px 0; font-size: 14px;'>Líneas: {lines}</p>"
                if d['stations']:
                    html += f"<p style='margin: 0 0 5px 0; font-size: 14px;'>Estaciones: {stations}</p>"
        else:
            html += f"<p style='color: #6c757d;'>No hay datos de {title.lower()} cercanos.</p>"

        html += "</div>"
        return html

    cols = st.columns(3)
    cols[0].markdown(format_transport_info("🚇", "Metro", tr["Subway"]), unsafe_allow_html=True)
    cols[1].markdown(format_transport_info("🚌", "Bus", tr["Bus"]), unsafe_allow_html=True)
    cols[2].markdown(format_transport_info("🚆", "Cercanías", tr["Train"]), unsafe_allow_html=True)



    
with col2:

# --- SUB-BLOQUE B: DATOS GEOGRÁFICOS ENRIQUECIDOS (WD) ---
    st.markdown("#### 🏛️ Contexto Geográfico y Gubernamental")

    col_w1, col_w2 = st.columns(2)

    # --- MUNICIPIO + BARRIO (Columna 1) ---
    with col_w1:
        
        # --- MUNICIPIO ---
        mun = wiki.get("municipality", {}) or {}
        mun_label = mun.get("label") or sel.get("municipality") or "—"
        st.markdown(f"##### Municipio de {mun_label}")
        
        if mun.get("uri"):
            st.markdown(f"[[Wikidata]({mun['uri']})]")

        st.markdown(f"* **Población:** {format_population(mun)}")
        st.markdown(f"* **Jefatura:** {', '.join(mun.get('head', [])) or '—'} (Cargo: {', '.join(mun.get('office', [])) or '—'})")
        st.markdown(f"* **Órgano Ejecutivo:** {', '.join(mun.get('executive_body', [])) or '—'}")

        st.markdown("---")

        # --- BARRIO ---
        nh = wiki.get("neighbourhood", {}) or {}
        nh_label = nh.get("label") or sel.get("neighbourhood") or "—"
        st.markdown(f"##### Barrio de {nh_label}")
        
        if nh.get("uri"):
            st.markdown(f"[[Wikidata]({nh['uri']})]")

        st.markdown(f"* **Población:** {format_population(nh)}")
        borders = nh.get("borders") or []
        borders_str = ", ".join(borders) if borders else "—"
        st.markdown(f"* **Limita con:** {borders_str}")

    # --- DISTRITO (Columna 2) ---
    with col_w2:
        
        dist = wiki.get("district", {}) or {}
        dist_label = dist.get("label") or sel.get("district") or "—"
        st.markdown(f"##### Distrito de {dist_label}")

        if dist.get("uri"):
            st.markdown(f"[[Wikidata]({dist['uri']})]")
            
        st.markdown(f"* **Población:** {format_population(dist)}")
        st.markdown(f"* **Jefatura:** {', '.join(dist.get('head', [])) or '—'} (Cargo: {', '.join(dist.get('office', [])) or '—'})")
        st.markdown(f"* **Órgano Ejecutivo:** {', '.join(dist.get('executive_body', [])) or '—'}")




