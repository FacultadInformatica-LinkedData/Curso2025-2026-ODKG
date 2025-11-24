import Header from "@/components/Header";
import FiltersSidebar from "@/components/FiltersSidebar";
import InteractiveMap from "@/components/InteractiveMap";
import SchoolsTable from "@/components/SchoolsTable";
import FeatureProfile from "@/components/FeatureProfile";
import ExportReport from "@/components/ExportReport";
import { FiltersProvider } from "@/contexts/FiltersContext";
import { SelectedFeatureProvider } from "@/contexts/SelectedFeatureContext";

const Index = () => {
  return (
    <FiltersProvider>
      <SelectedFeatureProvider>
        <div className="min-h-screen bg-background flex flex-col">
          <Header />
          <main className="p-4 md:p-6 flex flex-col lg:flex-row gap-4 md:gap-6 max-w-[1920px] mx-auto flex-1 w-full">
            <FiltersSidebar />
            
            <div className="flex-1 space-y-4 md:space-y-6 min-w-0">
              <InteractiveMap />
              
              <div className="grid grid-cols-1 xl:grid-cols-[1.5fr_1fr] gap-4 md:gap-6">
                <SchoolsTable />
                <FeatureProfile />
              </div>
              
              <ExportReport />
            </div>
          </main>
          <footer className="w-full bg-black">
            <div className="max-w-[1920px] mx-auto py-6 px-4 text-center text-sm text-white">
              Made with ❤️ by Pietro, Gabriele and Federico in Madrid
            </div>
          </footer>
        </div>
      </SelectedFeatureProvider>
    </FiltersProvider>
  );
};

export default Index;
