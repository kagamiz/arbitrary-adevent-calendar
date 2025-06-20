<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { user, loading, setError } from "$lib/stores";
    import { apiClient } from "$lib/api";
    import { CheckCircle, Loader } from "lucide-svelte";

    let authSuccess = false;
    let authError = false;

    onMount(async () => {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get("token");

        if (token) {
            // トークンをローカルストレージに保存
            localStorage.setItem("access_token", token);

            try {
                // ユーザー情報を取得
                const userData = await apiClient.getCurrentUser();
                user.set(userData);
                authSuccess = true;

                // 3秒後にメインページにリダイレクト
                setTimeout(() => {
                    goto("/");
                }, 3000);
            } catch (err) {
                authError = true;
                setError("認証に失敗しました");
            }
        } else {
            authError = true;
            setError("トークンが見つかりません");
        }
    });
</script>

<svelte:head>
    <title>認証完了 - アドベントカレンダー</title>
</svelte:head>

<div
    class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center"
>
    <div class="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
        {#if $loading}
            <div class="text-center">
                <Loader
                    class="h-12 w-12 text-indigo-600 animate-spin mx-auto mb-4"
                />
                <h2 class="text-xl font-semibold text-gray-900 mb-2">
                    認証中...
                </h2>
                <p class="text-gray-600">しばらくお待ちください</p>
            </div>
        {:else if authSuccess}
            <div class="text-center">
                <CheckCircle class="h-12 w-12 text-green-600 mx-auto mb-4" />
                <h2 class="text-xl font-semibold text-gray-900 mb-2">
                    認証完了
                </h2>
                <p class="text-gray-600 mb-4">Xでのログインが完了しました</p>
                <p class="text-sm text-gray-500">
                    まもなくメインページに移動します...
                </p>
            </div>
        {:else if authError}
            <div class="text-center">
                <div
                    class="h-12 w-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4"
                >
                    <span class="text-red-600 text-xl">×</span>
                </div>
                <h2 class="text-xl font-semibold text-gray-900 mb-2">
                    認証エラー
                </h2>
                <p class="text-gray-600 mb-4">認証に失敗しました</p>
                <button
                    on:click={() => goto("/")}
                    class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                >
                    メインページに戻る
                </button>
            </div>
        {/if}
    </div>
</div>
