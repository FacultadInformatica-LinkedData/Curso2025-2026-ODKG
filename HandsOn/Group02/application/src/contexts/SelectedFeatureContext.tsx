import { createContext, useContext, useState, type ReactNode } from "react";
import type { School, Accident, Radar } from "@/types/data";

export type SelectedFeature =
  | {
      type: "school";
      school: School;
      risk: number;
      accidents: number;
      radarDistance: number;
    }
  | {
      type: "accident";
      accident: Accident;
    }
  | {
    type: "radar";
    radar: Radar;
  };

interface SelectedFeatureContextValue {
  selectedFeature: SelectedFeature | null;
  setSelectedFeature: (feature: SelectedFeature | null) => void;
}

const SelectedFeatureContext = createContext<SelectedFeatureContextValue | undefined>(
  undefined
);

export const SelectedFeatureProvider = ({ children }: { children: ReactNode }) => {
  const [selectedFeature, setSelectedFeature] = useState<SelectedFeature | null>(null);

  return (
    <SelectedFeatureContext.Provider value={{ selectedFeature, setSelectedFeature }}>
      {children}
    </SelectedFeatureContext.Provider>
  );
};

export const useSelectedFeature = () => {
  const context = useContext(SelectedFeatureContext);
  if (!context) {
    throw new Error("useSelectedFeature must be used within SelectedFeatureProvider");
  }
  return context;
};


