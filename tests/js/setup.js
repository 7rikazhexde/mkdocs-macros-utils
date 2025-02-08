// MutationObserverのモック
global.MutationObserver = class {
    constructor(callback) {
      this.callback = callback;
    }
    disconnect() {}
    observe(element, initObject) {
      // 監視開始時に即座に変更を通知
      this.callback([{
        type: 'attributes',
        attributeName: 'data-md-color-scheme',
        target: element
      }]);
    }
  };

  // documentのメソッドを拡張
  Object.defineProperty(document, 'dispatchEvent', {
    value: function(event) {
      // イベントハンドラーを実行
      const handler = this[`on${event.type}`];
      if (typeof handler === 'function') {
        handler.call(this, event);
      }
    },
    writable: true
  });

  // グローバルイベントのサポート
  if (!global.Event) {
    global.Event = class Event {
      constructor(type) {
        this.type = type;
      }
    };
  }

  // タイマー関連のモック
  jest.useFakeTimers();

  // グローバルオブジェクトの設定
  Object.defineProperty(global, 'requestAnimationFrame', {
    value: (callback) => setTimeout(callback, 0)
  });

  Object.defineProperty(global, 'cancelAnimationFrame', {
    value: (id) => clearTimeout(id)
  });

  // コンソールメソッドのモック
  ['log', 'error', 'warn', 'info', 'debug'].forEach(method => {
    global.console[method] = jest.fn();
  });

  // エラーハンドリング
  process.on('unhandledRejection', (error) => {
    console.error('Unhandled Rejection:', error);
  });
