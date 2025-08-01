import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import axios from "axios";
import { useAuth } from "./AuthContext";

const SavedItemsContext = createContext();

export const useSavedItems = () => {
  const context = useContext(SavedItemsContext);
  if (!context) {
    throw new Error("useSavedItems must be used within a SavedItemsProvider");
  }
  return context;
};

export const SavedItemsProvider = ({ children }) => {
  const [savedItems, setSavedItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated, token } = useAuth();

  // Load saved items when user is authenticated and token is available
  useEffect(() => {
    if (isAuthenticated && token) {
      loadSavedItems();
    } else {
      setSavedItems([]);
    }
  }, [isAuthenticated, token]);

  const loadSavedItems = useCallback(async () => {
    if (!isAuthenticated || !token) return;

    setLoading(true);
    try {
      const response = await axios.get("http://localhost:8000/api/saved/list");
      setSavedItems(response.data);
      console.log(
        `✅ Loaded ${response.data.length} saved items (${
          response.data.filter((item) => item.favorited).length
        } favorited)`
      );
    } catch (error) {
      console.error("❌ Failed to load saved items:", error);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, token]);

  const saveItem = async (item) => {
    if (!isAuthenticated || !token)
      return { success: false, error: "Not authenticated" };

    try {
      // Handle both the old format and the new format from App.jsx
      const requestData = {
        item_id: item.item_id || item.entity_id || item.id,
        item_name: item.item_name || item.name || item.title,
        item_type: (item.item_type || item.type || "book").replace(
          "urn:entity:",
          ""
        ),
        item_image:
          item.item_image ||
          item.image_url ||
          item.cover_image ||
          (item.properties &&
            item.properties.image &&
            item.properties.image.url) ||
          "",
        item_description:
          item.item_description ||
          item.description ||
          item.short_description ||
          "",
        favorited: item.favorited || false,
      };

      console.log(
        "📤 Saving item:",
        requestData.item_name,
        "(favorited:",
        requestData.favorited + ")"
      );

      const response = await axios.post(
        "http://localhost:8000/api/saved/save",
        requestData
      );

      // Check if item is already in the list
      const existingItem = savedItems.find(
        (saved) => saved.item_id === requestData.item_id
      );
      if (!existingItem) {
        setSavedItems((prev) => [...prev, response.data]);
        console.log("➕ Added new item to local state");
      } else {
        // Update the existing item in local state
        setSavedItems((prev) =>
          prev.map((saved) =>
            saved.item_id === requestData.item_id ? response.data : saved
          )
        );
        console.log("🔄 Updated existing item in local state");
      }

      return { success: true };
    } catch (error) {
      console.error("❌ Failed to save item:", error);
      console.error("   Error details:", error.response?.data);
      return {
        success: false,
        error: error.response?.data?.detail || "Failed to save item",
      };
    }
  };

  const removeItem = async (itemId) => {
    if (!isAuthenticated) return { success: false, error: "Not authenticated" };

    try {
      console.log("Removing item with ID:", itemId);
      await axios.delete(`http://localhost:8000/api/saved/remove/${itemId}`);
      setSavedItems((prev) => prev.filter((item) => item.item_id !== itemId));
      console.log("Item removed successfully");
      return { success: true };
    } catch (error) {
      console.error("Failed to remove item:", error);
      return {
        success: false,
        error: error.response?.data?.detail || "Failed to remove item",
      };
    }
  };

  const checkIfSaved = async (itemId) => {
    if (!isAuthenticated) return false;

    try {
      const response = await axios.get(
        `http://localhost:8000/api/saved/check/${itemId}`
      );
      return response.data.is_saved;
    } catch (error) {
      console.error("Failed to check if item is saved:", error);
      return false;
    }
  };

  const isItemSaved = (itemId) => {
    return savedItems.some((item) => item.item_id === itemId);
  };

  const value = {
    savedItems,
    loading,
    saveItem,
    removeItem,
    checkIfSaved,
    isItemSaved,
    loadSavedItems,
  };

  return (
    <SavedItemsContext.Provider value={value}>
      {children}
    </SavedItemsContext.Provider>
  );
};
