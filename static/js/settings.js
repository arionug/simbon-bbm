/* =========================================================
   SIMBON BBM - Logika halaman Pengaturan
========================================================= */

// ---------------------------------------------------------
// Toast Notifikasi (sama seperti dashboard.js)
// ---------------------------------------------------------
function showToast(message, type = "info", duration = 3000) {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("hide");
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

function formatRibuan(angka) {
  const numOnly = String(angka).replace(/[^0-9]/g, "");
  if (!numOnly) return "";
  return parseInt(numOnly, 10).toLocaleString("id-ID");
}

function getRawNumber(str) {
  return String(str).replace(/[^0-9]/g, "");
}

function reloadAfter(ms = 600) {
  setTimeout(() => window.location.reload(), ms);
}

async function callApi(url, method, body) {
  try {
    const res = await fetch(url, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
    return await res.json();
  } catch (err) {
    return { success: false, message: "Gagal menghubungi server." };
  }
}

// ---------------------------------------------------------
// Harga BBM
// ---------------------------------------------------------
const tbodyPrices = document.getElementById("tbody-bbm-prices");
const formAddPrice = document.getElementById("form-add-price");
const newHargaBbmInput = document.getElementById("new-harga-bbm");

if (tbodyPrices) {
  tbodyPrices.querySelectorAll(".input-harga").forEach((input) => {
    input.value = formatRibuan(input.value);
    input.addEventListener("input", () => {
      input.value = formatRibuan(input.value);
    });
  });

  tbodyPrices.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const row = btn.closest("tr");
    const id = row.dataset.id;

    if (btn.dataset.action === "save-price") {
      const jenis = row.querySelector("td").textContent.trim();
      const harga = getRawNumber(row.querySelector(".input-harga").value);
      if (!harga) {
        showToast("Harga tidak boleh kosong.", "error");
        return;
      }
      const res = await callApi("/api/bbm-prices", "POST", { jenis_bbm: jenis, harga });
      showToast(res.message || (res.success ? "Berhasil disimpan." : "Gagal menyimpan."), res.success ? "success" : "error");
    }

    if (btn.dataset.action === "delete-price") {
      if (!confirm("Hapus jenis BBM ini? Kendaraan yang sudah memakai jenis ini tidak otomatis berubah.")) return;
      const res = await callApi(`/api/bbm-prices/${id}`, "DELETE");
      if (res.success) {
        showToast(res.message, "success");
        reloadAfter();
      } else {
        showToast(res.message || "Gagal menghapus jenis BBM.", "error");
      }
    }
  });
}

if (formAddPrice) {
  newHargaBbmInput.addEventListener("input", () => {
    newHargaBbmInput.value = formatRibuan(newHargaBbmInput.value);
  });

  formAddPrice.addEventListener("submit", async (e) => {
    e.preventDefault();
    const jenis = document.getElementById("new-jenis-bbm").value.trim();
    const harga = getRawNumber(newHargaBbmInput.value);
    if (!jenis || !harga) {
      showToast("Lengkapi nama jenis BBM dan harganya.", "error");
      return;
    }
    const res = await callApi("/api/bbm-prices", "POST", { jenis_bbm: jenis, harga });
    if (res.success) {
      showToast(res.message, "success");
      reloadAfter();
    } else {
      showToast(res.message || "Gagal menambah jenis BBM.", "error");
    }
  });
}

// ---------------------------------------------------------
// Kendaraan & Driver
// ---------------------------------------------------------
const tbodyVehicles = document.getElementById("tbody-vehicles");
const formAddVehicle = document.getElementById("form-add-vehicle");

if (tbodyVehicles) {
  tbodyVehicles.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const row = btn.closest("tr");
    const id = row.dataset.id;

    if (btn.dataset.action === "save-vehicle") {
      const nomor_polisi = row.querySelector(".input-nopol").value.trim().toUpperCase();
      const driver = row.querySelector(".input-driver").value;
      const jenis_bbm = row.querySelector(".input-jenis-bbm").value;
      if (!nomor_polisi) {
        showToast("Nomor polisi tidak boleh kosong.", "error");
        return;
      }
      const res = await callApi(`/api/vehicles/${id}`, "PUT", { nomor_polisi, driver, jenis_bbm });
      showToast(res.message || (res.success ? "Berhasil disimpan." : "Gagal menyimpan."), res.success ? "success" : "error");
    }

    if (btn.dataset.action === "delete-vehicle") {
      if (!confirm("Hapus kendaraan ini dari daftar?")) return;
      const res = await callApi(`/api/vehicles/${id}`, "DELETE");
      if (res.success) {
        row.remove();
        showToast(res.message, "success");
      } else {
        showToast(res.message || "Gagal menghapus kendaraan.", "error");
      }
    }
  });
}

if (formAddVehicle) {
  formAddVehicle.addEventListener("submit", async (e) => {
    e.preventDefault();
    const nomor_polisi = document.getElementById("new-nopol").value.trim().toUpperCase();
    const driver = document.getElementById("new-vehicle-driver").value;
    const jenis_bbm = document.getElementById("new-vehicle-jenis-bbm").value;
    if (!nomor_polisi) {
      showToast("Nomor polisi tidak boleh kosong.", "error");
      return;
    }
    const res = await callApi("/api/vehicles", "POST", { nomor_polisi, driver, jenis_bbm });
    if (res.success) {
      showToast(res.message, "success");
      reloadAfter();
    } else {
      showToast(res.message || "Gagal menambah kendaraan.", "error");
    }
  });
}

// ---------------------------------------------------------
// Driver
// ---------------------------------------------------------
const chipListDrivers = document.getElementById("chip-list-drivers");
const formAddDriver = document.getElementById("form-add-driver");

if (chipListDrivers) {
  chipListDrivers.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action='delete-driver']");
    if (!btn) return;
    const chip = btn.closest(".chip");
    const nama = chip.textContent.replace("×", "").trim();
    if (!confirm(`Hapus driver "${nama}"?`)) return;
    const res = await callApi(`/api/drivers/${chip.dataset.id}`, "DELETE");
    if (res.success) {
      showToast(res.message, "success");
      reloadAfter();
    } else {
      showToast(res.message || "Gagal menghapus driver.", "error");
    }
  });
}

if (formAddDriver) {
  formAddDriver.addEventListener("submit", async (e) => {
    e.preventDefault();
    const nama = document.getElementById("new-driver-nama").value.trim();
    if (!nama) {
      showToast("Nama driver tidak boleh kosong.", "error");
      return;
    }
    const res = await callApi("/api/drivers", "POST", { nama });
    if (res.success) {
      showToast(res.message, "success");
      reloadAfter();
    } else {
      showToast(res.message || "Gagal menambah driver.", "error");
    }
  });
}
