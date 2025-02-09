/**
 * Mock implementation of MutationObserver for testing purposes.
 * Simulates immediate attribute change notification during observation.
 */
global.MutationObserver = class {
  /**
   * Creates a mock MutationObserver instance.
   * @param {Function} callback - The callback function to be called on mutations
   */
  constructor(callback) {
    this.callback = callback;
  }

  /**
   * Disconnects the observer (no-op in this mock).
   */
  disconnect() {}

  /**
   * Starts observing the element and immediately triggers a mock mutation.
   * @param {Element} element - The element to observe
   * @param {Object} initObject - Initialization options for observation
   */
  observe(element, initObject) {
    // Immediately notify of a change when observation starts
    this.callback([
      {
        type: "attributes",
        attributeName: "data-md-color-scheme",
        target: element,
      },
    ]);
  }
};

/**
 * Extend document object with a custom dispatchEvent method for testing.
 * Allows simulating event dispatching and handler execution.
 */
Object.defineProperty(document, "dispatchEvent", {
  /**
   * Custom event dispatching method that directly calls the event handler.
   * @param {Event} event - The event to dispatch
   * @returns {void}
   */
  value: function (event) {
    // Execute event handler if defined
    const handler = this[`on${event.type}`];
    if (typeof handler === "function") {
      handler.call(this, event);
    }
  },
  writable: true,
});

/**
 * Provide a basic Event implementation if not already available.
 * This ensures compatibility across different testing environments.
 */
if (!global.Event) {
  /**
   * Minimal Event class implementation.
   */
  global.Event = class Event {
    /**
     * Create a new Event instance.
     * @param {string} type - The type of event
     */
    constructor(type) {
      this.type = type;
    }
  };
}

/**
 * Set up fake timers for Jest testing.
 * This allows controlling and manipulating time-based operations in tests.
 */
jest.useFakeTimers();

/**
 * Mock requestAnimationFrame using setTimeout.
 * Provides a simple implementation for testing environments.
 */
Object.defineProperty(global, "requestAnimationFrame", {
  /**
   * Simulate requestAnimationFrame by using setTimeout with zero delay.
   * @param {Function} callback - The callback to be executed
   * @returns {number} Timeout ID
   */
  value: (callback) => setTimeout(callback, 0),
});

/**
 * Mock cancelAnimationFrame using clearTimeout.
 * Ensures compatibility with requestAnimationFrame mock.
 */
Object.defineProperty(global, "cancelAnimationFrame", {
  /**
   * Cancel a previously scheduled animation frame.
   * @param {number} id - The ID of the animation frame to cancel
   */
  value: (id) => clearTimeout(id),
});

/**
 * Mock console methods for consistent testing behavior.
 * Replaces standard console methods with Jest mock functions.
 */
["log", "error", "warn", "info", "debug"].forEach((method) => {
  global.console[method] = jest.fn();
});

/**
 * Handle unhandled promise rejections during testing.
 * Logs any unhandled rejections to aid in debugging.
 */
process.on("unhandledRejection", (error) => {
  console.error("Unhandled Rejection:", error);
});
