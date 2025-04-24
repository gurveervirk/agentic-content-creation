
const handleReset = async () => {
  setLoading(true);
  try {
    const res = await fetch(`${API_BASE}/reset`, { method: "POST" });
    if (!res.ok) throw new Error("Network error");
    const data = await res.json();
    setMessages([]);
    toast({
      title: "Chat reset",
      description: data?.message || "Workflow reset successfully.",
      duration: 1500  // Shortened toast duration
    });
  } catch {
    toast({
      title: "Failed to reset chat",
      variant: "destructive",
      duration: 1500
    });
  }
  setLoading(false);
};
