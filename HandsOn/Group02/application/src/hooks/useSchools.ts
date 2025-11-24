import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { School } from "@/types/data";

export const useSchools = () => {
  return useQuery<School[]>({
    queryKey: ["schools"],
    queryFn: () => api.getSchools(),
  });
};
