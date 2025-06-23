<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import Quill from "quill";
    import "quill/dist/quill.snow.css";

    export let value = "";
    export let placeholder = "";

    let element: HTMLElement;
    let quill: any;

    onMount(() => {
        quill = new Quill(element, {
            theme: "snow",
            placeholder: placeholder,
            modules: {
                toolbar: [
                    [{ header: [1, 2, 3, false] }],
                    ["bold", "italic", "underline", "strike"],
                    ["link", "blockquote", "code-block"],
                    [{ list: "ordered" }, { list: "bullet" }],
                    [{ color: [] }, { background: [] }],
                    ["clean"],
                ],
            },
            formats: [
                "header",
                "bold",
                "italic",
                "underline",
                "strike",
                "link",
                "blockquote",
                "code-block",
                "list",
                "bullet",
                "color",
                "background",
            ],
        });

        // 初期値を設定
        if (value) {
            quill.root.innerHTML = value;
        }

        // 内容が変更されたときのイベント
        quill.on("text-change", () => {
            value = quill.root.innerHTML;
        });
    });

    onDestroy(() => {
        if (quill) {
            // Quillのクリーンアップ
            quill = null;
        }
    });

    // 外部から値が変更された場合の処理
    $: if (quill && value !== quill.root.innerHTML) {
        quill.root.innerHTML = value;
    }
</script>

<div class="quill-container">
    <div bind:this={element}></div>
</div>

<style>
    .quill-container {
        border: 1px solid #d1d5db;
        border-radius: 0.375rem;
        overflow: hidden;
        width: 100%;
        min-width: 600px;
    }

    .quill-container :global(.ql-toolbar) {
        background-color: #f9fafb;
        border-bottom: 1px solid #d1d5db;
        font-size: 12px;
    }

    .quill-container :global(.ql-toolbar .ql-formats) {
        margin-right: 8px;
    }

    .quill-container :global(.ql-toolbar .ql-picker) {
        font-size: 12px;
    }

    .quill-container :global(.ql-toolbar .ql-picker-label) {
        font-size: 12px;
        padding: 2px 4px;
    }

    .quill-container :global(.ql-toolbar .ql-picker-options) {
        font-size: 12px;
    }

    .quill-container :global(.ql-toolbar .ql-picker-item) {
        font-size: 12px;
        padding: 2px 4px;
    }

    .quill-container :global(.ql-container) {
        min-height: 8rem;
        background-color: white;
    }

    .quill-container :global(.ql-editor) {
        min-height: 8rem;
        padding: 0.75rem;
    }

    .quill-container :global(.ql-editor h1) {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }

    .quill-container :global(.ql-editor h2) {
        font-size: 1.25rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }

    .quill-container :global(.ql-editor h3) {
        font-size: 1.125rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }

    .quill-container :global(.ql-editor a) {
        color: #3b82f6;
        text-decoration: underline;
    }

    .quill-container :global(.ql-editor blockquote) {
        border-left: 4px solid #d1d5db;
        padding-left: 1rem;
        margin: 0.5rem 0;
        font-style: italic;
    }

    .quill-container :global(.ql-editor ul),
    .quill-container :global(.ql-editor ol) {
        padding-left: 1.5rem;
        margin: 0.5rem 0;
        display: block;
    }

    .quill-container :global(.ql-editor li) {
        margin: 0.25rem 0;
        display: list-item;
    }

    .quill-container :global(.ql-editor ul li) {
        list-style-type: disc;
        display: list-item;
    }

    .quill-container :global(.ql-editor ol li) {
        list-style-type: decimal;
        display: list-item;
    }

    /* ネストしたリスト */
    .quill-container :global(.ql-editor ul ul) {
        margin: 0.25rem 0;
        padding-left: 1rem;
        list-style-type: circle;
    }

    .quill-container :global(.ql-editor ol ol) {
        margin: 0.25rem 0;
        padding-left: 1rem;
        list-style-type: lower-alpha;
    }

    .quill-container :global(.ql-editor ul ul li) {
        list-style-type: circle;
        display: list-item;
    }

    .quill-container :global(.ql-editor ol ol li) {
        list-style-type: lower-alpha;
        display: list-item;
    }

    /* 3階層目のネスト */
    .quill-container :global(.ql-editor ul ul ul) {
        list-style-type: square;
    }

    .quill-container :global(.ql-editor ol ol ol) {
        list-style-type: lower-roman;
    }

    .quill-container :global(.ql-editor ul ul ul li) {
        list-style-type: square;
        display: list-item;
    }

    .quill-container :global(.ql-editor ol ol ol li) {
        list-style-type: lower-roman;
        display: list-item;
    }

    /* 混在したネスト */
    .quill-container :global(.ql-editor ul ol) {
        list-style-type: decimal;
    }

    .quill-container :global(.ql-editor ol ul) {
        list-style-type: disc;
    }

    .quill-container :global(.ql-editor ul ol li) {
        list-style-type: decimal;
        display: list-item;
    }

    .quill-container :global(.ql-editor ol ul li) {
        list-style-type: disc;
        display: list-item;
    }

    /* レスポンシブ対応 */
    @media (max-width: 768px) {
        .quill-container {
            min-width: auto;
        }

        .quill-container :global(.ql-toolbar) {
            font-size: 10px;
        }

        .quill-container :global(.ql-toolbar .ql-picker) {
            font-size: 10px;
        }

        .quill-container :global(.ql-toolbar .ql-picker-label) {
            font-size: 10px;
            padding: 1px 2px;
        }

        .quill-container :global(.ql-toolbar .ql-picker-options) {
            font-size: 10px;
        }

        .quill-container :global(.ql-toolbar .ql-picker-item) {
            font-size: 10px;
            padding: 1px 2px;
        }
    }
</style>
