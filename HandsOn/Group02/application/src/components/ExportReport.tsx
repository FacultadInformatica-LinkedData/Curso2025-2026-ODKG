import { FileDown, FileText, File, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

const ExportReport = () => {
  return (
    <div className="bg-card rounded-2xl p-4 md:p-6 animate-stagger-3 shadow-sm">
      <div className="flex items-center gap-2 mb-2 text-card-foreground">
        <FileDown className="w-5 h-5" />
        <h2 className="font-semibold text-lg">Exportable report</h2>
      </div>
      
      <p className="text-sm text-muted-foreground mb-4">
        Generate PDF or CSV with risk data for selected schools.
      </p>
      
      <div className="flex flex-wrap items-center gap-3">
        <Button variant="outline" className="gap-2 hover:scale-105 transition-transform">
          <FileText className="w-4 h-4" />
          CSV
        </Button>
        <Button variant="default" className="gap-2 bg-primary hover:scale-105 transition-transform">
          <File className="w-4 h-4" />
          PDF
        </Button>
        <Button variant="ghost" className="gap-2 text-muted-foreground hover:scale-105 transition-transform">
          <span className="hidden sm:inline">Advanced (RDF/SPARQL)</span>
          <span className="sm:hidden">Advanced</span>
          <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};

export default ExportReport;
