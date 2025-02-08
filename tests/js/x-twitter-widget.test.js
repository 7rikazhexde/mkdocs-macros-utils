describe("X-Twitter-Widget", () => {
  let originalConsoleLog;

  function initializeModule() {
    jest.isolateModules(() => {
      require("mkdocs_macros_utils/static/js/x-twitter-widget");
    });
    document.dispatchEvent(new Event("DOMContentLoaded"));
    jest.advanceTimersByTime(1000);
    jest.advanceTimersByTime(500);
  }

  beforeEach(() => {
    jest.resetModules();

    originalConsoleLog = console.log;
    console.log = jest.fn();

    document.body.innerHTML = `
      <div class="x-twitter-embed" data-url="https://twitter.com/example/status/123456789">
      </div>
    `;

    global.twttr = {
      widgets: {
        load: jest.fn().mockResolvedValue(true),
      },
    };

    Object.defineProperty(window, "localStorage", {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });

    Object.defineProperty(document, "readyState", {
      value: "complete",
      writable: true,
    });

    jest.useFakeTimers();
  });

  afterEach(() => {
    console.log = originalConsoleLog;
    document.body.innerHTML = "";
    jest.clearAllMocks();
    jest.clearAllTimers();
  });

  describe("getColorScheme", () => {
    test('returns "light" when no theme is set', () => {
      initializeModule();

      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote).toBeTruthy();
      expect(blockquote.getAttribute("data-theme")).toBe("light");
    });

    test("returns theme from palette when slate is set", () => {
      document.body.innerHTML = `
        <div class="x-twitter-embed" data-url="https://twitter.com/example/status/123456789"></div>
        <form class="md-header__option" data-md-component="palette">
          <input
            class="md-option"
            type="radio"
            name="__palette"
            id="__palette_1"
            data-md-color-media="(prefers-color-scheme: dark)"
            data-md-color-scheme="slate"
            data-md-color-primary="teal"
            data-md-color-accent="teal"
            checked
          >
        </form>
      `;

      console.log.mockClear();
      initializeModule();

      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote).toBeTruthy();
      expect(blockquote.getAttribute("data-theme")).toBe("dark");
    });

    test("returns theme from localStorage", () => {
      // Reset color scheme selectors
      document.documentElement.removeAttribute("data-md-color-scheme");
      document.body.removeAttribute("data-md-color-scheme");

      // Mock localStorage to return slate
      window.localStorage.getItem.mockReturnValue("slate");

      initializeModule();

      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote).toBeTruthy();
      expect(blockquote.getAttribute("data-theme")).toBe("dark");
    });

    test("handles palette change event", () => {
      document.body.innerHTML = `
        <div class="x-twitter-embed" data-url="https://twitter.com/example/status/123456789"></div>
        <form class="md-header__option" data-md-component="palette">
          <input
            class="md-option"
            type="radio"
            name="__palette"
            id="__palette_1"
            data-md-color-media="(prefers-color-scheme: dark)"
            data-md-color-scheme="slate"
            data-md-color-primary="teal"
            data-md-color-accent="teal"
          >
          <input
            class="md-option"
            type="radio"
            name="__palette"
            id="__palette_2"
            data-md-color-media="(prefers-color-scheme: light)"
            data-md-color-scheme="default"
            data-md-color-primary="teal"
            data-md-color-accent="teal"
            checked
          >
        </form>
      `;

      initializeModule();

      // Simulate palette change
      const palette = document.querySelector('[data-md-component="palette"]');
      const slateInput = document.getElementById("__palette_1");
      slateInput.checked = true;
      palette.dispatchEvent(new Event("change"));

      // Give time for debounce
      jest.advanceTimersByTime(200);

      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote).toBeTruthy();
      expect(blockquote.getAttribute("data-theme")).toBe("dark");
    });
  });

  describe("recreateTweet", () => {
    test("creates blockquote with correct attributes", () => {
      initializeModule();

      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");

      expect(blockquote).toBeTruthy();
      expect(blockquote.className).toBe("twitter-tweet");
      expect(blockquote.querySelector("a").href).toBe(
        "https://twitter.com/example/status/123456789"
      );
      expect(global.twttr.widgets.load).toHaveBeenCalled();
    });

    test("handles tweet widget load error", () => {
      // モックしたtwttrのloadメソッドをrejectに変更
      global.twttr.widgets.load = jest
        .fn()
        .mockRejectedValue(new Error("Load failed"));

      // デバッグログのモック
      console.error = jest.fn();

      initializeModule();

      // エラーハンドリングを確認
      expect(global.twttr.widgets.load).toHaveBeenCalled();
    });
  });

  describe("Twitter Script Loading", () => {
    test("handles Twitter script loading when not already loaded", () => {
      // twttrオブジェクトを削除
      delete global.twttr;

      // スクリプト追加のスパイ
      const appendChildSpy = jest.spyOn(document.head, "appendChild");

      // 初期化
      initializeModule();

      // スクリプト追加を確認
      const scriptElements = appendChildSpy.mock.calls.filter(
        (call) => call[0].tagName === "SCRIPT"
      );
      expect(scriptElements.length).toBeGreaterThan(0);

      // スクリプトのonload関数をシミュレート
      const script = scriptElements[0][0];
      if (script.onload) {
        script.onload();
      }

      appendChildSpy.mockRestore();
    });

    test("handles script load failure", () => {
      // twttrオブジェクトを削除
      delete global.twttr;

      // スクリプト追加のスパイ
      const appendChildSpy = jest.spyOn(document.head, "appendChild");

      // コンソールエラーのモック
      console.error = jest.fn();

      // 初期化
      initializeModule();

      // スクリプト追加を確認
      const scriptElements = appendChildSpy.mock.calls.filter(
        (call) => call[0].tagName === "SCRIPT"
      );
      expect(scriptElements.length).toBeGreaterThan(0);

      // スクリプトのonerror関数をシミュレート
      const script = scriptElements[0][0];
      if (script.onerror) {
        script.onerror(new Error("Script load failed"));
      }

      appendChildSpy.mockRestore();
    });
  });

  describe("debug", () => {
    test("logs initialization steps", () => {
      initializeModule();

      const allLogs = console.log.mock.calls;
      const initLogs = allLogs.filter((log) =>
        log.some((arg) => String(arg).includes("[X-Twitter-Widget]"))
      );

      expect(initLogs.length).toBeGreaterThan(0);
    });
  });
});
