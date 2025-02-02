(function() {
    // デバッグモードの設定
    const DEBUG = true; // この値を true に変更するとデバッグログが有効になります
    const LOG_PREFIX = '[X-Twitter-Widget]';

    function log(message, ...args) {
        if (DEBUG) {
            console.log(`${LOG_PREFIX} ${message}`, ...args);
        }
    }

    // カラースキームを取得する関数
    function getColorScheme() {
        // 既存のカラースキームを取得
        const html = document.documentElement;
        const body = document.body;
        const currentScheme = html.getAttribute('data-md-color-scheme') ||
                            body.getAttribute('data-md-color-scheme');

        if (currentScheme) {
            log('Current document color scheme:', currentScheme);
            return currentScheme === 'slate' ? 'dark' : 'light';
        }

        // パレットから選択状態を取得
        const palette = document.querySelector('[data-md-component="palette"]');
        if (palette) {
            const checkedInput = palette.querySelector('input[type="radio"]:checked');
            if (checkedInput) {
                const scheme = checkedInput.getAttribute('data-md-color-scheme');
                log('Using palette color scheme:', scheme);
                return scheme === 'slate' ? 'dark' : 'light';
            }
        }

        // ローカルストレージから取得
        const storedScheme = localStorage.getItem('data-md-color-scheme');
        if (storedScheme) {
            log('Using stored color scheme:', storedScheme);
            return storedScheme === 'slate' ? 'dark' : 'light';
        }

        // デフォルトはライトモード
        log('Using default light theme');
        return 'light';
    }

    // ツイートを再構築する関数
    function recreateTweet(container) {
        const theme = getColorScheme();
        const url = container.getAttribute('data-url');
        log('Recreating tweet:', url, 'with theme:', theme);

        // 既存のコンテンツをクリア
        container.innerHTML = '';

        // 新しいブロッククォートを作成
        const blockquote = document.createElement('blockquote');
        blockquote.className = 'twitter-tweet';
        blockquote.setAttribute('data-theme', theme);

        const link = document.createElement('a');
        link.href = url;
        blockquote.appendChild(link);

        container.appendChild(blockquote);

        // ウィジェットを再読み込み
        if (window.twttr && window.twttr.widgets) {
            window.twttr.widgets.load(container)
                .then(() => log('Tweet widget loaded successfully'))
                .catch(err => log('Error loading tweet widget:', err));
        }
    }

    // 全てのツイートを再構築する関数
    function recreateAllTweets() {
        log('Recreating all tweets');
        document.querySelectorAll('.x-twitter-embed').forEach(container => {
            recreateTweet(container);
        });
    }

    // 遅延実行用のユーティリティ関数
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Twitter ウィジェットを初期化する関数
    function initializeWidget() {
        log('Initializing Twitter widget');

        if (!window.twttr) {
            log('Loading Twitter script');
            const script = document.createElement('script');
            script.src = 'https://platform.twitter.com/widgets.js';
            script.async = true;
            script.onload = () => {
                log('Twitter script loaded');
                setTimeout(recreateAllTweets, 500);
            };
            document.head.appendChild(script);
        } else {
            setTimeout(recreateAllTweets, 500);
        }
    }

    // Material for MkDocs のカラースキーム変更を監視する
    function setupColorSchemeObserver() {
        log('Setting up color scheme observer');

        // 変更検知をデバウンス
        const debouncedRecreate = debounce(recreateAllTweets, 100);

        // HTML要素のdata-md-color-scheme属性変更を監視
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-md-color-scheme') {
                    log('Color scheme mutation detected');
                    debouncedRecreate();
                }
            });
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-md-color-scheme']
        });

        // body要素も監視
        observer.observe(document.body, {
            attributes: true,
            attributeFilter: ['data-md-color-scheme']
        });

        // パレットの変更も監視
        const palette = document.querySelector('[data-md-component="palette"]');
        if (palette) {
            palette.addEventListener('change', () => {
                log('Palette change detected');
                debouncedRecreate();
            });
        }
    }

    // 初期化
    function initialize() {
        log('Starting initialization');

        if (document.readyState === 'loading') {
            log('Document still loading, waiting for DOMContentLoaded');
            document.addEventListener('DOMContentLoaded', () => {
                setupColorSchemeObserver();
                setTimeout(initializeWidget, 1000);
            });
            return;
        }

        setupColorSchemeObserver();
        setTimeout(initializeWidget, 1000);
    }

    // スクリプトの実行開始
    log('Script loaded');
    initialize();
})();
