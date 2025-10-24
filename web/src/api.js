// web/src/api.js
import axios from "axios";

// You can change this if backend runs elsewhere
const API_BASE = "http://localhost:8000";

export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await axios.post(`${API_BASE}/upload/faq`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data;
}

export async function askQuestion(question) {
  const res = await axios.post(`${API_BASE}/chat`, { question });
  return res.data;
}
