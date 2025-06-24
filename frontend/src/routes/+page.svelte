<script lang="ts">
    import { onMount } from "svelte";
    import {
        user,
        posts,
        calendarInfo,
        loading,
        error,
        errorType,
        checkAuth,
        logout,
        setError,
        calendarName,
        overview,
    } from "$lib/stores";
    import { apiClient } from "$lib/api";
    import {
        Calendar,
        User,
        LogOut,
        Plus,
        ExternalLink,
        Edit,
        Trash2,
        Eye,
        Settings,
    } from "lucide-svelte";
    import type { Post } from "$lib/types";
    import QuillEditor from "$lib/QuillEditor.svelte";

    let showContentModal = false;
    let showActionModal = false;
    let showPreRegisterModal = false;
    let selectedPost: Post | null = null;
    let contentForm = {
        title: "",
        url: "",
        description: "",
    };
    let preRegisterForm = {
        post_date: "",
        username: "",
    };
    let calendarDates: string[] = [];
    let menuOpen = false;
    let overviewHtml = "";
    let overviewEdit = "";
    let editing = false;
    let previewing = false;
    let saving = false;
    let errorMsg = "";

    onMount(async () => {
        console.log("VITE_FRONTEND_URL:", import.meta.env.VITE_FRONTEND_URL);

        // URLパラメータから認証エラーをチェック
        const urlParams = new URLSearchParams(window.location.search);
        const authError = urlParams.get("auth_error");
        if (authError === "login_failed") {
            setError("ログインに失敗しました");
            // URLからエラーパラメータを削除
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.delete("auth_error");
            window.history.replaceState({}, "", newUrl.toString());
        }

        await loadData();
        try {
            const res = await apiClient.getOverview();
            overview.set(res.content);
            overviewHtml = res.content;
            overviewEdit = res.content;
        } catch (e) {
            errorMsg = "概要の取得に失敗しました";
        }
    });

    async function loadData() {
        loading.set(true);
        try {
            // カレンダー情報を取得
            const info = await apiClient.getCalendarInfo();
            calendarInfo.set(info);

            // カレンダー名を更新（バックエンドから取得した値または環境変数の値）
            calendarName.set(
                info.calendar_name || import.meta.env.VITE_CALENDAR_NAME || "",
            );

            // 認証済みの場合、ユーザー情報と投稿を取得
            if (checkAuth()) {
                try {
                    const [userData, postsData] = await Promise.all([
                        apiClient.getCurrentUser(),
                        apiClient.getPosts(),
                    ]);
                    user.set(userData);
                    posts.set(postsData);
                } catch (err) {
                    // 認証情報取得失敗時は未ログインページへリダイレクト
                    window.location.href = "/";
                    return;
                }
            } else {
                // 未ログイン時は公開状態APIを使う
                const postsData = await apiClient.getPublicPosts();
                posts.set(postsData);
            }
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "データの読み込みに失敗しました",
            );
        } finally {
            loading.set(false);
        }
    }

    async function handleXLogin() {
        try {
            const authResponse = await apiClient.getAuthUrl();
            window.location.href = authResponse.auth_url;
        } catch (err) {
            setError("認証URLの取得に失敗しました");
        }
    }

    async function handleMockLogin() {
        try {
            // ローカル環境では直接モック認証エンドポイントにアクセス
            window.location.href = "http://localhost:8000/auth/mock";
        } catch (err) {
            setError("モック認証に失敗しました");
        }
    }

    // ローカル環境かどうかを判定
    function isLocalEnvironment(): boolean {
        return (
            import.meta.env.VITE_FRONTEND_URL?.includes("localhost") ||
            import.meta.env.VITE_FRONTEND_URL?.includes("127.0.0.1")
        );
    }

    async function handleReservePost(postDate: string) {
        const scrollY = window.scrollY;
        try {
            await apiClient.reservePost(postDate);
            await loadData();
            window.scrollTo(0, scrollY);
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "担当者の予約に失敗しました",
            );
        }
    }

    async function handlePreRegisterPost() {
        try {
            await apiClient.preRegisterPost(
                preRegisterForm.post_date,
                preRegisterForm.username,
            );
            showPreRegisterModal = false;
            preRegisterForm = { post_date: "", username: "" };
            await loadData();
        } catch (err) {
            setError(
                err instanceof Error ? err.message : "事前登録に失敗しました",
            );
        }
    }

    async function handleDeletePost(post: Post) {
        if (!confirm("この投稿を削除しますか？")) return;
        const scrollY = window.scrollY;
        try {
            await apiClient.deletePost(post.id);
            await loadData();
            window.scrollTo(0, scrollY);
        } catch (err) {
            setError(
                err instanceof Error ? err.message : "投稿の削除に失敗しました",
            );
        }
    }

    async function handlePublishPost(post: Post) {
        try {
            await apiClient.publishPost(post.id);
            await loadData();
        } catch (err) {
            setError(
                err instanceof Error ? err.message : "投稿の公開に失敗しました",
            );
        }
    }

    async function handleUpdateContent() {
        if (!selectedPost) return;
        try {
            await apiClient.updatePostContent(selectedPost.id, contentForm);
            showContentModal = false;
            selectedPost = null;
            await loadData();
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "記事情報の更新に失敗しました",
            );
        }
    }

    function openContentModal(post: Post) {
        selectedPost = post;
        contentForm = {
            title: post.title,
            url: post.url,
            description: post.description || "",
        };
        showContentModal = true;
    }

    function openActionModal(post: Post) {
        selectedPost = post;
        showActionModal = true;
    }

    function formatDate(dateStr: string): string {
        const date = new Date(dateStr);
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const dayOfWeek = date.getDay();
        const dayNames = ["日", "月", "火", "水", "木", "金", "土"];
        return `${month}/${day}(${dayNames[dayOfWeek]})`;
    }

    function getDateColor(dateStr: string): string {
        const date = new Date(dateStr);
        const dayOfWeek = date.getDay();
        if (dayOfWeek === 0) return "text-red-600"; // 日曜日
        if (dayOfWeek === 6) return "text-blue-600"; // 土曜日
        return "text-gray-900"; // 平日
    }

    function isToday(dateStr: string): boolean {
        const today = new Date();
        const date = new Date(dateStr);
        return today.toDateString() === date.toDateString();
    }

    function canEdit(post: Post): boolean {
        if (!$user) return false;
        return $user.is_admin || post.user_id === $user.id;
    }

    function hasFullAccess(post: Post): boolean {
        // 公開済みの投稿は誰でも見られる
        if (post.is_public) return true;
        // 未ログイン時は未公開投稿は見られない
        if (!$user) return false;
        // 未公開の投稿は投稿者本人または管理者のみ
        return $user.is_admin || post.user_id === $user.id;
    }

    function canSeePostDetails(post: Post): boolean {
        // バックエンドから返されるis_publicを使用
        return post.is_public;
    }

    $: if ($calendarInfo) {
        const start = new Date($calendarInfo.start_date);
        const end = new Date($calendarInfo.end_date);
        const dates = [];
        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
            dates.push(d.toISOString().slice(0, 10));
        }
        calendarDates = dates;
    }

    async function handleLogout() {
        logout("manual");
        await loadData(); // ログアウト後にデータを再読み込み
    }

    async function saveOverview() {
        saving = true;
        errorMsg = "";
        try {
            const res = await apiClient.updateOverview(overviewEdit);
            overview.set(res.content);
            overviewHtml = res.content;
            editing = false;
        } catch (e) {
            errorMsg = "保存に失敗しました";
        } finally {
            saving = false;
        }
    }
