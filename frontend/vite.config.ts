import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// В режиме разработки запросы к /api проксируются на backend.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  test: {
    // Тесты работают с компонентами и localStorage — нужна DOM-среда.
    environment: 'jsdom',
    include: ['src/**/*.test.{ts,tsx}'],
    // Глобальных переменных нет: describe/it/expect импортируются явно,
    // чтобы проверки типов не расходились с исполнением.
    globals: false,
    restoreMocks: true,
  },
});
