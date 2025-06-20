import { writable } from 'svelte/store';
import type { User, Post, CalendarInfo } from './types';

// ユーザーストア
export const user = writable<User | null>(null);

// 投稿ストア
export const posts = writable<Post[]>([]);

// カレンダー情報ストア
export const calendarInfo = writable<CalendarInfo | null>(null);

// ローディング状態ストア
export const loading = writable(false);

// エラーメッセージストア
export const error = writable<string | null>(null);

// カレンダー名ストア
export const calendarName = writable(import.meta.env.VITE_CALENDAR_NAME || "");

// 認証状態をチェック
export function checkAuth(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
}

// ログアウト
export function logout() {
    localStorage.removeItem('access_token');
    user.set(null);
    posts.set([]);
    // calendarInfoは保持する（ログアウト後もカレンダー情報は表示する必要がある）
}

// エラーを設定
export function setError(message: string) {
    error.set(message);
    setTimeout(() => {
        error.set(null);
    }, 5000);
} 
