import { Search, Shield, Globe } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

const Header = () => {
  return (
    <header className="bg-primary text-primary-foreground px-4 md:px-6 py-4 flex items-center justify-between border-b border-border/20 sticky top-0 z-50 backdrop-blur-sm">
      <div className="flex items-center gap-2 md:gap-3">
        <Shield className="w-5 h-5 flex-shrink-0" />
        <h1 className="text-base md:text-lg font-semibold whitespace-nowrap">Safe School</h1>
        <Badge variant="secondary" className="bg-card text-card-foreground hidden sm:inline-flex">
          Madrid
        </Badge>
      </div>
    </header>
  );
};

export default Header;
