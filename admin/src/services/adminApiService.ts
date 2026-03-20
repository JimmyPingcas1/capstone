const API_BASE_URL = 'http://localhost:5000';

export interface DashboardReading {
  time: string;
  temp: number;
  ph: number;
  ammonia: number;
  turbidity: number;
  do: number;
}

export interface DashboardResponse {
  totalPonds: number;
  totalUsers: number;
  activePondToday: number;
  recentReadings: DashboardReading[];
}

export interface AdminUser {
  id: string;
  name: string;
  email: string;
  pondId: string;
  status: string;
}

export interface AdminPond {
  id: string;
  pond_id: string;
  name: string;
  location: string;
  user_id: string;
  user_name?: string;
  devices: number;
  status: string;
}

export interface DataRecord {
  id: string | number;
  date: string;
  time: string;
  pondId: string;
  pondName: string;
  temperature: number;
  ph: number;
  ammonia: number;
  turbidity: number;
  do?: number;
  predicted_dissolved_oxygen?: number;
  validation_warnings?: string[];
  prediction?: string;
  aeratorOn?: boolean | null;
  waterPumpOn?: boolean | null;
  heaterOn?: boolean | null;
  detectedIssues?: string[] | null;
  final_devices?: {
    heater: boolean;
    water_pump: boolean;
    danger: boolean;
  };
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export class AdminApiService {
  static async getDashboard(): Promise<DashboardResponse> {
    return fetchJson<DashboardResponse>('/api/v1/admin/dashboard');
  }

  static async getUsers(): Promise<AdminUser[]> {
    const data = await fetchJson<{ users: AdminUser[] }>('/api/v1/admin/users');
    return data.users ?? [];
  }

  static async getPonds(): Promise<AdminPond[]> {
    const data = await fetchJson<{ ponds: AdminPond[] }>('/api/v1/admin/ponds');
    return data.ponds ?? [];
  }

  static async getRecords(limit = 300): Promise<DataRecord[]> {
    const data = await fetchJson<{ records: DataRecord[] }>(`/api/v1/admin/records?limit=${limit}`);
    return data.records ?? [];
  }

  static async getDevicePredictions(limit: number = 300): Promise<any[]> {
    const data = await fetchJson<{ devicePredictions: any[] }>(`/api/v1/admin/device-predictions?limit=${limit}`);
    return data.devicePredictions ?? [];
  }
}
