import {resolve} from "path";

export default {
  plugins: [],
  root: resolve("./digiplan/static/"),
  base: "/static/",
  server: {
    host: "localhost",
    port: 3000,
    open: false,
    watch: {
      usePolling: true,
      disableGlobbing: false,
    },
  },
  resolve: {
    extensions: [".js", ".json"],
  },
  build: {
    outDir: resolve("./dist/"),
    assetsDir: "",
    manifest: true,
    emptyOutDir: true,
    target: "es2015",
    rollupOptions: {
      input: {
        popup: resolve("./digiplan/static/js/popup.js"),
      },
      output: {
        chunkFileNames: undefined,
      },
    },
  },
};
