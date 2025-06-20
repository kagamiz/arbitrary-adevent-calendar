export interface User {
    id: number;
    username: string;
    display_name: string;
    profile_image_url?: string;
    is_admin: boolean;
    created_at: string;
}

export interface Post {
    id: number;
    post_date: string;
    title: string;
    url: string;
    description?: string;
    user_id: number;
    user?: User;
    created_at: string;
    updated_at: string;
    is_public: boolean;
}

export interface PostCreate {
    post_date: string;
    title: string;
    url: string;
    description?: string;
}

export interface PostUpdate {
    title?: string;
    url?: string;
    description?: string;
}

export interface CalendarInfo {
    start_date: string;
    end_date: string;
    total_days: number;
}

export interface AuthResponse {
    auth_url: string;
}

export interface Token {
    access_token: string;
    token_type: string;
} 
