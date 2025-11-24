import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useFilters } from "@/contexts/FiltersContext";
import { useSelectedFeature } from "@/contexts/SelectedFeatureContext";
import { getSeverityBadgeConfig } from "@/lib/severity";
import type { ReactNode } from "react";

const getRiskBadge = (risk: number) => {
  if (risk >= 80) return { label: "Very High", class: "bg-[hsl(var(--danger))]" };
  if (risk >= 50) return { label: "High", class: "bg-orange-500" };
  if (risk >= 30) return { label: "Medium", class: "bg-yellow-500" };
  return { label: "Low", class: "bg-green-500" };
};

const renderValue = (value?: ReactNode) => {
  if (value === null || value === undefined) {
    return <span className="text-muted-foreground">N/D</span>;
  }

  if (typeof value === "string" && value.trim() === "") {
    return <span className="text-muted-foreground">N/D</span>;
  }

  return value;
};

const InfoBlock = ({ label, value }: { label: string; value?: ReactNode }) => (
  <div className="rounded-xl border border-border/60 bg-muted/20 p-3">
    <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
    <p className="text-sm font-semibold text-card-foreground mt-1 break-words">
      {renderValue(value)}
    </p>
  </div>
);

const formatPhoneNumber = (phone?: number | null) => {
  if (!phone) return null;
  const phoneString = phone.toString();
  if (phoneString.length === 9) {
    return `${phoneString.slice(0, 3)} ${phoneString.slice(3, 6)} ${phoneString.slice(6)}`;
  }
  return phoneString;
};

const normalizeWebsite = (url?: string | null) => {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  return `https://${url}`;
};

