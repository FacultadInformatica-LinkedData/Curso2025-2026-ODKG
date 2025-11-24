import { createContext, useContext, useState, ReactNode } from "react";

export interface Filters {
  schoolTypes: string[];
  neighborhoods: string[];
  severity: string;
  riskRadius: number;
  mapLayers: {
    schools: boolean;
    accidents: boolean;
    speedCameras: boolean;
    riskZones: boolean;
  };
}

interface FiltersContextType {
  filters: Filters;
  setSchoolTypes: (types: string[]) => void;
  setNeighborhoods: (neighborhoods: string[]) => void;
  setSeverity: (severity: string) => void;
  setRiskRadius: (radius: number) => void;
  toggleMapLayer: (layer: keyof Filters['mapLayers']) => void;
}

const FiltersContext = createContext<FiltersContextType | undefined>(undefined);

export const FiltersProvider = ({ children }: { children: ReactNode }) => {
  const [filters, setFilters] = useState<Filters>({
    schoolTypes: [],
    neighborhoods: [],
    severity: "All",
    riskRadius: 200,
    mapLayers: {
      schools: true,
      accidents: true,
      speedCameras: true,
      riskZones: true,
    },
  });

  const setSchoolTypes = (types: string[]) => {
    setFilters(prev => ({ ...prev, schoolTypes: types }));
  };

  const setNeighborhoods = (neighborhoods: string[]) => {
    setFilters(prev => ({ ...prev, neighborhoods }));
  };

  const setSeverity = (severity: string) => {
    setFilters(prev => ({ ...prev, severity }));
  };

  const setRiskRadius = (radius: number) => {
    setFilters(prev => ({ ...prev, riskRadius: radius }));
  };

  const toggleMapLayer = (layer: keyof Filters['mapLayers']) => {
    setFilters(prev => ({
      ...prev,
      mapLayers: { ...prev.mapLayers, [layer]: !prev.mapLayers[layer] }
    }));
  };

  return (
    <FiltersContext.Provider
      value={{
        filters,
        setSchoolTypes,
        setNeighborhoods,
        setSeverity,
        setRiskRadius,
        toggleMapLayer,
      }}
    >
      {children}
    </FiltersContext.Provider>
  );
};

export const useFilters = () => {
  const context = useContext(FiltersContext);
  if (!context) {
    throw new Error("useFilters must be used within FiltersProvider");
  }
  return context;
};
