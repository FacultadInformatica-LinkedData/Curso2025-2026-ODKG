import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useSelectedFeature } from "@/contexts/SelectedFeatureContext";
import { getSeverityBadgeConfig } from "@/lib/severity";

const getRiskBadge = (risk: number) => {
  if (risk >= 80) return { label: "Very High", class: "bg-[hsl(var(--danger))]" };
  if (risk >= 50) return { label: "High", class: "bg-orange-500" };
  if (risk >= 30) return { label: "Medium", class: "bg-yellow-500" };
  return { label: "Low", class: "bg-green-500" };
};

const SchoolProfile = () => {
  const { selectedFeature } = useSelectedFeature();

  if (!selectedFeature) {
    return (
      <div className="bg-card rounded-2xl p-4 md:p-6 animate-stagger-2 shadow-sm flex flex-col gap-2">
        <h2 className="text-sm font-medium text-muted-foreground">Dettagli elemento</h2>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Nessun elemento selezionato. Clicca su una scuola, un incidente o un radar sulla mappa
          per visualizzare i dettagli qui.
        </p>
      </div>
    );
  }

  if (selectedFeature.type === "school") {
    const { school, risk, accidents, radarDistance } = selectedFeature;
    const riskBadge = getRiskBadge(risk);

    return (
      <div className="bg-card rounded-2xl p-4 md:p-6 animate-stagger-2 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-6">
          <div>
            <h2 className="text-sm font-medium text-muted-foreground mb-1">School profile</h2>
            <h3 className="text-xl font-bold text-card-foreground">{school.centro_nombre}</h3>
            <p className="text-sm text-muted-foreground mt-1">{school.direccion}</p>
          </div>
          <Badge className={`${riskBadge.class} text-white shrink-0`}>
            {riskBadge.label} · {risk}
          </Badge>
        </div>
        
        <div className="grid grid-cols-3 gap-3 mb-6">
          <Card className="p-3 md:p-4 border-2 hover:border-primary/50 transition-colors">
            <div className="text-xs text-muted-foreground mb-1">Accidents</div>
            <div className="text-xl md:text-2xl font-bold text-card-foreground">{accidents}</div>
          </Card>
          <Card className="p-3 md:p-4 border-2 hover:border-primary/50 transition-colors">
            <div className="text-xs text-muted-foreground mb-1">Radar</div>
            <div className="text-xl md:text-2xl font-bold text-card-foreground">{radarDistance} m</div>
          </Card>
          <Card className="p-3 md:p-4 border-2 hover:border-primary/50 transition-colors">
            <div className="text-xs text-muted-foreground mb-1">Risk</div>
            <div className="text-xl md:text-2xl font-bold text-card-foreground">{risk}</div>
          </Card>
        </div>
        
        <Tabs defaultValue="details" className="w-full">
          <TabsList className="w-full grid grid-cols-3">
            <TabsTrigger value="details" className="text-xs md:text-sm">Details</TabsTrigger>
            <TabsTrigger value="accidents" className="text-xs md:text-sm">Accidents</TabsTrigger>
            <TabsTrigger value="notes" className="text-xs md:text-sm">Notes</TabsTrigger>
          </TabsList>
          <TabsContent value="details" className="mt-4 space-y-3">
            <div className="flex justify-between py-2 border-b border-border">
              <span className="text-sm text-muted-foreground">School type</span>
              <span className="text-sm font-medium text-card-foreground">
                {school.centro_tipo_descripcion || "N/A"}
              </span>
            </div>
            <div className="flex justify-between py-2 border-b border-border">
              <span className="text-sm text-muted-foreground">Neighborhood</span>
              <span className="text-sm font-medium text-card-foreground">
                {school.distrito_nombre}
              </span>
            </div>
          </TabsContent>
          <TabsContent value="accidents" className="mt-4">
            <p className="text-sm text-muted-foreground">
              Accidents within the selected radius: {accidents}
            </p>
          </TabsContent>
          <TabsContent value="notes" className="mt-4">
            <p className="text-sm text-muted-foreground">
              Notes section
            </p>
          </TabsContent>
        </Tabs>
      </div>
    );
  }

  if (selectedFeature.type === "accident") {
    const { accident } = selectedFeature;
    const severityBadge = getSeverityBadgeConfig(accident.nivel_lesividad);

    return (
      <div className="bg-card rounded-2xl p-4 md:p-6 animate-stagger-2 shadow-sm space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-sm font-medium text-muted-foreground mb-1">Injury level</h2>
            <h3 className="text-xl font-bold text-card-foreground">{accident.lesividad}</h3>
            <p className="text-sm text-muted-foreground mt-1">
              {accident.fecha} · {accident.hora}
            </p>
          </div>
          <Badge className={`${severityBadge.class} text-white`}>
            {severityBadge.label}
          </Badge>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between py-2 border-b border-border">
            <span className="text-sm text-muted-foreground">District</span>
            <span className="text-sm font-medium text-card-foreground">{accident.distrito}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-border">
            <span className="text-sm text-muted-foreground">Location</span>
            <span className="text-sm font-medium text-card-foreground">{accident.localizacion}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-border">
            <span className="text-sm text-muted-foreground">Case ID</span>
            <span className="text-sm font-medium text-card-foreground">{accident.num_expediente}</span>
          </div>
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

export default SchoolProfile;
