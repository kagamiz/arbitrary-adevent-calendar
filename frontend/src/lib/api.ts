import type { User, Post, PostCreate, PostUpdate, AuthResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export type CalendarInfo = {
    start_date: string;
    end_date: string;
    total_days: number;
    calendar_name: string;
};

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}/api${endpoint}`;
        const token = localStorage.getItem('access_token');

        const config: RequestInit = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        if (token) {
            config.headers = {
                ...config.headers,
                Authorization: `Bearer ${token}`,
            };
        }

        const response = await fetch(url, config);

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }

        return response.json();
    }

    // 認証関連
    async getAuthUrl(): Promise<AuthResponse> {
        return this.request<AuthResponse>('/auth/x/url');
    }

    // カレンダー情報
    async getCalendarInfo(): Promise<CalendarInfo> {
        return this.request<CalendarInfo>('/calendar/info');
    }

    // 投稿関連
    async getPosts(): Promise<Post[]> {
        return this.request<Post[]>('/posts');
    }

    async getPostsForGuest(): Promise<Post[]> {
        return this.request<Post[]>('/posts/guest');
    }

    async getPublicPosts(): Promise<Post[]> {
        return this.request<Post[]>('/posts/public');
    }

    async getPostsExistence(): Promise<{ post_dates: string[] }> {
        return this.request<{ post_dates: string[] }>('/posts/existence');
    }

    async createPost(post: PostCreate): Promise<Post> {
        return this.request<Post>('/posts', {
            method: 'POST',
            body: JSON.stringify(post),
        });
    }

    async reservePost(postDate: string): Promise<Post> {
        return this.request<Post>('/posts/reserve', {
            method: 'POST',
            body: JSON.stringify({ post_date: postDate }),
        });
    }

    async preRegisterPost(postDate: string, username: string): Promise<{ message: string; post: Post }> {
        return this.request<{ message: string; post: Post }>('/posts/pre-register', {
            method: 'POST',
            body: JSON.stringify({ post_date: postDate, username }),
        });
    }

    async updatePost(postId: number, post: PostUpdate): Promise<Post> {
        return this.request<Post>(`/posts/${postId}`, {
            method: 'PUT',
            body: JSON.stringify(post),
        });
    }

    async updatePostContent(postId: number, content: { title?: string; url?: string; description?: string }): Promise<Post> {
        return this.request<Post>(`/posts/${postId}/content`, {
            method: 'PUT',
            body: JSON.stringify(content),
        });
    }

    async deletePost(postId: number): Promise<void> {
        return this.request<void>(`/posts/${postId}`, {
            method: 'DELETE',
        });
    }

    async publishPost(postId: number): Promise<Post> {
        return this.request<Post>(`/posts/${postId}/publish`, {
            method: 'POST',
        });
    }

    // ユーザー情報
    async getCurrentUser(): Promise<User> {
        return this.request<User>('/me');
    }
}

export const apiClient = new ApiClient(); 
