export function createQueryCache(ttlMs = 0) {
  const ttl = Number(ttlMs);
  if (!Number.isFinite(ttl) || ttl <= 0) {
    return {
      get: () => null,
      set: () => {},
      clear: () => {},
    };
  }

  const store = new Map();

  return {
    get(key) {
      const entry = store.get(key);
      if (!entry) {
        return null;
      }
      if (Date.now() - entry.timestamp > ttl) {
        store.delete(key);
        return null;
      }
      return entry.value;
    },
    set(key, value) {
      store.set(key, { value, timestamp: Date.now() });
    },
    clear() {
      store.clear();
    },
  };
}
