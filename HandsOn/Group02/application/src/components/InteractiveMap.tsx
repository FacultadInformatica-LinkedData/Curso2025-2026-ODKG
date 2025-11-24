import { Badge } from "@/components/ui/badge";
import "leaflet/dist/leaflet.css";
import { useEffect, useMemo, useRef } from "react";
import L from "leaflet";
import { useSchools } from "@/hooks/useSchools";
import { useAccidents } from "@/hooks/useAccidents";
import { useRadar } from "@/hooks/useRadar";
import { parseWKT, calculateRiskScore } from "@/lib/geoUtils";
import { getSeverityColor, matchesSeverityFilter } from "@/lib/severity";
import { useFilters } from "@/contexts/FiltersContext";
import { useSelectedFeature } from "@/contexts/SelectedFeatureContext";

// Fix per l'icona del marker di default di Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const InteractiveMap = () => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);
  const schoolsLayerRef = useRef<L.LayerGroup | null>(null);
  const accidentsLayerRef = useRef<L.LayerGroup | null>(null);
  const radarsLayerRef = useRef<L.LayerGroup | null>(null);
  const riskZonesLayerRef = useRef<L.LayerGroup | null>(null);
  const { filters } = useFilters();
  const { data: schools } = useSchools();
  const { data: accidents } = useAccidents({ radius: filters.riskRadius });
  const { data: radars } = useRadar();
  const { selectedFeature, setSelectedFeature } = useSelectedFeature();

  const filteredSchools = useMemo(() => {
    if (!schools) return [];
    return schools.filter((school) => {
      const schoolType = school.centro_tipo_descripcion?.toLowerCase() || "";
      const typeMatch =
        filters.schoolTypes.length === 0 ||
        filters.schoolTypes.some((type) => {
          if (type === "Public") {
            return schoolType.includes("público");
          }
          if (type === "Private") {
            return schoolType.includes("privado");
          }
          return true;
        });
      const neighborhoodMatch =
        filters.neighborhoods.length === 0 ||
        filters.neighborhoods.includes(school.distrito_nombre);
      return typeMatch && neighborhoodMatch;
    });
  }, [schools, filters.schoolTypes, filters.neighborhoods]);

  const filteredAccidents = useMemo(() => {
    if (!accidents) return [];
    return accidents.filter((accident) => {
      const severityMatches = matchesSeverityFilter(filters.severity, accident.nivel_lesividad);
      const neighborhoodMatch =
        filters.neighborhoods.length === 0 ||
        filters.neighborhoods.includes(accident.distrito);
      return severityMatches && neighborhoodMatch;
    });
  }, [accidents, filters.severity, filters.neighborhoods]);

  // Initialize map once
  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;

    const madridCenter: [number, number] = [40.4168, -3.7038];
    const map = L.map(mapRef.current).setView(madridCenter, 13);
    mapInstance.current = map;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    schoolsLayerRef.current = L.layerGroup().addTo(map);
    accidentsLayerRef.current = L.layerGroup().addTo(map);
    radarsLayerRef.current = L.layerGroup().addTo(map);
    riskZonesLayerRef.current = L.layerGroup().addTo(map);

    return () => {
      map.remove();
      mapInstance.current = null;
      schoolsLayerRef.current = null;
      accidentsLayerRef.current = null;
      radarsLayerRef.current = null;
      riskZonesLayerRef.current = null;
    };
  }, []);

  // Sync overlays when data or filters change
  useEffect(() => {
    if (
      !mapInstance.current ||
      !schoolsLayerRef.current ||
      !accidentsLayerRef.current ||
      !radarsLayerRef.current ||
      !riskZonesLayerRef.current ||
      !radars
    ) {
      return;
    }

    if (selectedFeature) {
      const isFeatureStillAvailable = () => {
        if (selectedFeature.type === "school") {
          return filteredSchools.some(
            (school) => school.centro_codigo === selectedFeature.school.centro_codigo
          );
        }

        if (selectedFeature.type === "accident") {
          return filteredAccidents.some(
            (accident) =>
              accident.num_expediente === selectedFeature.accident.num_expediente
          );
        }

        if (selectedFeature.type === "radar") {
          return radars.some(
            (radar) => radar.numero_radar === selectedFeature.radar.numero_radar
          );
        }

        return false;
      };

      if (!isFeatureStillAvailable()) {
        setSelectedFeature(null);
      }
    }

    schoolsLayerRef.current.clearLayers();
    accidentsLayerRef.current.clearLayers();
    radarsLayerRef.current.clearLayers();
    riskZonesLayerRef.current.clearLayers();

    filteredSchools.forEach((school) => {
      const coords = parseWKT(school.wktGeometry);
      if (!coords) return;

      const { score, nearbyAccidents, nearestRadar } = calculateRiskScore(
        coords,
        filteredAccidents,
        radars,
        filters.riskRadius
      );

      if (filters.mapLayers.schools) {
        const marker = L.marker(coords);
        marker.on("click", () =>
          setSelectedFeature({
            type: "school",
            school,
            risk: score,
            accidents: nearbyAccidents,
            radarDistance: nearestRadar,
          })
        );
        marker.bindPopup(`
          <div style="font-size: 14px;">
            <h3 style="font-weight: 600; margin-bottom: 4px;">${school.centro_nombre}</h3>
            <p style="font-size: 12px; color: #6b7280; margin: 0;">Risk: ${score}</p>
            <p style="font-size: 12px; color: #6b7280; margin: 0;">Accidents: ${nearbyAccidents}</p>
          </div>
        `);
        marker.addTo(schoolsLayerRef.current);
      }

      if (filters.mapLayers.riskZones) {
        const color =
          score > 80 ? "#ef4444" : score > 50 ? "#f59e0b" : "#22c55e";
        L.circle(coords, {
          color,
          fillColor: color,
          fillOpacity: 0.1,
          weight: 2,
          radius: filters.riskRadius,
        }).addTo(riskZonesLayerRef.current);
      }
    });

    if (filters.mapLayers.accidents) {
      filteredAccidents.forEach((accident) => {
        const coords = parseWKT(accident.wktGeometry);
        if (!coords) return;

        const color = getSeverityColor(accident.nivel_lesividad);
        const marker = L.circleMarker(coords, {
          radius: 6,
          color,
          fillColor: color,
          fillOpacity: 0.8,
          weight: 1,
        });

        marker.on("click", () =>
          setSelectedFeature({
            type: "accident",
            accident,
          })
        );

        marker.bindPopup(`
          <div style="font-size: 13px;">
            <h3 style="font-weight: 600; margin-bottom: 4px;">${accident.lesividad}</h3>
            <p style="font-size: 12px; color: #6b7280; margin: 0;">District: ${accident.distrito}</p>
            <p style="font-size: 12px; color: #6b7280; margin: 0;">Date: ${accident.fecha} ${accident.hora}</p>
            <p style="font-size: 12px; color: #6b7280; margin: 0;">Location: ${accident.localizacion}</p>
          </div>
        `);

        marker.addTo(accidentsLayerRef.current);
      });
    }

    if (filters.mapLayers.speedCameras) {
      radars.forEach((radar) => {
        const coords = parseWKT(radar.wktGeometry);
        if (!coords) return;

        const marker = L.circleMarker(coords, {
          radius: 7,
          color: "#2563eb",
          fillColor: "#60a5fa",
          fillOpacity: 0.9,
          weight: 2,
        });

        marker.on("click", () =>
          setSelectedFeature({
            type: "radar",
            radar,
          })
        );

        marker.bindPopup(`
          <div style="font-size: 13px;">
            <h3 style="font-weight: 600; margin-bottom: 4px;">Radar ${radar.numero_radar}</h3>
            <p style="font-size: 12px; color: #6b7280; margin: 0;">Limit: ${radar.velocidad_limite} km/h</p>
            <p style="font-size: 12px; color: #6b7280; margin: 0;">Type: ${radar.tipo}</p>
            <p style="font-size: 12px; color: #6b7280; margin: 0;">${radar.ubicacion}</p>
          </div>
        `);

        marker.addTo(radarsLayerRef.current);
      });
    }
  }, [
    filteredSchools,
    filteredAccidents,
    radars,
    filters.mapLayers,
    filters.riskRadius,
    selectedFeature,
    setSelectedFeature,
  ]);

  return (
    <div className="bg-card rounded-2xl p-4 md:p-6 animate-stagger-1 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <h2 className="font-semibold text-lg text-card-foreground">Interactive Map</h2>
      </div>
      
      <div 
        ref={mapRef}
        className="rounded-xl overflow-hidden h-[480px] md:h-[600px] border-2 border-border shadow-inner"
        style={{ zIndex: 0 }}
      />
    </div>
  );
};

export default InteractiveMap;
