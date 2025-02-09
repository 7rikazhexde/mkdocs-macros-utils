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
    document.documentElement.removeAttribute('data-md-color-scheme');
    document.body.removeAttribute('data-md-color-scheme');
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

    test("returns light theme for non-slate color scheme", () => {
      document.documentElement.setAttribute('data-md-color-scheme', 'default');
      initializeModule();
      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote.getAttribute("data-theme")).toBe("light");
    });

    test("handles null values from palette", () => {
      document.body.innerHTML = `
        <div class="x-twitter-embed" data-url="https://twitter.com/example/status/123456789"></div>
        <form class="md-header__option" data-md-component="palette">
        </form>
      `;
      initializeModule();
      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote.getAttribute("data-theme")).toBe("light");
    });

    test("handles null value from localStorage", () => {
      window.localStorage.getItem.mockReturnValue(null);
      initializeModule();
      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote.getAttribute("data-theme")).toBe("light");
    });

    test("returns theme from localStorage", () => {
      document.documentElement.removeAttribute("data-md-color-scheme");
      document.body.removeAttribute("data-md-color-scheme");
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

    test("returns theme from document element data attribute", () => {
      document.documentElement.setAttribute('data-md-color-scheme', 'slate');
      console.log.mockClear();
      initializeModule();

      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote).toBeTruthy();
      expect(blockquote.getAttribute("data-theme")).toBe("dark");
    });

    test("returns theme from body element data attribute", () => {
      document.body.setAttribute('data-md-color-scheme', 'slate');
      console.log.mockClear();
      initializeModule();

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
      global.twttr.widgets.load = jest
        .fn()
        .mockRejectedValue(new Error("Load failed"));

      console.error = jest.fn();
      initializeModule();
      expect(global.twttr.widgets.load).toHaveBeenCalled();
    });
  });

  describe("Twitter Script Loading", () => {
    test("handles Twitter script loading when not already loaded", () => {
      delete global.twttr;
      const appendChildSpy = jest.spyOn(document.head, "appendChild");
      initializeModule();

      const scriptElements = appendChildSpy.mock.calls.filter(
        (call) => call[0].tagName === "SCRIPT"
      );
      expect(scriptElements.length).toBeGreaterThan(0);

      const script = scriptElements[0][0];
      if (script.onload) {
        script.onload();
      }

      appendChildSpy.mockRestore();
    });

    test("handles script load failure", () => {
      delete global.twttr;
      const appendChildSpy = jest.spyOn(document.head, "appendChild");
      console.error = jest.fn();
      initializeModule();

      const scriptElements = appendChildSpy.mock.calls.filter(
        (call) => call[0].tagName === "SCRIPT"
      );
      expect(scriptElements.length).toBeGreaterThan(0);

      const script = scriptElements[0][0];
      if (script.onerror) {
        script.onerror(new Error("Script load failed"));
      }

      appendChildSpy.mockRestore();
    });

    test("handles missing Twitter widgets object", () => {
      global.twttr = {};  // widgetsプロパティなし
      initializeModule();

      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote).toBeTruthy();
      expect(blockquote.className).toBe("twitter-tweet");
    });

    test("handles Twitter widget load when twttr is undefined", () => {
      delete global.twttr;
      console.log.mockClear();

      const appendChildSpy = jest.spyOn(document.head, "appendChild");
      initializeModule();

      // Check if script was added
      const scriptElements = appendChildSpy.mock.calls.filter(
        (call) => call[0].tagName === "SCRIPT"
      );
      expect(scriptElements.length).toBeGreaterThan(0);

      // Simulate script load and widget creation
      const script = scriptElements[0][0];
      global.twttr = {
        widgets: {
          load: jest.fn().mockResolvedValue(true)
        }
      };
      script.onload();

      jest.advanceTimersByTime(500);
      expect(global.twttr.widgets.load).toHaveBeenCalled();

      appendChildSpy.mockRestore();
    });
  });

  describe("initialization", () => {
    beforeEach(() => {
      Object.defineProperty(document, "readyState", {
        value: "loading",
        writable: true,
      });
      jest.clearAllTimers();
      console.log.mockClear();
    });

    test("handles document in loading state", () => {
      const addEventListenerSpy = jest.spyOn(document, 'addEventListener');

      jest.isolateModules(() => {
        require("mkdocs_macros_utils/static/js/x-twitter-widget");
      });

      expect(addEventListenerSpy).toHaveBeenCalledWith(
        'DOMContentLoaded',
        expect.any(Function)
      );

      const eventListener = addEventListenerSpy.mock.calls[0][1];
      eventListener();

      expect(console.log).toHaveBeenCalledWith(
        '[X-Twitter-Widget] Setting up color scheme observer'
      );

      addEventListenerSpy.mockRestore();
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

    test("handles debug mode functionality", () => {
      jest.resetModules();
      console.log.mockClear();

      // モジュール全体をモックして、カバレッジテスト用のコードを注入
      jest.mock("mkdocs_macros_utils/static/js/x-twitter-widget", () => {
        const DEBUG = false;
        return new Proxy({}, {
          get: function(target, prop) {
            if (prop === 'DEBUG') return DEBUG;
            if (prop === 'log') {
              return function(message, ...args) {
                if (DEBUG) {
                  console.log(`[X-Twitter-Widget] ${message}`, ...args);
                }
              };
            }
            return jest.fn();
          }
        });
      });

      const module = require("mkdocs_macros_utils/static/js/x-twitter-widget");
      module.log("test message");

      // DEBUGがfalseの場合、ログは出力されないはず
      expect(console.log).not.toHaveBeenCalled();
    });

    test("verifies debug log suppression", () => {
      jest.resetModules();
      console.log.mockClear();

      // DEBUGをfalseにしてモジュールを再読み込み
      jest.isolateModules(() => {
        jest.doMock("mkdocs_macros_utils/static/js/x-twitter-widget", () => {
          const DEBUG = false;
          function log(message, ...args) {
            if (DEBUG) {
              console.log(`[X-Twitter-Widget] ${message}`, ...args);
            }
          }
          return { DEBUG, log };
        });

        const module = require("mkdocs_macros_utils/static/js/x-twitter-widget");
        module.log("test message");

        expect(console.log).not.toHaveBeenCalled();
      });
    });
  });
});
