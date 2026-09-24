export type WasteCategory =
  | "plastic" | "metal" | "glass" | "paper_cardboard"
  | "organic" | "e_waste" | "textile" | "other" | "unknown";

export interface Alternative { category: WasteCategory; confidence: number; }

export interface PredictionResult {
  category: WasteCategory;
  display_name: string;
  confidence: number;
  is_uncertain: boolean;
  recommendation: string;
  hardware_command: string;
  model_version: string;
  message?: string;
  alternatives?: Alternative[];
}

export interface PredictionHistoryItem {
  id: string;
  category: WasteCategory;
  confidence: number;
  is_uncertain: boolean;
  recommendation: string;
  hardware_command: string;
  source: "upload" | "webcam";
  model_version: string;
  image_url?: string;
  created_at: string;
}

export interface ModelInfo {
  model_version: string;
  architecture: string;
  classes: number;
  class_names: string[];
  image_size: number;
  trained_at?: string;
  confidence_threshold: number;
  uncertain_threshold: number;
  missing_categories: string[];
  model_available: boolean;
}

export interface Profile {
  id: string;
  user_id: string;
  display_name: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}
