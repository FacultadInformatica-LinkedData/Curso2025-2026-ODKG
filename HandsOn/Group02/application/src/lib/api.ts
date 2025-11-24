const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API request failed with ${response.status}: ${errorText}`);
  }

  return response.json() as Promise<T>;
}

type AccidentsParams = {
  radius?: number;
  originWkt?: string;
};

export const api = {
  getSchools: () => request("/schools"),
  getAccidents: ({ radius, originWkt }: AccidentsParams = {}) => {
    const params = new URLSearchParams();
    if (typeof radius === "number" && Number.isFinite(radius)) {
      params.set("radius", radius.toString());
    }
    if (originWkt) {
      params.set("origin", originWkt);
    }
    const queryString = params.toString();
    return request(`/accidents${queryString ? `?${queryString}` : ""}`);
  },
  getRadars: () => request("/radar"),
};
