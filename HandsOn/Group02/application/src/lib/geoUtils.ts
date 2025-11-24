// Parse WKT (Well-Known Text) geometry to [lat, lng]
export const parseWKT = (wkt: string): [number, number] | null => {
  if (!wkt) return null;
  
  const match = wkt.match(/POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)/i);
  if (match) {
    const lng = parseFloat(match[1]);
    const lat = parseFloat(match[2]);
    return [lat, lng];
  }
  return null;
};

// Calculate distance between two points in meters using Haversine formula
export const calculateDistance = (
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number => {
  const R = 6371e3; // Earth's radius in meters
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
};

// Calculate risk score for a school based on nearby accidents and radars
export const calculateRiskScore = (
  schoolCoords: [number, number],
  accidents: Array<{ wktGeometry: string; nivel_lesividad: number }>,
  radars: Array<{ wktGeometry: string }>,
  radius: number = 500
): { score: number; nearbyAccidents: number; nearestRadar: number } => {
  let nearbyAccidents = 0;
  let totalSeverity = 0;
  let nearestRadar = Infinity;

  // Count accidents within radius and sum severity
  accidents.forEach((accident) => {
    const accidentCoords = parseWKT(accident.wktGeometry);
    if (accidentCoords) {
      const distance = calculateDistance(
        schoolCoords[0],
        schoolCoords[1],
        accidentCoords[0],
        accidentCoords[1]
      );
      if (distance <= radius) {
        nearbyAccidents++;
        totalSeverity += accident.nivel_lesividad || 1;
      }
    }
  });

  // Find nearest radar
  radars.forEach((radar) => {
    const radarCoords = parseWKT(radar.wktGeometry);
    if (radarCoords) {
      const distance = calculateDistance(
        schoolCoords[0],
        schoolCoords[1],
        radarCoords[0],
        radarCoords[1]
      );
      nearestRadar = Math.min(nearestRadar, distance);
    }
  });

  // Calculate risk score
  // Higher accidents and severity increase risk
  const accidentWeight = nearbyAccidents * 5;
  const severityWeight = totalSeverity * 2;

  const score = Math.round(accidentWeight + severityWeight);

  return {
    score,
    nearbyAccidents,
    nearestRadar: nearestRadar === Infinity ? 0 : Math.round(nearestRadar),
  };
};
