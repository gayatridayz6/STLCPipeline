tecimport { defineConfig } from "vite";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { cartApiMock } from "./server/cartApiMock.js";

export default defineConfig({
  plugins: [react(), cartApiMock()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/setupTests.js"],
    globals: false,
    coverage: {
      provider: "v8",
      include: ["src/**/*.{js,jsx}"],
      exclude: ["src/**/*.test.jsx", "src/setupTests.js", "src/main.jsx"],
      reporter: ["text", "json-summary"],
      reportsDirectory: "coverage",
    },
  },
});
