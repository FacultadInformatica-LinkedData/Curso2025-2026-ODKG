import { SlidersHorizontal, MapPin, AlertTriangle, Camera, AlertCircle } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { useFilters } from "@/contexts/FiltersContext";

const SCHOOL_TYPES = ["Public", "Private"];
const NEIGHBORHOODS = ["Centro", "Salamanca", "Chamartín", "Arganzuela", "Carabanchel", "Latina"];

const FiltersSidebar = () => {
  const { filters, setSchoolTypes, setNeighborhoods, setSeverity, setRiskRadius, toggleMapLayer } = useFilters();
  const allSchoolTypesSelected = filters.schoolTypes.length === 0;
  const allNeighborhoodsSelected = filters.neighborhoods.length === 0;
  const toggleSchoolType = (type: string) => {
    if (filters.schoolTypes.includes(type)) {
      setSchoolTypes(filters.schoolTypes.filter(t => t !== type));
    } else {
      setSchoolTypes([...filters.schoolTypes, type]);
    }
  };

  const toggleNeighborhood = (neighborhood: string) => {
    if (filters.neighborhoods.includes(neighborhood)) {
      setNeighborhoods(filters.neighborhoods.filter(n => n !== neighborhood));
    } else {
      setNeighborhoods([...filters.neighborhoods, neighborhood]);
    }
  };
  const FilterButton = ({
    label,
    active,
    onClick
  }: {
    label: string;
    active: boolean;
    onClick: () => void;
  }) => <button onClick={onClick} className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${active ? "bg-[hsl(var(--filter-active))] text-primary-foreground" : "bg-[hsl(var(--filter-inactive))] text-card-foreground hover:bg-secondary"}`}>
      {label}
    </button>;
  return <aside className="w-full lg:w-[280px] bg-card rounded-2xl p-4 md:p-6 space-y-6 animate-fade-in shadow-sm">
      <div className="flex items-center gap-2 text-card-foreground pb-2 border-b border-border">
        <SlidersHorizontal className="w-5 h-5" />
        <h2 className="font-semibold text-lg">Filters</h2>
      </div>
      
      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-semibold mb-3 text-card-foreground">School type</h3>
          <div className="flex flex-wrap gap-2">
            <FilterButton label="All" active={allSchoolTypesSelected} onClick={() => setSchoolTypes([])} />
            {SCHOOL_TYPES.map(type => (
              <FilterButton key={type} label={type} active={filters.schoolTypes.includes(type)} onClick={() => toggleSchoolType(type)} />
            ))}
          </div>
        </div>
        
        <div>
          <h3 className="text-sm font-semibold mb-3 text-card-foreground">Neighborhood</h3>
          <div className="flex flex-wrap gap-2">
            <FilterButton label="All" active={allNeighborhoodsSelected} onClick={() => setNeighborhoods([])} />
            {NEIGHBORHOODS.map(n => (
              <FilterButton key={n} label={n} active={filters.neighborhoods.includes(n)} onClick={() => toggleNeighborhood(n)} />
            ))}
          </div>
        </div>
        
        <div>
          <h3 className="text-sm font-semibold mb-3 text-card-foreground">Accident severity</h3>
          <div className="flex flex-wrap gap-2">
            {["All", "Low", "Medium", "High"].map(s => <FilterButton key={s} label={s} active={filters.severity === s} onClick={() => setSeverity(s)} />)}
          </div>
        </div>
        
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-card-foreground">Risk radius</h3>
            <span className="text-sm font-medium text-primary">{filters.riskRadius} m</span>
          </div>
          <Slider value={[filters.riskRadius]} onValueChange={(val) => setRiskRadius(val[0])} max={500} min={50} step={10} className="mb-1" />
        </div>
        
        <div className="space-y-3 pt-4 border-t border-border">
          <h3 className="text-sm font-semibold text-card-foreground mb-3">Map layers</h3>
          {[
            { icon: MapPin, label: "Schools", key: "schools" as const },
            { icon: AlertTriangle, label: "Accidents", key: "accidents" as const },
            { icon: Camera, label: "Speed cameras", key: "speedCameras" as const },
            { icon: AlertCircle, label: "Risk zones", key: "riskZones" as const }
          ].map(({ icon: Icon, label, key }) => (
            <div key={label} className="flex items-center justify-between group hover:bg-secondary/50 -mx-2 px-2 py-1.5 rounded-lg transition-colors">
              <div className="flex items-center gap-2 text-card-foreground">
                <Icon className="w-4 h-4" />
                <span className="text-sm">{label}</span>
              </div>
              <Switch checked={filters.mapLayers[key]} onCheckedChange={() => toggleMapLayer(key)} />
            </div>
          ))}
        </div>
      </div>
    </aside>;
};
export default FiltersSidebar;