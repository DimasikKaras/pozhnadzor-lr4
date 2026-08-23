export type Role = 'Администратор' | 'Старший инспектор' | 'Инспектор';
export type RiskLevel = 'Высокий' | 'Значительный' | 'Средний' | 'Умеренный' | 'Низкий';
export type EquipmentStatus = 'Исправен' | 'Требует ремонта' | 'Списан' | 'На проверке';
export type InspectionResult = 'Пройдена' | 'Не пройдена';

export interface Inspector {
  id: number;
  full_name: string;
  rank: string;
  phone?: string;
  email: string;
  role: Role;
}

export interface Facility {
  id: number;
  name: string;
  address: string;
  risk_level: RiskLevel;
  cadastral_number?: string;
  responsible_person?: string;
}

export interface Equipment {
  id: number;
  facility_id: number;
  name?: string;
  type: string;
  serial_number?: string;
  status: EquipmentStatus;
  last_check_date: string;
  next_check_date?: string;
  notes?: string;
}

export interface Inspection {
  id: number;
  facility_id: number;
  inspector_id: number;
  date: string;
  result: InspectionResult;
  violations?: string;
  prescription_number?: string;
}
