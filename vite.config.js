import {resolve} from "path";

export default {
  plugins: [],
  root: resolve("./digiplan/static/src"),
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
    outDir: resolve("./digiplan/static/dist"),
    assetsDir: "",
    manifest: true,
    emptyOutDir: true,
    target: "es2015",
    rollupOptions: {
      input: {
        main: resolve("./digiplan/static/src/js/main.js"),
      },
      output: {
        chunkFileNames: undefined,
      },
    },
  },
};
