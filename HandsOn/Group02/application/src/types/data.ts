export interface School {
  centro_codigo: number;
  centro_nombre: string;
  direccion: string;
  direccion_codigo_postal?: number | null;
  distrito_nombre: string;
  distrito_codigo: number | null;
  centro_tipo_descripcion: string;
  centro_tipo_codigo?: number | null;
  centro_titularidad?: string | null;
  contacto_email1?: string | null;
  contacto_telefono1?: number | null;
  contacto_web?: string | null;
  wktGeometry: string;
}

export interface Accident {
  num_expediente: string;
  wktGeometry: string;
  lesividad: string;
  nivel_lesividad: number;
  distrito: string;
  fecha: string;
  hora: string;
  localizacion: string;
  cod_distrito?: number | null;
  estado_meteorológico?: string | null;
  peaton_involucrado?: boolean | null;
  positiva_alcohol?: boolean | null;
  positiva_droga?: boolean | null;
  tipo_accidente?: string | null;
  vehiculos_involucrados?: string | null;
}

export interface Radar {
  numero_radar: number;
  ubicacion: string;
  wktGeometry: string;
  velocidad_limite: number;
  tipo: string;
}
