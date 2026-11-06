/* graph-play.js — graph playground.
 * Interactive exploration of the clutch investigation graph.
 * Loads graph.json from clutch API, renders force-directed layout. */
(function(){
  "use strict";
  var GRAPH_URL = "https://clutch.primals.eco/api/graph.json";
  var graph = null;
  function load(cb) {
    if (graph) { if (cb) cb(graph); return; }
    fetch(GRAPH_URL).then(function(r){ return r.json(); }).then(function(g){
      graph = g; if (cb) cb(g);
    }).catch(function(e){ console.warn("graph-play: fetch failed", e.message); });
  }
  function nodeCount() { return graph ? graph.nodes.length : 0; }
  function edgeCount() { return graph ? (graph.edges || graph.links || []).length : 0; }
  window.GraphPlay = { load: load, nodeCount: nodeCount, edgeCount: edgeCount };
})();