</script>

<svelte:head>
    <title>{$calendarName || "arbitrary-advent-calendar"}</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- ヘッダー -->
    <header class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <div class="flex items-center space-x-3">
                    <img
                        src="/jbadv.png"
                        alt="logo"
                        class="h-12 object-contain rounded"
                    />
                    <h1 class="text-xl font-bold text-gray-900">
                        {$calendarName || "arbitrary-advent-calendar"}
                    </h1>
                    {#if $user && $user.is_admin}
                        <span
                            class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full"
                        >
                            管理者モード
                        </span>
                    {/if}
                </div>

                <!-- PC: 横並び, モバイル: ハンバーガー -->
                <div class="hidden sm:flex items-center space-x-4">
                    {#if $user}
                        <div class="flex items-center space-x-2">
                            {#if $user.profile_image_url}
                                <img
                                    src={$user.profile_image_url}
                                    alt={$user.display_name}
                                    class="h-8 w-8 rounded-full"
                                />
                            {:else}
                                <User class="h-8 w-8 text-gray-400" />
                            {/if}
                            <span class="text-sm font-medium text-gray-700"
                                >{$user.display_name}</span
                            >
                        </div>
                        {#if $user.is_admin}
                            <button
                                on:click={() => (showPreRegisterModal = true)}
                                class="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors"
                            >
                                <Plus class="h-4 w-4" />
                                <span>事前登録</span>
                            </button>
                        {/if}
                        <button
                            on:click={handleLogout}
                            class="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                        >
                            <LogOut class="h-4 w-4" />
                            <span>ログアウト</span>
                        </button>
                    {:else}
                        <button
                            on:click={isLocalEnvironment()
                                ? handleMockLogin
                                : handleXLogin}
                            class="flex items-center space-x-2 px-4 py-2 bg-black text-white rounded-md hover:bg-gray-800 transition-colors"
                        >
                            <span
                                >{isLocalEnvironment()
                                    ? "モックログイン"
                                    : "Xでログイン"}</span
                            >
                        </button>
                        {#if isLocalEnvironment()}
                            <button
                                on:click={() => {
                                    window.location.href =
                                        "http://localhost:8000/auth/mock2";
                                }}
                                class="flex items-center space-x-2 px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-900 transition-colors"
                            >
                                <span>モックユーザー２でログイン</span>
                            </button>
                        {/if}
                    {/if}
                </div>
                <!-- ハンバーガー: sm未満で表示 -->
                <div class="sm:hidden">
                    <button
                        on:click={() => (menuOpen = !menuOpen)}
                        class="p-2 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                        <svg
                            class="h-6 w-6"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                            ><path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M4 6h16M4 12h16M4 18h16"
                            ></path></svg
                        >
                    </button>
                    {#if menuOpen}
                        <div
                            class="absolute right-4 top-16 z-50 w-48 bg-white rounded shadow-md py-2 border"
                        >
                            {#if $user}
                                <div
                                    class="flex items-center space-x-2 px-4 py-2"
                                >
                                    {#if $user.profile_image_url}
                                        <img
                                            src={$user.profile_image_url}
                                            alt={$user.display_name}
                                            class="h-8 w-8 rounded-full"
                                        />
                                    {:else}
                                        <User class="h-8 w-8 text-gray-400" />
                                    {/if}
                                    <span
                                        class="text-sm font-medium text-gray-700"
                                        >{$user.display_name}</span
                                    >
                                </div>
                                {#if $user.is_admin}
                                    <button
                                        on:click={() => {
                                            showPreRegisterModal = true;
                                            menuOpen = false;
                                        }}
                                        class="flex items-center space-x-1 w-full px-4 py-2 text-sm font-medium text-green-700 hover:bg-green-50"
                                    >
                                        <Plus class="h-4 w-4" />
                                        <span>事前登録</span>
                                    </button>
                                {/if}
                                <button
                                    on:click={() => {
                                        handleLogout();
                                        menuOpen = false;
                                    }}
                                    class="flex items-center space-x-1 w-full px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
                                >
                                    <LogOut class="h-4 w-4" />
                                    <span>ログアウト</span>
                                </button>
                            {:else}
                                <button
                                    on:click={() => {
                                        isLocalEnvironment()
                                            ? handleMockLogin()
                                            : handleXLogin();
                                        menuOpen = false;
                                    }}
                                    class="flex items-center space-x-2 w-full px-4 py-2 text-sm font-medium text-black hover:bg-gray-100"
                                >
                                    <span
                                        >{isLocalEnvironment()
                                            ? "モックログイン"
                                            : "Xでログイン"}</span
                                    >
                                </button>
                                {#if isLocalEnvironment()}
                                    <button
                                        on:click={() => {
                                            window.location.href =
                                                "http://localhost:8000/auth/mock2";
                                            menuOpen = false;
                                        }}
                                        class="flex items-center space-x-2 w-full px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
                                    >
                                        <span>モックユーザー２でログイン</span>
                                    </button>
                                {/if}
                            {/if}
                        </div>
                    {/if}
                </div>
            </div>
        </div>
    </header>

    <!-- メインコンテンツ -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {#if $loading}
            <div class="flex justify-center items-center h-64">
                <div
                    class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"
                ></div>
            </div>
        {:else if $calendarInfo}
            <!-- 概要セクション -->
            {#if $user && $user.is_admin}
                <div class="mb-4 bg-white rounded shadow p-4 w-full">
                    <div class="flex justify-between items-center mb-2">
                        <span class="font-semibold">説明用テキスト記入欄</span>
                        {#if !editing}
                            <button
                                class="text-sm text-blue-600 hover:underline"
                                on:click={() => (editing = true)}>編集</button
                            >
                        {/if}
                    </div>
                    {#if editing}
                        <div class="mb-2 w-full overflow-x-auto">
                            <QuillEditor
                                bind:value={overviewEdit}
                                placeholder="カレンダーの概要を入力してください..."
                            />
                        </div>
                        <div class="flex space-x-2">
                            <button
                                class="px-3 py-1 bg-blue-600 text-white rounded"
                                on:click={saveOverview}
                                disabled={saving}>保存</button
                            >
                            <button
                                class="px-3 py-1 bg-green-600 text-white rounded"
                                on:click={() => (previewing = !previewing)}
                            >
                                {previewing
                                    ? "プレビューを閉じる"
                                    : "プレビュー"}
                            </button>
                            <button
                                class="px-3 py-1 bg-gray-300 rounded"
                                on:click={() => {
                                    editing = false;
                                    previewing = false;
                                    overviewEdit = overviewHtml;
                                }}>キャンセル</button
                            >
                        </div>
                        {#if previewing}
                            <div class="mt-4 p-4 bg-gray-50 rounded border">
                                <h4
                                    class="text-sm font-medium text-gray-700 mb-2"
                                >
                                    プレビュー:
                                </h4>
                                <div class="prose max-w-none quill-preview">
                                    {@html overviewEdit}
                                </div>
                            </div>
                        {/if}
                        {#if errorMsg}
                            <div class="text-red-600 text-sm mt-1">
                                {errorMsg}
                            </div>
                        {/if}
                    {:else}
                        <div class="mb-4 bg-white rounded shadow p-4">
                            <div class="prose max-w-none quill-preview">
                                <QuillEditor
                                    value={overviewHtml}
                                    preview={true}
                                />
                            </div>
                        </div>
                    {/if}
                </div>
            {:else if overviewHtml}
                <div class="mb-4 bg-white rounded shadow p-4">
                    <div class="prose max-w-none quill-preview">
                        <QuillEditor value={overviewHtml} preview={true} />
                    </div>
                </div>
            {/if}

            <div class="bg-white rounded-lg shadow-sm p-6 mb-8">
                <h2 class="text-lg font-semibold text-gray-900 mb-4">
                    カレンダー
                </h2>
                <div class="overflow-x-auto">
                    <table
                        class="min-w-[600px] w-full border-collapse text-sm sm:text-base"
                    >
                        <tbody>
                            {#each calendarDates as dateStr, i (dateStr)}
                                {@const postsOfDay = $posts.filter(
                                    (p) => p.post_date === dateStr,
                                )}
                                <tr class="hover:bg-indigo-50">
                                    <td
                                        class="p-1 sm:p-2 border-b whitespace-nowrap w-16 {getDateColor(
                                            dateStr,
                                        )} align-middle"
                                    >
                                        {formatDate(dateStr)}
                                    </td>
                                    {#if $user}
                                        <td
                                            class="p-1 sm:p-2 border-b w-8 min-w-[32px] align-middle text-center"
                                        >
                                            <button
                                                type="button"
                                                class="px-1 py-0.5 bg-green-200 text-green-700 rounded hover:bg-green-300 text-xs"
                                                title="この日に記事を追加"
                                                on:click={() =>
                                                    handleReservePost(dateStr)}
                                                >＋</button
                                            >
                                        </td>
                                    {/if}
                                    <td class="p-1 sm:p-2 border-b">
                                        {#if postsOfDay.length > 0}
                                            {#each postsOfDay as post}
                                                {#if hasFullAccess(post)}
                                                    <!-- 記事タイトル・担当者・説明など（既存の表示ロジックを流用） -->
                                                    <div
                                                        class="mb-2 border-b border-gray-200 pb-2 last:border-b-0 last:pb-0"
                                                    >
                                                        <!-- タイトル・URL表示 -->
                                                        {#if post.url && post.url.trim() !== "" && post.title && post.title.trim() !== ""}
                                                            <a
                                                                href={post.url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                class="text-indigo-600 hover:underline break-all font-medium text-base"
                                                                >{post.title}<ExternalLink
                                                                    class="inline h-4 w-4"
                                                                /></a
                                                            >
                                                        {:else if post.url && post.url.trim() !== ""}
                                                            <a
                                                                href={post.url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                class="text-indigo-600 hover:underline break-all font-medium text-base"
                                                                >{post.url}<ExternalLink
                                                                    class="inline h-4 w-4"
                                                                /></a
                                                            >
                                                        {:else if post.title && post.title.trim() !== ""}
                                                            <span
                                                                class="break-all font-medium text-base"
                                                                >{post.title}</span
                                                            >
                                                        {:else}
                                                            <span
                                                                class="text-gray-700 break-all font-medium text-base"
                                                                >(タイトル未定)</span
                                                            >
                                                        {/if}
                                                        <!-- 担当者情報 -->
                                                        <div
                                                            class="flex items-center space-x-1 mt-1"
                                                        >
                                                            <span
                                                                class="text-gray-700"
                                                                >by</span
                                                            >
                                                            {#if post.user?.profile_image_url}
                                                                <img
                                                                    src={post
                                                                        .user
                                                                        .profile_image_url}
                                                                    alt={post
                                                                        .user
                                                                        .display_name}
                                                                    class="h-5 w-5 rounded-full"
                                                                />
                                                            {:else}
                                                                <User
                                                                    class="h-5 w-5 text-gray-400"
                                                                />
                                                            {/if}
                                                            <span
                                                                class="text-gray-700"
                                                            >
                                                                {#if post.user?.display_name && post.user.display_name.trim() !== ""}
                                                                    {post.user
                                                                        .display_name}
                                                                    {#if post.user?.username && post.user.username.trim() !== ""}
                                                                        {@html ` (<a href=\"https://x.com/${post.user.username}\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"text-indigo-600 hover:underline\">@${post.user.username}</a>)`}
                                                                    {/if}
                                                                {:else if post.user?.username && post.user.username.trim() !== ""}
                                                                    {@html `<a href=\"https://x.com/${post.user.username}\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"text-indigo-600 hover:underline\">@${post.user.username}</a>`}
                                                                {/if}
                                                            </span>
                                                            {#if canEdit(post)}
                                                                <button
                                                                    on:click={() =>
                                                                        openActionModal(
                                                                            post,
                                                                        )}
                                                                    title="設定"
                                                                >
                                                                    <Settings
                                                                        class="inline h-5 w-5 ml-1 text-gray-500 hover:text-indigo-600"
                                                                    />
                                                                </button>
                                                            {/if}
                                                        </div>
                                                        <!-- 説明 -->
                                                        {#if post.description && post.description.trim() !== ""}
                                                            <div
                                                                class="text-sm text-gray-600 break-all mt-1"
                                                            >
                                                                {post.description}
                                                            </div>
                                                        {/if}
                                                    </div>
                                                {:else}
                                                    <!-- 未公開記事 -->
                                                    <div
                                                        class="mb-2 border-b border-gray-200 pb-2 last:border-b-0 last:pb-0"
                                                    >
                                                        <span
                                                            class="text-gray-400 font-medium text-base"
                                                            >？？？</span
                                                        >
                                                        <div
                                                            class="flex items-center space-x-1"
                                                        >
                                                            <span
                                                                class="text-gray-400"
                                                                >by</span
                                                            >
                                                            <User
                                                                class="h-5 w-5 text-gray-300"
                                                            />
                                                            <span
                                                                class="text-gray-400"
                                                                >？？？</span
                                                            >
                                                        </div>
                                                    </div>
                                                {/if}
                                            {/each}
                                        {:else}
                                            <div class="text-gray-300">
                                                記事なし
                                            </div>
                                        {/if}
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </div>
        {/if}

        <!-- エラーメッセージ -->
        {#if $error}
            <div
                class="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 px-6 py-3 rounded shadow-lg text-white transition-all duration-300 flex items-center gap-4"
                class:bg-green-500={$errorType === "success"}
                class:bg-red-500={$errorType === "error"}
            >
                <span>{$error}</span>
                <button
                    class="ml-2 text-white text-xl focus:outline-none"
                    on:click={() => {
                        error.set(null);
                        errorType.set(null);
                    }}
                    aria-label="閉じる">×</button
                >
            </div>
        {/if}

        <!-- 事前登録モーダル -->
        {#if showPreRegisterModal}
            <div
                class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            >
                <div class="bg-white rounded-lg p-6 w-full max-w-md">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">
                        事前登録
                    </h3>
                    <form on:submit|preventDefault={handlePreRegisterPost}>
                        <div class="space-y-4">
                            <div>
                                <label
                                    for="pre_register_date"
                                    class="block text-sm font-medium text-gray-700"
                                    >投稿日</label
                                >
                                <select
                                    id="pre_register_date"
                                    bind:value={preRegisterForm.post_date}
                                    required
                                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                >
                                    <option value=""
                                        >日付を選択してください</option
                                    >
                                    {#each calendarDates as dateStr}
                                        <option value={dateStr}
                                            >{formatDate(dateStr)}</option
                                        >
                                    {/each}
                                </select>
                            </div>
                            <div>
                                <label
                                    for="username"
                                    class="block text-sm font-medium text-gray-700"
                                    >Xユーザー名</label
                                >
                                <input
                                    type="text"
                                    id="username"
                                    bind:value={preRegisterForm.username}
                                    placeholder="例: mock_user"
                                    required
                                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>
                        </div>
                        <div class="flex justify-end space-x-3 mt-6">
                            <button
                                type="button"
                                on:click={() => (showPreRegisterModal = false)}
                                class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                            >
                                キャンセル
                            </button>
                            <button
                                type="submit"
                                class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 transition-colors"
                            >
                                登録する
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        {/if}

        <!-- 記事情報入力・更新モーダル -->
        {#if showContentModal && selectedPost}
            <div
                class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            >
                <div class="bg-white rounded-lg p-6 w-full max-w-md">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">
                        記事情報の入力・更新
                    </h3>
                    <form on:submit|preventDefault={handleUpdateContent}>
                        <div class="space-y-4">
                            <div>
                                <label
                                    class="block text-sm font-medium text-gray-700"
                                    >投稿日</label
                                >
                                <div
                                    class="mt-1 p-2 bg-gray-100 rounded-md text-gray-700"
                                >
                                    {formatDate(selectedPost.post_date)}
                                </div>
                            </div>
                            <div>
                                <label
                                    for="content_title"
                                    class="block text-sm font-medium text-gray-700"
                                    >記事タイトル（任意）</label
                                >
                                <input
                                    type="text"
                                    id="content_title"
                                    bind:value={contentForm.title}
                                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>
                            <div>
                                <label
                                    for="content_url"
                                    class="block text-sm font-medium text-gray-700"
                                    >記事URL（任意）</label
                                >
                                <input
                                    type="url"
                                    id="content_url"
                                    bind:value={contentForm.url}
                                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                />
                            </div>
                            <div>
                                <label
                                    for="content_description"
                                    class="block text-sm font-medium text-gray-700"
                                    >説明（任意）</label
                                >
                                <textarea
                                    id="content_description"
                                    bind:value={contentForm.description}
                                    rows="3"
                                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                ></textarea>
                            </div>
                        </div>
                        <div class="flex justify-end space-x-3 mt-6">
                            <button
                                type="button"
                                on:click={() => (showContentModal = false)}
                                class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                            >
                                キャンセル
                            </button>
                            <button
                                type="submit"
                                class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 transition-colors"
                            >
                                更新する
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        {/if}

        <!-- 操作モーダル -->
        {#if showActionModal && selectedPost}
            <div
                class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            >
                <div class="bg-white rounded-lg p-6 w-full max-w-sm">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">
                        操作メニュー
                    </h3>
                    <div class="space-y-3">
                        <button
                            class="w-full px-4 py-2 bg-blue-200 text-blue-700 rounded hover:bg-blue-300 transition-colors text-left"
                            on:click={() => {
                                showActionModal = false;
                                if (selectedPost)
                                    openContentModal(selectedPost);
                            }}
                        >
                            記事情報の入力・更新
                        </button>
                        <button
                            class="w-full px-4 py-2 bg-red-200 text-red-700 rounded hover:bg-red-300 transition-colors text-left"
                            on:click={() => {
                                showActionModal = false;
                                if (selectedPost)
                                    handleDeletePost(selectedPost);
                            }}
                        >
                            {#if $user && $user.is_admin && selectedPost && selectedPost.user_id !== $user.id}
                                担当者を外す
                            {:else}
                                担当を外れる
                            {/if}
                        </button>
                    </div>
                    <div class="flex justify-end mt-6">
                        <button
                            type="button"
                            on:click={() => (showActionModal = false)}
                            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                        >
                            キャンセル
                        </button>
                    </div>
                </div>
            </div>
        {/if}
    </main>
</div>
