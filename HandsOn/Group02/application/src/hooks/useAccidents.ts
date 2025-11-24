import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Accident } from "@/types/data";

type UseAccidentsOptions = {
  radius?: number;
  originWkt?: string;
};

export const useAccidents = (options: UseAccidentsOptions = {}) => {
  const { radius, originWkt } = options;

  return useQuery<Accident[]>({
    queryKey: ["accidents", radius ?? null, originWkt ?? null],
    queryFn: () => api.getAccidents({ radius, originWkt }),
  });
};
