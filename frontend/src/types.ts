export type UserRole = "member" | "admin";
export type ReservationStatus = "REQUESTED" | "APPROVED" | "PICKED_UP" | "RETURNED" | "DENIED" | "CANCELLED";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_suspended: boolean;
  created_at: string;
}

export interface Invitation {
  id: number;
  email: string;
  token: string;
  used_at: string | null;
  expires_at: string | null;
  created_at: string;
}

export interface Tool {
  id: number;
  owner_id: number;
  name: string;
  description: string;
  category: string;
  condition: string;
  photo_url?: string | null;
  lending_rules?: string | null;
  is_active: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at?: string | null;
  owner?: User | null;
}

export interface Reservation {
  id: number;
  tool_id: number;
  borrower_id: number;
  status: ReservationStatus;
  start_date: string;
  end_date: string;
  created_at: string;
  updated_at?: string | null;
  tool?: Tool | null;
  borrower?: User | null;
}

export interface Message {
  id: number;
  reservation_id: number;
  sender_id: number;
  body: string;
  created_at: string;
  sender?: User | null;
}

export interface NotificationItem {
  id: number;
  user_id?: number;
  reservation_id?: number | null;
  title: string;
  body: string;
  is_read?: boolean;
  created_at: string;
}

export interface Review {
  id: number;
  reservation_id: number;
  reviewer_id: number;
  reviewee_id: number;
  rating: number;
  comment?: string | null;
  created_at: string;
}

export interface DamageReport {
  id: number;
  reservation_id: number;
  reporter_id: number;
  description: string;
  photo_url?: string | null;
  created_at: string;
}

export interface Dashboard {
  profile: User;
  my_tools: Tool[];
  incoming_requests: Reservation[];
  outgoing_reservations: Reservation[];
  unread_notifications: NotificationItem[];
}
