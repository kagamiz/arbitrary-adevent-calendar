import { writable } from 'svelte/store';
import type { User, Post, CalendarInfo } from './types';

// ユーザーストア
export const user = writable<User | null>(null);

// 投稿ストア
export const posts = writable<Post[]>([]);

// カレンダー情報ストア
export const calendarInfo = writable<CalendarInfo | null>(null);

// 概要データストア
export const overview = writable<string>('');

// ローディング状態ストア
export const loading = writable(false);

// エラーメッセージストア
export const error = writable<string | null>(null);
export const errorType = writable<'error' | 'success' | null>(null);

// カレンダー名ストア
export const calendarName = writable(import.meta.env.VITE_CALENDAR_NAME || "");

// 認証状態をチェック
export function checkAuth(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
}

// ログアウト
export function logout(reason: 'manual' | 'auth' = 'manual') {
    localStorage.removeItem('access_token');
    user.set(null);
    posts.set([]);
    // calendarInfoは保持する（ログアウト後もカレンダー情報は表示する必要がある）

    if (reason === 'manual') {
        setSuccess('ログアウトしました');
    } else if (reason === 'auth') {
        setError('認証情報を取得できませんでした', 'error');
    }
}

// エラーを設定
export function setError(message: string, type: 'error' | 'success' = 'error') {
    error.set(message);
    errorType.set(type);
    setTimeout(() => {
        error.set(null);
        errorType.set(null);
    }, 5000);
}

// 成功メッセージを設定
export function setSuccess(message: string) {
    setError(message, 'success');
} 
