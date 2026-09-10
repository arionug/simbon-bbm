/* =========================================================
   SIMBON BBM - Logika halaman Dashboard / Form Bon BBM
========================================================= */

// ---------------------------------------------------------
// Toast Notifikasi
// ---------------------------------------------------------
function showToast(message, type = "info", duration = 3800) {
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

// ---------------------------------------------------------
// Dropdown searchable Nomor Polisi
// ---------------------------------------------------------
let vehicleList = (window.VEHICLES_DATA || []).map((v) => v.nomor_polisi);
const vehicleMap = {};
(window.VEHICLES_DATA || []).forEach((v) => { vehicleMap[v.nomor_polisi] = v; });
const BBM_PRICES = window.BBM_PRICES || {};

const inputPlat = document.getElementById("nomor_polisi_input");
const hiddenPlat = document.getElementById("nomor_polisi");
const optionsList = document.getElementById("plat-options");
const selectJenisBbm = document.getElementById("jenis_bbm");
const selectMengetahui = document.getElementById("mengetahui");

function renderPlatOptions(filterText = "") {
  optionsList.innerHTML = "";
  const keyword = filterText.trim().toUpperCase();
  const filtered = vehicleList.filter((plat) => plat.toUpperCase().includes(keyword));

  if (filtered.length === 0) {
    if (keyword) {
      const addItem = document.createElement("div");
      addItem.className = "option-item add-new";
      addItem.textContent = `+ Tambahkan "${filterText.trim().toUpperCase()}" sebagai kendaraan baru`;
      addItem.addEventListener("click", () => addNewVehicle(filterText.trim().toUpperCase()));
      optionsList.appendChild(addItem);
    } else {
      const noResult = document.createElement("div");
      noResult.className = "no-result";
      noResult.textContent = "Tidak ada data kendaraan.";
      optionsList.appendChild(noResult);
    }
  } else {
    filtered.forEach((plat) => {
      const item = document.createElement("div");
      item.className = "option-item";
      item.textContent = plat;
      item.addEventListener("click", () => selectPlat(plat));
      optionsList.appendChild(item);
    });

    if (keyword && !filtered.some((p) => p.toUpperCase() === keyword)) {
      const addItem = document.createElement("div");
      addItem.className = "option-item add-new";
      addItem.textContent = `+ Tambahkan "${filterText.trim().toUpperCase()}" sebagai kendaraan baru`;
      addItem.addEventListener("click", () => addNewVehicle(filterText.trim().toUpperCase()));
      optionsList.appendChild(addItem);
    }
  }
  optionsList.classList.add("open");
}

function selectPlat(plat) {
  inputPlat.value = plat;
  hiddenPlat.value = plat;
  optionsList.classList.remove("open");
  clearFieldError("nomor_polisi");
  autofillFromVehicle(plat);
}

// ---------------------------------------------------------
// Autofill Jenis BBM & Driver berdasarkan Nomor Polisi
// ---------------------------------------------------------
function setSelectValueIfExists(selectEl, value) {
  if (!value) return;
  const hasOption = Array.from(selectEl.options).some((opt) => opt.value === value);
  if (hasOption) {
    selectEl.value = value;
    clearFieldError(selectEl.id);
  }
}

function autofillFromVehicle(plat) {
  const vehicle = vehicleMap[plat];
  if (!vehicle) return;
  setSelectValueIfExists(selectJenisBbm, vehicle.jenis_bbm);
  setSelectValueIfExists(selectMengetahui, vehicle.driver);
  recalcFromPriceChange();
}

async function addNewVehicle(plat) {
  if (!plat) return;
  try {
    const res = await fetch("/api/vehicles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nomor_polisi: plat }),
    });
    const data = await res.json();
    if (data.success) {
      vehicleList.push(plat);
      selectPlat(plat);
      showToast(`Kendaraan ${plat} berhasil ditambahkan.`, "success");
    } else {
      // Kemungkinan sudah terdaftar, tetap pilih platnya
      selectPlat(plat);
      showToast(data.message || "Kendaraan sudah terdaftar, dipilih otomatis.", "info");
    }
  } catch (err) {
    showToast("Gagal menghubungi server untuk menambah kendaraan.", "error");
  }
}

inputPlat.addEventListener("focus", () => renderPlatOptions(inputPlat.value));
inputPlat.addEventListener("input", () => {
  hiddenPlat.value = "";
  renderPlatOptions(inputPlat.value);
});

document.addEventListener("click", (e) => {
  if (!document.getElementById("searchable-plat").contains(e.target)) {
    optionsList.classList.remove("open");
  }
});

// ---------------------------------------------------------
// Format & validasi input angka (Liter & Uang)
// ---------------------------------------------------------
const inputLiter = document.getElementById("jumlah_liter");
const inputUang = document.getElementById("uang");
const inputTerbilang = document.getElementById("terbilang");

// Harga per liter dari jenis BBM yang sedang dipilih (0 jika belum diketahui)
function getHarga() {
  const harga = parseFloat(BBM_PRICES[selectJenisBbm.value]);
  return isNaN(harga) || harga <= 0 ? 0 : harga;
}

// Format ribuan otomatis untuk Uang Sebanyak
function formatRibuan(angka) {
  const numOnly = String(angka).replace(/[^0-9]/g, "");
  if (!numOnly) return "";
  return parseInt(numOnly, 10).toLocaleString("id-ID");
}

function getRawUang() {
  return inputUang.value.replace(/[^0-9]/g, "");
}

