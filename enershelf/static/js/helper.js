// Global Helper Functions


function logMessage(msg) {
  if (store.cold.debugMode) {
    let caller = arguments.callee.caller;
    if (typeof caller === "function") {
      caller = caller.toString().substr("function ".length);
      caller = caller.substr(0, caller.indexOf("("));
    }
    const whatCalledWho = `${msg} triggered\n${caller}`;
    console.log(whatCalledWho);
    return whatCalledWho;
  }
}
