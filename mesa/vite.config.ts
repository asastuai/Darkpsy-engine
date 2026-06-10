import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// COOP only for now. COEP require-corp is deferred until we actually need
// SharedArrayBuffer/wasm (F3 metering) — it can break same-origin audio fetches
// in some setups, so we don't pay that risk before it buys us anything.
const headers = { "Cross-Origin-Opener-Policy": "same-origin" };

export default defineConfig({
  plugins: [react()],
  server: { headers },
  preview: { headers },
});