function getRawLiter() {
  return inputLiter.value.replace(/[^0-9.]/g, "");
}

let terbilangTimeout = null;
function scheduleTerbilangUpdate() {
  clearTimeout(terbilangTimeout);
  terbilangTimeout = setTimeout(async () => {
    const raw = getRawUang();
    if (!raw) return;
    try {
      const res = await fetch("/api/terbilang", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uang: raw }),
      });
      const data = await res.json();
      if (data.success && data.terbilang) {
        inputTerbilang.value = data.terbilang;
        clearFieldError("terbilang");
      }
    } catch (err) {
      // Jika gagal, biarkan user mengisi manual
    }
  }, 400);
}

// Uang -> Liter, dibulatkan 2 desimal (format 12.23)
function recalcLiterFromUang() {
  const harga = getHarga();
  const raw = getRawUang();
  if (!harga || !raw) return;
  const nominal = parseFloat(raw);
  if (isNaN(nominal)) return;
  const liter = Math.round((nominal / harga) * 100) / 100;
  inputLiter.value = liter.toFixed(2);
  clearFieldError("jumlah_liter");
}

// Liter -> Uang, dibulatkan ke Rupiah penuh (uang tidak berbentuk pecahan)
function recalcUangFromLiter() {
  const harga = getHarga();
  const raw = getRawLiter();
  if (!harga || !raw) return;
  const liter = parseFloat(raw);
  if (isNaN(liter)) return;
  const uang = Math.round(liter * harga);
  inputUang.value = formatRibuan(String(uang));
  clearFieldError("uang");
  scheduleTerbilangUpdate();
}

// Dipanggil saat jenis BBM berubah (manual maupun autofill nomor polisi):
// hitung ulang field yang belum jadi sumber input terakhir.
function recalcFromPriceChange() {
  if (getRawUang()) {
    recalcLiterFromUang();
  } else if (getRawLiter()) {
    recalcUangFromLiter();
  }
}

// Hanya izinkan angka & satu titik desimal pada Jumlah Liter
inputLiter.addEventListener("input", () => {
  let val = inputLiter.value.replace(/[^0-9.]/g, "");
  const parts = val.split(".");
  if (parts.length > 2) {
    val = parts[0] + "." + parts.slice(1).join("");
  }
  inputLiter.value = val;
  clearFieldError("jumlah_liter");
  recalcUangFromLiter();
});

// Format ribuan otomatis untuk Uang Sebanyak + generate liter & terbilang otomatis
inputUang.addEventListener("input", () => {
  const formatted = formatRibuan(inputUang.value);
  inputUang.value = formatted;
  clearFieldError("uang");
  recalcLiterFromUang();
  scheduleTerbilangUpdate();
});

selectJenisBbm.addEventListener("change", () => {
  clearFieldError("jenis_bbm");
  recalcFromPriceChange();
});

// ---------------------------------------------------------
// Validasi Form
// ---------------------------------------------------------
function setFieldError(fieldName) {
  const group = document.querySelector(`[data-field="${fieldName}"]`);
  if (group) group.classList.add("invalid");
}

function clearFieldError(fieldName) {
  const group = document.querySelector(`[data-field="${fieldName}"]`);
  if (group) group.classList.remove("invalid");
}

function validateForm() {
  let valid = true;
  const fields = {
    tanggal_nota: document.getElementById("tanggal_nota").value.trim(),
    nomor_polisi: hiddenPlat.value.trim(),
    jenis_bbm: document.getElementById("jenis_bbm").value.trim(),
    jumlah_liter: inputLiter.value.trim(),
    uang: getRawUang(),
    terbilang: inputTerbilang.value.trim(),
    mengetahui: document.getElementById("mengetahui").value.trim(),
  };

  Object.entries(fields).forEach(([name, value]) => {
    if (!value || (["jumlah_liter", "uang"].includes(name) && isNaN(parseFloat(value)))) {
      setFieldError(name);
      valid = false;
    } else {
      clearFieldError(name);
    }
  });

  return { valid, fields };
}

// ---------------------------------------------------------
// Submit Form -> Generate Nota BBM
// ---------------------------------------------------------
const form = document.getElementById("form-bon-bbm");
const btnGenerate = document.getElementById("btn-generate");
const btnGenerateText = document.getElementById("btn-generate-text");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const { valid, fields } = validateForm();
  if (!valid) {
    showToast("Mohon lengkapi semua field yang wajib diisi.", "error");
    return;
  }

  btnGenerate.disabled = true;
  btnGenerateText.textContent = "Memproses...";

  try {
    const res = await fetch("/api/generate-nota", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(fields),
    });
    const data = await res.json();

    if (data.success) {
      showToast("Nota Bon BBM berhasil dibuat dan disimpan.", "success");
      window.open(data.pdf_url, "_blank");
      form.reset();
      hiddenPlat.value = "";
      inputPlat.value = "";
    } else {
      showToast(data.message || "Gagal menyimpan data.", "error");
    }
  } catch (err) {
    showToast("Terjadi kesalahan koneksi ke server.", "error");
  } finally {
    btnGenerate.disabled = false;
    btnGenerateText.textContent = "Generate Nota BBM";
  }
});

document.getElementById("btn-reset").addEventListener("click", () => {
  form.reset();
  hiddenPlat.value = "";
  inputPlat.value = "";
  document.querySelectorAll(".form-group.invalid").forEach((el) => el.classList.remove("invalid"));
});

// Set tanggal hari ini sebagai default
document.getElementById("tanggal_nota").valueAsDate = new Date();
