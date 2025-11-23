# -------------------------------------------------------------
# app.R — Charging stations in Vienna
# -------------------------------------------------------------

library(shiny)
library(rdflib)
library(dplyr)
library(leaflet)
library(DT)
library(stringr)
library(htmltools)

# -------------------------
# TTL file path
# -------------------------
rdf_file_path <- "../chargingstations-with-links.ttl"

# -------------------------
# Function to load stations
# -------------------------
load_stations_from_ttl <- function(rdf_path) {
  if (!file.exists(rdf_path)) stop("RDF file not found")
  
  g <- rdf_parse(rdf_path, format = "turtle")
  
  query <- "
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  PREFIX geo: <http://www.opengis.net/ont/geosparql#>
  PREFIX cs: <https://iamabsa.github.io/chargingstation#>

  SELECT ?station ?name ?address ?evseId ?countryCode ?district ?wkt
  WHERE {
    ?station a cs:ChargingStation .
    OPTIONAL { ?station rdfs:label ?name. }
    OPTIONAL { ?station cs:address ?address. }
    OPTIONAL { ?station cs:evseId ?evseId. }
    OPTIONAL { ?station cs:countryCode ?countryCode. }
    OPTIONAL { ?station cs:isInDistrict ?district. }
    OPTIONAL { ?station geo:hasGeometry ?geom . ?geom geo:asWKT ?wkt. }
  }
  "
  
  raw <- rdf_query(g, query)
  
  # Parse WKT POINT -> lat/lon
  parse_wkt_point <- function(wkt) {
    if (is.na(wkt) || wkt == "") return(c(NA_real_, NA_real_))
    # Support POINT, POINT Z, POINT M
    m <- str_match(wkt, "POINT\\s*(Z|M)?\\s*\\(\\s*([+-]?[0-9]+(?:\\.[0-9]+)?)\\s+([+-]?[0-9]+(?:\\.[0-9]+)?)")
    if (is.na(m[1])) return(c(NA_real_, NA_real_))
    lon <- as.numeric(m[3])
    lat <- as.numeric(m[4])
    return(c(lat, lon))
  }
  
  coords <- t(sapply(raw$wkt, parse_wkt_point, USE.NAMES = FALSE))
  coords <- as.data.frame(coords)
  colnames(coords) <- c("lat", "lon")
  
  df <- raw %>%
    mutate(
      station = as.character(station),
      name = ifelse(is.na(name) | name == "", station, name),
      address = ifelse(is.na(address), "", address),
      evseId = ifelse(is.na(evseId), "", evseId),
      countryCode = ifelse(is.na(countryCode), "", countryCode),
      district_uri = ifelse(is.na(district), "", district)
    ) %>%
    bind_cols(coords) %>%
    filter(!is.na(lat) & !is.na(lon)) %>%
    distinct(station, .keep_all = TRUE)
  
  # Extract and decode district names
  df <- df %>%
    mutate(
      district = district_uri,
      district = sub(".*/district/", "", district),
      district = sub("^Vienna-", "", district),
      district = URLdecode(district),
      district = trimws(district)
    ) %>%
    select(station, name, address, district, evseId, countryCode, lat, lon)
  
  return(df)
}

# -------------------------
# Load stations
# -------------------------
stations_df <- load_stations_from_ttl(rdf_file_path)

# -------------------------
# UI
# -------------------------
ui <- fluidPage(
  titlePanel("Vienna EV Charging Stations"),
  sidebarLayout(
    sidebarPanel(
      textInput("search", "Search station or address:", value = ""),
      uiOutput("district_ui"),
      actionButton("reset", "Reset filters"),
      hr(),
      p(paste("Loaded stations:", nrow(stations_df)))
    ),
    mainPanel(
      tabsetPanel(
        tabPanel("Map", leafletOutput("map", height = 650)),
        tabPanel("List", DTOutput("table"))
      )
    )
  )
)

# -------------------------
# SERVER
# -------------------------
server <- function(input, output, session) {
  
  # Populate district dropdown
  output$district_ui <- renderUI({
    districts <- sort(unique(stations_df$district[stations_df$district != ""]))
    selectInput("district", "District:", choices = c("(any)", districts), selected = "(any)")
  })
  
  # Reactive filtered data
  filtered <- reactive({
    df <- stations_df
    
    # Search filter (case-insensitive)
    if (!is.null(input$search) && nzchar(trimws(input$search))) {
      pattern <- tolower(trimws(input$search))
      df <- df %>% filter(
        grepl(pattern, tolower(name), fixed = TRUE) |
          grepl(pattern, tolower(address), fixed = TRUE)
      )
    }
    
    # District filter
    if (!is.null(input$district) && input$district != "(any)") {
      df <- df %>% filter(district == input$district)
    }
    
    df
  })
  
  # Reset filters
  observeEvent(input$reset, {
    updateTextInput(session, "search", value = "")
    updateSelectInput(session, "district", selected = "(any)")
  })
  
  # Leaflet map
  output$map <- renderLeaflet({
    leaflet() %>%
      addTiles() %>%
      setView(lng = 16.3738, lat = 48.2082, zoom = 11)
  })
  
  # Update markers when filtered data changes
  observe({
    df <- filtered()
    proxy <- leafletProxy("map") %>% clearMarkers() %>% clearPopups()
    if (nrow(df) == 0) return()
    
    popups <- paste0("<b>", htmlEscape(df$name), "</b><br/>",
                     htmlEscape(df$address), "<br/>",
                     ifelse(df$district != "", paste0("District: ", htmlEscape(df$district), "<br/>"), ""),
                     "EVSE ID: ", htmlEscape(df$evseId))
    
    proxy %>% addCircleMarkers(
      data = df,
      lng = ~lon,
      lat = ~lat,
      radius = 6,
      weight = 1,
      label = ~name,
      popup = popups,
      layerId = ~station
    )
  })
  
  # Table of stations
  output$table <- renderDT({
    df <- filtered()
    if (nrow(df) == 0) return(datatable(data.frame(Message = "No stations match filters"), options = list(dom = 't')))
    datatable(df %>% select(name, address, district, evseId, countryCode, lat, lon),
              options = list(pageLength = 10), rownames = FALSE)
  })
  
  # Zoom map when selecting table row
  observeEvent(input$table_rows_selected, {
    sel <- input$table_rows_selected
    if (is.null(sel) || length(sel) == 0) return()
    df <- filtered()
    row <- df[sel, ]
    leafletProxy("map") %>%
      setView(lng = row$lon, lat = row$lat, zoom = 15) %>%
      clearPopups() %>%
      addPopups(lng = row$lon, lat = row$lat, popup = paste0("<b>", row$name, "</b><br/>", row$address))
  })
}

# -------------------------
# Run App
# -------------------------
shinyApp(ui, server)

