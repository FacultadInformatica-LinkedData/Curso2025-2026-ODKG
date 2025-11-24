import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Radar } from "@/types/data";

export const useRadar = () => {
  return useQuery<Radar[]>({
    queryKey: ["radar"],
    queryFn: () => api.getRadars(),
  });
};