const FeatureProfile = () => {
  const { selectedFeature } = useSelectedFeature();
  const { filters } = useFilters();
  const riskRadius = filters.riskRadius;

  if (!selectedFeature) {
    return (
      <div className="bg-card rounded-2xl p-4 md:p-6 animate-stagger-2 shadow-sm flex flex-col gap-2">
        <h2 className="text-sm font-medium text-muted-foreground">Element details</h2>
        <p className="text-sm text-muted-foreground leading-relaxed">
        No items selected. Click on a school, accident, or speed camera on the map to view details here.
        </p>
      </div>
    );
  }

  if (selectedFeature.type === "school") {
    const { school, risk, accidents } = selectedFeature;
    const riskBadge = getRiskBadge(risk);
    const website = normalizeWebsite(school.contacto_web);
    const contactPhone = formatPhoneNumber(school.contacto_telefono1);
    const schoolName = school.centro_nombre?.trim() || "Unnamed educational center";
    const addressLine = school.direccion?.trim() || "Address not available";
    const postalSuffix = school.direccion_codigo_postal ? ` · ${school.direccion_codigo_postal}` : "";

    return (
      <div className="bg-card rounded-2xl p-4 md:p-6 animate-stagger-2 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="secondary" className="uppercase tracking-wide text-[11px]">
                School profile
              </Badge>
              {school.centro_titularidad && (
                <Badge variant="secondary" className="uppercase tracking-wide text-[11px]">
                  {school.centro_titularidad}
                </Badge>
              )}
              {school.centro_tipo_descripcion && (
                <Badge variant="secondary" className="uppercase tracking-wide text-[11px]">
                  {school.centro_tipo_descripcion}
                </Badge>
              )}
            </div>
            <div>
              <h3 className="text-xl font-bold text-card-foreground">
                {schoolName}
              </h3>
              <p className="text-sm text-muted-foreground mt-1">
                {addressLine}
                {postalSuffix}
              </p>
            </div>
          </div>
          <Badge className={`${riskBadge.class} text-white shrink-0`}>
            {riskBadge.label} · {risk}
          </Badge>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Card className="p-3 md:p-4 border-2 hover:border-primary/50 transition-colors">
            <div className="text-xs text-muted-foreground mb-1">Accidents nearby</div>
            <div className="text-2xl font-bold text-card-foreground">{accidents}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Historical incidents within {riskRadius} m
            </p>
          </Card>
          <Card className="p-3 md:p-4 border-2 hover:border-primary/50 transition-colors">
            <div className="text-xs text-muted-foreground mb-1">Risk score</div>
            <div className="text-2xl font-bold text-card-foreground">{risk}</div>
            <p className="text-xs text-muted-foreground mt-1">composite exposure score</p>
          </Card>
        </div>

        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="w-full grid grid-cols-3">
            <TabsTrigger value="overview" className="text-xs md:text-sm">Overview</TabsTrigger>
            <TabsTrigger value="safety" className="text-xs md:text-sm">Safety</TabsTrigger>
            <TabsTrigger value="contacts" className="text-xs md:text-sm">Contacts</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-4 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <InfoBlock label="School type" value={school.centro_tipo_descripcion} />
              <InfoBlock label="Ownership" value={school.centro_titularidad} />
              <InfoBlock label="Center code" value={school.centro_codigo} />
              <InfoBlock label="Type code" value={school.centro_tipo_codigo} />
              <InfoBlock label="District" value={school.distrito_nombre} />
              <InfoBlock label="District code" value={school.distrito_codigo} />
            </div>
          </TabsContent>

          <TabsContent value="safety" className="mt-4 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <InfoBlock
                label="Recorded accidents"
                value={`${accidents} incidents within ${riskRadius} m`}
              />
              <InfoBlock label="Speed controls" value="Presence detected in this district" />
            </div>
            <div className="rounded-2xl border border-dashed border-primary/40 bg-primary/5 p-4">
              <p className="text-sm text-muted-foreground leading-relaxed">
              The risk score is derived from accident density and severity.
              </p>
            </div>
          </TabsContent>

          <TabsContent value="contacts" className="mt-4 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <InfoBlock label="Primary phone" value={contactPhone} />
              <InfoBlock
                label="Email"
                value={
                  school.contacto_email1 ? (
                    <a
                      className="text-primary hover:underline break-words"
                      href={`mailto:${school.contacto_email1}`}
                    >
                      {school.contacto_email1}
                    </a>
                  ) : undefined
                }
              />
              <InfoBlock
                label="Website"
                value={
                  website ? (
                    <a
                      className="text-primary hover:underline break-words"
                      href={website}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {school.contacto_web}
                    </a>
                  ) : undefined
                }
              />
              <InfoBlock label="Address" value={addressLine} />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    );
  }

  if (selectedFeature.type === "accident") {
    const { accident } = selectedFeature;
    const severityBadge = getSeverityBadgeConfig(accident.nivel_lesividad);
    const incidentName = accident.lesividad?.trim() || "Incidente registrato";
    const incidentDate = accident.fecha || "Data non disponibile";
    const incidentTime = accident.hora || "--:--";

    const involvementBadges = [
      { label: "Pedestrian involved", active: Boolean(accident.peaton_involucrado) },
      { label: "Alcohol positive", active: Boolean(accident.positiva_alcohol) },
      { label: "Drug positive", active: Boolean(accident.positiva_droga) },
    ];

    return (
      <div className="bg-card rounded-2xl p-4 md:p-6 animate-stagger-2 shadow-sm space-y-5">
        <div className="flex flex-col gap-3">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Injury level</p>
              <h3 className="text-xl font-bold text-card-foreground">{incidentName}</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {incidentDate} · {incidentTime}
              </p>
            </div>
            <Badge className={`${severityBadge.class} text-white`}>
              {severityBadge.label}
            </Badge>
          </div>
          <div className="flex flex-wrap gap-2">
            {involvementBadges.map(({ label, active }) => (
              <Badge
                key={label}
                variant={active ? "default" : "secondary"}
                className={
                  active
                    ? "bg-emerald-500/20 text-emerald-600 dark:text-emerald-200"
                    : "bg-muted text-muted-foreground"
                }
              >
                {label}
              </Badge>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <InfoBlock label="Case ID" value={accident.num_expediente} />
          <InfoBlock label="District" value={accident.distrito} />
          <InfoBlock label="District code" value={accident.cod_distrito} />
          <InfoBlock label="Accident type" value={accident.tipo_accidente} />
          <InfoBlock label="Vehicles involved" value={accident.vehiculos_involucrados} />
          <InfoBlock label="Weather conditions" value={accident.estado_meteorológico} />
        </div>

        <div className="rounded-2xl border border-border/80 bg-muted/30 p-4">
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">
            Location
          </p>
          <p className="text-sm font-semibold text-card-foreground">{accident.localizacion}</p>
          <p className="text-xs text-muted-foreground mt-1">
            Coordinate reference stored as WKT for precise GIS overlays.
          </p>
        </div>
      </div>
    );
  }

  if (selectedFeature.type === "radar") {
    const { radar } = selectedFeature;

    return (
      <div className="bg-card rounded-2xl p-4 md:p-6 animate-stagger-2 shadow-sm space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-sm font-medium text-muted-foreground mb-1">Speed camera</h2>
            <h3 className="text-xl font-bold text-card-foreground">Radar {radar.numero_radar}</h3>
            <p className="text-sm text-muted-foreground mt-1">{radar.ubicacion}</p>
          </div>
          <Badge className="bg-blue-600 text-white">Fixed radar</Badge>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between py-2 border-b border-border">
            <span className="text-sm text-muted-foreground">Speed limit</span>
            <span className="text-sm font-medium text-card-foreground">
              {radar.velocidad_limite} km/h
            </span>
          </div>
          <div className="flex justify-between py-2 border-b border-border">
            <span className="text-sm text-muted-foreground">Type</span>
            <span className="text-sm font-medium text-card-foreground">{radar.tipo}</span>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default FeatureProfile;
