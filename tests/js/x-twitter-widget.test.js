/**
 * Test suite for X-Twitter-Widget module
 * Covers various scenarios of widget initialization, color scheme detection,
 * and tweet embedding functionality
 */
describe("X-Twitter-Widget", () => {
  /** Store the original console.log method to restore after tests */
  let originalConsoleLog;

  /**
   * Initialize the module for testing
   * Loads the module, dispatches DOMContentLoaded event,
   * and advances timers to simulate initialization process
   */
  function initializeModule() {
    jest.isolateModules(() => {
      require("mkdocs_macros_utils/static/js/x-twitter-widget");
    });
    document.dispatchEvent(new Event("DOMContentLoaded"));
    jest.advanceTimersByTime(1000);
    jest.advanceTimersByTime(500);
  }

  /**
   * Setup routine before each test
   * Resets modules, mocks console.log, prepares test DOM,
   * and sets up global objects for consistent testing environment
   */
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

  /**
   * Cleanup routine after each test
   * Restores original console.log, clears DOM and mocks,
   * resets color scheme attributes
   */
  afterEach(() => {
    console.log = originalConsoleLog;
    document.body.innerHTML = "";
    jest.clearAllMocks();
    jest.clearAllTimers();
    document.documentElement.removeAttribute("data-md-color-scheme");
    document.body.removeAttribute("data-md-color-scheme");
  });

  /**
   * Test suite for color scheme detection functionality
   * Verifies different scenarios of theme detection
   */
  describe("getColorScheme", () => {
    /** Test default light theme when no theme is explicitly set */
    test('returns "light" when no theme is set', () => {
      initializeModule();

      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote).toBeTruthy();
      expect(blockquote.getAttribute("data-theme")).toBe("light");
    });

    /** Test dark theme detection when slate palette is selected */
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

    /** Test light theme for non-slate color schemes */
    test("returns light theme for non-slate color scheme", () => {
      document.documentElement.setAttribute("data-md-color-scheme", "default");
      initializeModule();
      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote.getAttribute("data-theme")).toBe("light");
    });

    /** Test handling of null values in palette */
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

    /** Test handling of null localStorage value */
    test("handles null value from localStorage", () => {
      window.localStorage.getItem.mockReturnValue(null);
      initializeModule();
      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote.getAttribute("data-theme")).toBe("light");
    });

    /** Test theme detection from localStorage */
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

    /** Test palette change event handling */
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

    /** Test theme detection from document element attribute */
    test("returns theme from document element data attribute", () => {
      document.documentElement.setAttribute("data-md-color-scheme", "slate");
      console.log.mockClear();
      initializeModule();

      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote).toBeTruthy();
      expect(blockquote.getAttribute("data-theme")).toBe("dark");
    });

    /** Test theme detection from body element attribute */
    test("returns theme from body element data attribute", () => {
      document.body.setAttribute("data-md-color-scheme", "slate");
      console.log.mockClear();
      initializeModule();

      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote).toBeTruthy();
      expect(blockquote.getAttribute("data-theme")).toBe("dark");
    });
  });

  /**
   * Test suite for tweet recreation functionality
   * Verifies correct tweet widget creation and error handling
   */
  describe("recreateTweet", () => {
    /** Test blockquote creation with correct attributes */
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

    /** Test error handling for tweet widget loading */
    test("handles tweet widget load error", () => {
      global.twttr.widgets.load = jest
        .fn()
        .mockRejectedValue(new Error("Load failed"));

      console.error = jest.fn();
      initializeModule();
      expect(global.twttr.widgets.load).toHaveBeenCalled();
    });
  });

  /**
   * Test suite for Twitter script loading scenarios
   * Covers various cases of script and widget initialization
   */
  describe("Twitter Script Loading", () => {
    /** Test script loading when Twitter widget is not already present */
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

    /** Test error handling during script loading */
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

    /** Test handling of missing Twitter widgets object */
    test("handles missing Twitter widgets object", () => {
      global.twttr = {}; // widgetsプロパティなし
      initializeModule();

      const container = document.querySelector(".x-twitter-embed");
      const blockquote = container.querySelector("blockquote");
      expect(blockquote).toBeTruthy();
      expect(blockquote.className).toBe("twitter-tweet");
    });

    /** Test widget loading when twttr is undefined */
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
          load: jest.fn().mockResolvedValue(true),
        },
      };
      script.onload();

      jest.advanceTimersByTime(500);
      expect(global.twttr.widgets.load).toHaveBeenCalled();

      appendChildSpy.mockRestore();
    });
  });

  /**
   * Test suite for widget initialization process
   * Verifies correct handling of document loading state
   */
  describe("initialization", () => {
    /** Prepare document for initialization tests */
    beforeEach(() => {
      Object.defineProperty(document, "readyState", {
        value: "loading",
        writable: true,
      });
      jest.clearAllTimers();
      console.log.mockClear();
    });

    /** Test handling of document in loading state */
    test("handles document in loading state", () => {
      const addEventListenerSpy = jest.spyOn(document, "addEventListener");

      jest.isolateModules(() => {
        require("mkdocs_macros_utils/static/js/x-twitter-widget");
      });

      expect(addEventListenerSpy).toHaveBeenCalledWith(
        "DOMContentLoaded",
        expect.any(Function)
      );

      const eventListener = addEventListenerSpy.mock.calls[0][1];
      eventListener();

      expect(console.log).toHaveBeenCalledWith(
        "[X-Twitter-Widget] Setting up color scheme observer"
      );

      addEventListenerSpy.mockRestore();
    });
  });

  /**
   * Test suite for debugging functionality
   * Verifies logging and debug mode behavior
   */
  describe("debug", () => {
    /** Test logging of initialization steps */
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
