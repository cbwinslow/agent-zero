import { createStore } from "/js/AlpineStore.js";
import * as API from "/js/api.js";
import sleep from "/js/sleep.js";

const model = {
  servers: [],
  filteredServers: [],
  loading: false,
  searchQuery: "",
  sourceFilter: "all", // all, npm, github, docker
  sortBy: "popularity", // popularity, name, date
  selectedServer: null,
  
  async initialize() {
    await this.discoverServers();
  },
  
  async discoverServers(forceRefresh = false) {
    this.loading = true;
    try {
      const resp = await API.callJsonApi("mcp_discover", {
        force_refresh: forceRefresh
      });
      
      if (resp.success) {
        this.servers = resp.servers;
        this.applyFilters();
      } else {
        console.error("Failed to discover servers:", resp.error);
        alert("Failed to discover MCP servers: " + resp.error);
      }
    } catch (error) {
      console.error("Error discovering servers:", error);
      alert("Error discovering MCP servers: " + error.message);
    }
    this.loading = false;
  },
  
  applyFilters() {
    let filtered = [...this.servers];
    
    // Apply source filter
    if (this.sourceFilter !== "all") {
      filtered = filtered.filter(s => s.source === this.sourceFilter);
    }
    
    // Apply search query
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(s => 
        s.name.toLowerCase().includes(query) ||
        (s.description && s.description.toLowerCase().includes(query)) ||
        (s.topics && s.topics.some(t => t.toLowerCase().includes(query)))
      );
    }
    
    // Apply sorting
    if (this.sortBy === "popularity") {
      filtered.sort((a, b) => {
        const aScore = a.stars || a.downloads || a.pulls || 0;
        const bScore = b.stars || b.downloads || b.pulls || 0;
        return bScore - aScore;
      });
    } else if (this.sortBy === "name") {
      filtered.sort((a, b) => a.name.localeCompare(b.name));
    } else if (this.sortBy === "date") {
      filtered.sort((a, b) => {
        const aDate = a.last_updated || "2000-01-01";
        const bDate = b.last_updated || "2000-01-01";
        return bDate.localeCompare(aDate);
      });
    }
    
    this.filteredServers = filtered;
  },
  
  onSearchChange() {
    this.applyFilters();
  },
  
  onSourceFilterChange() {
    this.applyFilters();
  },
  
  onSortChange() {
    this.applyFilters();
  },
  
  async viewServerDetails(server) {
    this.selectedServer = server;
    openModal("settings/mcp/discovery/mcp-server-details.html");
  },
  
  async addServerToConfig(server) {
    try {
      const resp = await API.callJsonApi("mcp_add_from_registry", {
        server_name: server.full_name || server.name,
        enabled: false
      });
      
      if (resp.success) {
        // Copy the configuration to clipboard
        const configJson = JSON.stringify(resp.config, null, 2);
        await navigator.clipboard.writeText(configJson);
        
        alert(`Configuration for "${server.name}" has been copied to clipboard.\n\nPaste it into your MCP Servers configuration and enable it.`);
      } else {
        alert("Failed to generate configuration: " + resp.error);
      }
    } catch (error) {
      console.error("Error adding server:", error);
      alert("Error adding server: " + error.message);
    }
  },
  
  getSourceIcon(source) {
    const icons = {
      npm: "📦",
      github: "🐙",
      docker: "🐳"
    };
    return icons[source] || "📚";
  },
  
  getSourceColor(source) {
    const colors = {
      npm: "#CB3837",
      github: "#181717",
      docker: "#2496ED"
    };
    return colors[source] || "#666";
  },
  
  formatNumber(num) {
    if (!num) return "0";
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toString();
  },
  
  formatDate(dateStr) {
    if (!dateStr) return "Unknown";
    const date = new Date(dateStr);
    return date.toLocaleDateString();
  }
};

const store = createStore("mcpDiscoveryStore", model);

export { store };
