import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { BarChart3 } from "lucide-react";
import { useSchools } from "@/hooks/useSchools";
import type { School } from "@/types/data";
import { useAccidents } from "@/hooks/useAccidents";
import { useRadar } from "@/hooks/useRadar";
import { parseWKT, calculateRiskScore } from "@/lib/geoUtils";
import { matchesSeverityFilter } from "@/lib/severity";
import { useMemo } from "react";
import { useFilters } from "@/contexts/FiltersContext";
import { useSelectedFeature } from "@/contexts/SelectedFeatureContext";

type SchoolWithRisk = {
  school: School;
  accidents: number;
  risk: number;
  radarDistance: number;
};

const SchoolsTable = () => {
  const { filters } = useFilters();
  const { data: schools, isLoading: schoolsLoading } = useSchools();
  const { data: accidents, isLoading: accidentsLoading } = useAccidents({
    radius: filters.riskRadius,
  });
  const { data: radars, isLoading: radarsLoading } = useRadar();
  const { selectedFeature, setSelectedFeature } = useSelectedFeature();

  const schoolsWithRisk = useMemo(() => {
    if (!schools || !accidents || !radars) return [];

    // Filter schools by type and neighborhood
    const filteredSchools = schools.filter(school => {
      // For school types, only filter if specific types are selected (not the default all)
      const typeMatch = filters.schoolTypes.length === 0 || 
        filters.schoolTypes.some(type => {
          const schoolType = school.centro_tipo_descripcion?.toLowerCase() || '';
          return (type === "Public" && schoolType.includes("público")) ||
                 (type === "Private" && schoolType.includes("privado"));
        });
      const neighborhoodMatch = filters.neighborhoods.length === 0 || 
        filters.neighborhoods.includes(school.distrito_nombre);
      return typeMatch && neighborhoodMatch;
    });

    // Filter accidents by severity
    const filteredAccidents = accidents.filter(accident =>
      matchesSeverityFilter(filters.severity, accident.nivel_lesividad)
    );

    return filteredSchools
      .map((school) => {
        const coords = parseWKT(school.wktGeometry);
        if (!coords) return null;

        const { score, nearbyAccidents, nearestRadar } = calculateRiskScore(
          coords,
          filteredAccidents,
          radars,
          filters.riskRadius
        );

        return {
          school,
          accidents: nearbyAccidents,
          risk: score,
          radarDistance: nearestRadar,
        };
      })
      .filter((s): s is SchoolWithRisk => s !== null)
      .sort((a, b) => b.risk - a.risk)
      .slice(0, 10);
  }, [schools, accidents, radars, filters]);

  const handleSelectSchool = (schoolData: SchoolWithRisk) => {
    setSelectedFeature({
      type: "school",
      school: schoolData.school,
      risk: schoolData.risk,
      accidents: schoolData.accidents,
      radarDistance: schoolData.radarDistance,
    });
  };

  if (schoolsLoading || accidentsLoading || radarsLoading) {
    return (
      <div className="bg-card rounded-2xl p-4 md:p-6 animate-stagger-2 shadow-sm">
        <div className="flex items-center gap-2 mb-4 text-card-foreground">
          <BarChart3 className="w-5 h-5" />
          <h2 className="font-semibold text-lg">Most at-risk schools</h2>
        </div>
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  const getRiskBadge = (risk: number) => {
    if (risk >= 80) return { label: "Very High", class: "bg-[hsl(var(--danger))]" };
    if (risk >= 50) return { label: "High", class: "bg-orange-500" };
    if (risk >= 30) return { label: "Medium", class: "bg-yellow-500" };
    return { label: "Low", class: "bg-green-500" };
  };

  return (
    <div className="bg-card rounded-2xl p-4 md:p-6 animate-stagger-2 shadow-sm">
      <div className="flex items-center gap-2 mb-4 text-card-foreground">
        <BarChart3 className="w-5 h-5" />
        <h2 className="font-semibold text-lg">Most at-risk schools</h2>
      </div>
      
      <div className="overflow-x-auto -mx-4 md:mx-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="font-semibold">School</TableHead>
              <TableHead className="font-semibold hidden sm:table-cell">Neighborhood</TableHead>
              <TableHead className="font-semibold hidden md:table-cell">Accidents</TableHead>
              <TableHead className="font-semibold">Risk</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {schoolsWithRisk.map((schoolData) => {
              const riskBadge = getRiskBadge(schoolData.risk);
              const isSelected =
                selectedFeature?.type === "school" &&
                selectedFeature.school.centro_codigo === schoolData.school.centro_codigo;
              return (
                <TableRow
                  key={schoolData.school.centro_codigo}
                  onClick={() => handleSelectSchool(schoolData)}
                  className={`cursor-pointer transition-colors ${isSelected ? "bg-primary/5 hover:bg-primary/5" : "hover:bg-secondary/50"}`}
                  aria-selected={isSelected}
                >
                  <TableCell className="font-medium text-black dark:text-white">
                    {schoolData.school.centro_nombre}
                  </TableCell>
                  <TableCell className="text-muted-foreground hidden sm:table-cell">
                    {schoolData.school.distrito_nombre}
                  </TableCell>
                  <TableCell className="text-muted-foreground hidden md:table-cell">
                    {schoolData.accidents}
                  </TableCell>
                  <TableCell>
                    <Badge className={`${riskBadge.class} text-white rounded-full px-3 whitespace-nowrap`}>
                      {riskBadge.label} · {schoolData.risk}
                    </Badge>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export default SchoolsTable;
